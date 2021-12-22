from pydantic import BaseModel


class Rate(BaseModel):
    code1: str
    code2: str
    rate: float
