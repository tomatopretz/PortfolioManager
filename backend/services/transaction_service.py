from typing import Optional

from models.TransactionDTO import TransactionDTO
from repository.transaction_repository import TransactionRepository


class TransactionService:
    """Business logic for transactions."""

    @staticmethod
    def list_transactions(tickers: Optional[list[str]] = None) -> list[TransactionDTO]:
        """List all recorded transactions, optionally filtered to one or more tickers."""
        if not tickers:
            return TransactionRepository.list_all()
        return TransactionRepository.list_by_tickers(tickers)

    @staticmethod
    def add_transaction(transaction: TransactionDTO) -> TransactionDTO:
        """Create a new transaction record."""
        return TransactionRepository.add(transaction)

    @staticmethod
    def delete_transaction(transaction_id: str) -> bool:
        """Delete a transaction record. Returns False if no transaction with that id exists."""
        return TransactionRepository.delete(transaction_id)
