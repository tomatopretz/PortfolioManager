from pydantic import BaseModel


class ErrorResultDTO(BaseModel):
    error: str
