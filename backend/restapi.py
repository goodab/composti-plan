from typing import Annotated, Union, List
from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Field, Session, SQLModel, create_engine, Relationship, select
from contextlib import asynccontextmanager
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import selectinload


class Business(SQLModel, table=True):
    id: Union[int, None] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    phone_number: int = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    disposal_requests: List["DisposalRequest"] = Relationship(back_populates="business")

class Timeslot(SQLModel, table=True):
    id: Union[int, None] = Field(default=None, primary_key=True)
    start_time: datetime = Field(index=True, nullable=False) 
    end_time: datetime = Field(index=True, nullable=False)
    disposal_request_id: Union[int, None] = Field(foreign_key="disposalrequest.id", nullable=True)
    disposal_request: "DisposalRequest" = Relationship(back_populates="timeslots")

class DisposalRequest(SQLModel, table=True):
    id: Union[int, None] = Field(default=None, primary_key=True)
    address: str = Field(index=True, nullable=False) 
    business_id: int = Field(foreign_key="business.id", nullable=False)
    longitude: float
    latitude: float
    business: "Business" = Relationship(back_populates="disposal_requests")  
    
    expected_amt: int = Field(index=True, nullable=False)
    waste_type: str = Field(index=True, nullable=False)
    deadline: datetime = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    timeslots: List["Timeslot"] = Relationship(back_populates="disposal_request")

class BusinessResponse(BaseModel):
    id: int
    name : str
    phone_number : int
    email : str

    class Config:
        from_attributes = True
        validate_by_name = True 

class TimeslotResponse(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True 
        validate_by_name = True

class DisposalRequestResponse(BaseModel):
    id: int
    location: str
    expected_amt: int
    waste_type: str
    deadline: datetime
    created_at: datetime
    business: BusinessResponse 
    timeslots: List[TimeslotResponse]

    class Config:
        from_attributes = True
        validate_by_name = True

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    print("Closing resources...")

app = FastAPI(lifespan=lifespan)


@app.post("/businesses/", status_code=status.HTTP_201_CREATED)
def create_business(business: Business, session: SessionDep) -> Business:
    session.add(business)
    session.commit()
    session.refresh(business)
    return business

@app.post("/disposal/requests/", status_code=status.HTTP_201_CREATED)
def create_disposal_request(disposal_request: DisposalRequest, session: SessionDep) -> DisposalRequest:
    business = session.get(Business, disposal_request.business_id)
    disposal_request.deadline = datetime.fromisoformat(disposal_request.deadline)
    disposal_request.created_at = datetime.fromisoformat(disposal_request.created_at)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with id {disposal_request.business_id} not found"
        )
    session.add(disposal_request)
    session.commit()
    session.refresh(disposal_request)
    return disposal_request

@app.post("/disposal/requests/{request_id}/timeslots", status_code=status.HTTP_201_CREATED)
def create_timeslot(request_id: int, timeslot: Timeslot, session: SessionDep) -> Timeslot:
    disposal_request = session.get(DisposalRequest, request_id)
    
    if not disposal_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disposal request with id {request_id} not found"
        )
    SessionDep
    timeslot.disposal_request_id = request_id
    timeslot.start_time = datetime.fromisoformat(timeslot.start_time)
    timeslot.end_time = datetime.fromisoformat(timeslot.end_time)
    session.add(timeslot)
    session.commit()
    session.refresh(timeslot)

    return timeslot


@app.get("/disposal/requests/")
def read_disposal_requests(session: SessionDep, offset: int = 0):
    disposal_requests = session.exec(select(DisposalRequest).offset(offset)).all()
    return disposal_requests

@app.get("/disposal/requests/{request_id}", response_model=DisposalRequestResponse)
def get_timeslots_for_request(request_id: int, session: SessionDep):
    disposal_request = session.exec(
        select(DisposalRequest).where(DisposalRequest.id == request_id)
        .options(
            selectinload(DisposalRequest.business),
            selectinload(DisposalRequest.timeslots)
        )
    ).first()

    if not disposal_request:
        raise HTTPException(status_code=404, detail="Disposal request not found")

    return disposal_request