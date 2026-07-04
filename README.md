# rent-flatmate-finder
A platform where room owners can list their rooms and tenants can create profiles with their budget and preferred location. The app calculates a compatibility score between tenants and listings so people can find better matches faster, and lets them chat and get notified once there's mutual interest.

## Features
- Owner and tenant signup/login with JWT-based authentication
- Role-based access (owner, tenant, admin)
- Owners can post, browse, and mark room listings as filled
- Tenants can create a profile (preferred location, budget range) and browse listings
- AI-powered compatibility scoring using the Claude API, with a rule-based fallback if the LLM is unavailable or not configured
- Tenants can express interest in a listing; owners can accept or decline
- Email notifications: owner gets notified when a high-compatibility tenant (score > 80) expresses interest, and tenant gets notified when their interest is accepted/declined

## Tech Stack
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (hosted on Neon), SQLAlchemy ORM
- **Auth:** JWT tokens, bcrypt password hashing
- **AI:** Anthropic Claude API for compatibility scoring
- **Email:** SMTP via Gmail

## Setup Instructions
1. Clone the repo and go into the backend folder:
cd backend
2. Create and activate a virtual environment:
python -m venv venv
venv\Scripts\activate
3. Install dependencies:
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose passlib bcrypt python-multipart pydantic-settings anthropic python-dotenv email-validator
4. Copy `.env.example` to `.env` and fill in your own database URL, secret key, Anthropic API key, and SMTP credentials.
5. Create the database tables:
python create_tables.py
6. Run the server:
uvicorn app.main:app --reload
7. Visit `http://127.0.0.1:8000/docs` for the interactive API docs.

## Compatibility Scoring Design
Each tenant-listing pair gets a score from 0-100 based on budget fit (50%) and location match (50%). The score is calculated once and stored in the database, not recomputed on every request. If the Claude API call fails, is not configured, or returns an unexpected response, the system automatically falls back to a rule-based scorer that applies the same budget/location logic directly in Python. This was tested and works in both modes.

## 
While building this, I hit and fixed a few real bugs along the way, like a passlib/bcrypt version incompatibility that was breaking password hashing, and a variable name typo that was silently breaking the location filter on listings. Both are fixed and tested.
