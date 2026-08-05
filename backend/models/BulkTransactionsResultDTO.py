from pydantic import BaseModel

from models.TransactionDTO import TransactionDTO


class BulkTransactionsResultDTO(BaseModel):
    count: int
    created: list[TransactionDTO]
