# ER Diagram

```mermaid
erDiagram
    PORTFOLIO_ITEM ||--o{ TRANSACTION : "has"

    PORTFOLIO_ITEM {
        string id PK
        string ticker
        string assetType
        float quantity
        float costBasis
        boolean isFavourite
        timestamp lastUpdated
    }

    TRANSACTION {
        string id PK
        string portfolioItemId FK
        string type
        float quantity
        float price
        timestamp date
        boolean useCash
    }
```

`PortfolioItem` has its own `id`.

`Transaction` has its own `id` and stores a foreign key to `PortfolioItem.id`.

The unique constraint for `PortfolioItem` is composite: `(ticker, assetType)` must be unique together.

