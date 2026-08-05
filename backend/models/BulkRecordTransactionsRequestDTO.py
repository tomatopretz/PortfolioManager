from pydantic import BaseModel, Field

from models.RecordTransactionRequestDTO import RecordTransactionRequestDTO


class BulkRecordTransactionsRequestDTO(BaseModel):
    """Body for POST /api/transactions/bulk."""
    transactions: list[RecordTransactionRequestDTO] = Field(min_length=1, max_length=500)
