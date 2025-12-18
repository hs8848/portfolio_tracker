from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)
    name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)


class Token (BaseModel):
    access_token: str
    token_type: str = 'bearer'


class InstrumentCreate(BaseModel):
    name: str
    type: str
    isin: str
    ext_id_01: Optional[str]
    ext_id_01_type: Optional[str]
    amc: Optional[str]
    mf_class: Optional[str]
    issuer: Optional[str]


class InstrumentResponse(BaseModel):
    id: int
    name: str
    type: str
    isin: str


class HoldingCreate(BaseModel):
    instrument_id: int
    quantity: float
    avg_cost_price: float

class HoldingResponse(BaseModel):
    id: int
    instrument_id: int
    instrument_name: str
    quantity: float
    avg_cost_price: float