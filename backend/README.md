# Portfolio Manager Backend

Flask-based REST API for portfolio management.

## Setup

### macOS / Linux (bash/zsh)

```bash
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
brew install --cask google-cloud-sdk
brew install cloud-sql-proxy
gcloud auth login
gcloud auth application-default login
cp .env.example .env
```

### Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
winget install --id Google.CloudSDK
Invoke-WebRequest -Uri "https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v<VERSION>/cloud-sql-proxy.x64.exe" -OutFile "cloud-sql-proxy.exe"
gcloud auth login
gcloud auth application-default login
Copy-Item .env.example .env
```

Replace `<VERSION>` with the latest release tag from the [cloud-sql-proxy releases page](https://github.com/GoogleCloudPlatform/cloud-sql-proxy/releases). There's no winget/choco package for `cloud-sql-proxy`, so either keep the downloaded `.exe` on your `PATH` or run it with `.\cloud-sql-proxy.exe` from wherever you saved it.

If `Activate.ps1` is blocked by your execution policy, run this once per machine:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Set `DATABASE_URL` in `.env`:

```env
DATABASE_URL=postgresql://USER:PASSWORD@127.0.0.1:5433/portfoliomanager-bfaa2-database
```

Use the shared database username and password provided separately. Do not commit `.env`.

Start the Cloud SQL proxy in a separate terminal:

```bash
cloud-sql-proxy pretap-bfaa2:asia-southeast1:portfoliomanager-bfaa2-instance --port 5433
```

```powershell
cloud-sql-proxy pretap-bfaa2:asia-southeast1:portfoliomanager-bfaa2-instance --port 5433
```

Run the backend:

```bash
python app.py
```

```powershell
python app.py
```

The API will be available at `http://localhost:5000`

## Available Endpoints

- `GET /health` - Health check
- `GET /api/portfolio` - Retrieve portfolio (not implemented)
- `GET /api/portfolio/items` - List portfolio items (not implemented)

## Project Structure

```
backend/
├── app.py                  # Flask application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── models/               # Data models
├── routes/               # API route handlers
├── services/             # Business logic services
├── utils/                # Utility functions
└── tests/                # Test files
```

## Next Steps

- Set up Firebase SQL Connect/PostgreSQL integration (Step 2)
- Implement portfolio and item models (Step 3)
- Create database service layer (Step 4)
- Implement GET endpoints (Step 5)
