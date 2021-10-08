from pydantic import BaseModel


class Rate(BaseModel):
    code: str
    rate: float


class CurrencyStatus(BaseModel):
    code: str
    is_subscribed: bool
