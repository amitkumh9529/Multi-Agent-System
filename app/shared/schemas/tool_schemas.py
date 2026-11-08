from pydantic import BaseModel

class ToolRead(BaseModel):
    id: int
    name: str
    display_name: str
    description: str | None = None

    class Config:
        from_attributes = True