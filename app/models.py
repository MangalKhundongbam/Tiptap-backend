from pydantic import BaseModel # type: ignore

class Item(BaseModel):
    name: str
    price: float

class HTMLData(BaseModel):
    html: str