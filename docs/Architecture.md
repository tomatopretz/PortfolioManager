# Architecture

```mermaid
flowchart LR
    Browser["Browser"] --> Frontend["Frontend\nReact"]
    Frontend --> Backend["Backend\nFlask API"]
    Backend --> Yahoo["Yahoo Finance API"]
    Backend --> Firebase["Firebase\nvia SQL Connect"]
```

## Frontend Routes

- `/`
- `/holdings`
- `/transactions`

## Backend Routes

- `/api/portfolio`
- `/api/transactions`
- `/api/prices`
- `/api/performance`

## POST /api/transactions Flow

```mermaid
flowchart TD
    Type{"buy or sell?"}

    Type -->|buy| BuyKind{"stock/bond\nor CASH?"}
    BuyKind -->|CASH| Deposit["credit CASH\nPortfolioItem"]
    BuyKind -->|stock/bond| Buy["1. debit* CASH PortfolioItem\n2. credit stock/bond PortfolioItem"]

    Type -->|sell| SellKind{"stock/bond\nor CASH?"}
    SellKind -->|CASH| Withdraw["debit* CASH\nPortfolioItem"]
    SellKind -->|stock/bond| Sell["1. debit* stock/bond PortfolioItem\n2. credit CASH PortfolioItem"]

    Deposit & Buy & Withdraw & Sell --> Record["record Transaction"]
```

\* debit steps all go through the same check:

```mermaid
flowchart TD
    Cheap{"greedy check:\ntoday's balance\ncovers it?"}
    Cheap -->|no, always reject\neven if backdated| Reject(["reject"])
    Cheap -->|yes| Backdated{"backdated?"}
    Backdated -->|no| Accept(["accept"])
    Backdated -->|yes| Replay["replay full history\nwith this inserted"]
    Replay --> Neg{"any point\nnegative?"}
    Neg -->|yes| Reject
    Neg -->|no| Accept
```

## Work Split

| Person | Area |
|---|---|
| Shuqing | Frontend |
| Yangxian | Backend — Performance API & DB |
| Emmelyn | Backend — all other APIs (portfolio & transactions) |
