# CryptoVault — Crypto Investment Platform

A full-stack, production-quality crypto investment platform built with **FastAPI** (backend) and **Vanilla HTML/CSS/JS + Axios** (frontend).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.10+ |
| Database | SQLite via SQLAlchemy ORM |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Frontend | HTML5, CSS3, Vanilla JS, Axios |
| Charts | TradingView Lightweight Charts v4 |
| Live Prices | CoinGecko Public API (with mock fallback) |
| Server | Uvicorn (ASGI) |

---

## Project Structure

```
cryptovault/
├── main.py                        # FastAPI app entry point + startup seeding
├── requirements.txt
├── README.md
├── cryptovault.db                 # SQLite database (auto-created on first run)
│
├── backend/
│   ├── core/
│   │   ├── config.py              # Settings (SECRET_KEY, JWT config)
│   │   ├── database.py            # SQLAlchemy engine + session + get_db
│   │   └── security.py            # JWT creation, bcrypt, get_current_user
│   │
│   ├── models/
│   │   └── models.py              # SQLAlchemy models: User, Transaction,
│   │                              #   Investment, InvestmentPlan, ProfitLog, LoanRequest
│   │
│   ├── schemas/
│   │   └── schemas.py             # Pydantic v2 request/response schemas
│   │
│   └── routers/
│       ├── auth.py                # POST /auth/register, /auth/login
│       ├── user.py                # GET /user/me, /user/overview, POST deposit/withdraw
│       ├── transactions.py        # GET /transactions (paginated + filterable)
│       ├── investments.py         # Plans, invest, my-investments, claim, accrue
│       ├── profits.py             # GET /profits (profit log)
│       └── loans.py               # POST request/repay, GET my loans
│
└── frontend/
    ├── index.html                 # Landing page (hero, charts, plans, how-it-works, payouts, SEC)
    ├── login.html                 # JWT login form
    ├── register.html              # Registration form
    ├── dashboard.html             # Full dashboard SPA (all 10 sections)
    └── whitepaper.pdf             # Replace with your actual whitepaper
```

---

## Quick Start

### 1. Clone & enter project

```bash
cd cryptovault
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Open in browser

- **Landing Page:** http://localhost:8000
- **Register:** http://localhost:8000/register
- **Login:** http://localhost:8000/login
- **Dashboard:** http://localhost:8000/dashboard
- **API Docs:** http://localhost:8000/docs (Swagger UI)

---

## API Endpoints

### Authentication (`/auth`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, returns JWT token |

### User (`/user`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/user/me` | Get current user profile |
| GET | `/user/overview` | Dashboard overview stats |
| POST | `/user/deposit` | Deposit funds |
| POST | `/user/withdraw` | Request withdrawal |

### Investments (`/investments`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/investments/plans` | List all active plans |
| POST | `/investments/invest` | Create new investment |
| GET | `/investments/my` | List user's investments |
| POST | `/investments/claim` | Claim matured investment principal |
| POST | `/investments/accrue-profits` | Trigger profit accrual (demo) |

### Transactions (`/transactions`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/transactions?page=1&per_page=10&type_filter=deposit` | Paginated transaction history |

### Profits (`/profits`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/profits?limit=50` | Profit log |

### Loans (`/loans`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/loans/request` | Request credit advance |
| GET | `/loans/my` | List user's loans |
| POST | `/loans/repay` | Repay a loan |

---

## Investment Plans (Auto-Seeded)

| Plan | Daily ROI | Min | Max | Duration |
|------|-----------|-----|-----|----------|
| Starter | 0.8%/day | $50 | $999 | 30 days |
| Growth | 1.5%/day | $1,000 | $4,999 | 60 days |
| Premium | 2.2%/day | $5,000 | $24,999 | 90 days |
| Elite | 3.0%/day | $25,000 | $1,000,000 | 120 days |

---

## Dashboard Sections

1. **Overview** — Balance, invested, profit, active investments, live charts, accrue profits, wallet
2. **Add Funds** — Deposit form with wallet display and crypto type selector
3. **Withdraw** — Withdrawal request with balance check
4. **Credit Advance** — Loan request (up to 50% of invested, 5% flat interest)
5. **Claim Back** — Claim principal from matured investments
6. **Investment Plans** — Browse and invest in available plans
7. **My Investments** — Progress bars, ROI, status for all investments
8. **Profit History** — Daily profit log with source and amount
9. **Transactions** — Full paginated, filterable transaction history
10. **My Loans** — Loan status and repayment

---

## Key Implementation Notes

- **Passwords** are hashed with `bcrypt` via `passlib`
- **JWT tokens** expire after 24 hours (configurable in `config.py`)
- **Profit Accrual** is triggered manually via the dashboard button (or automatically call `POST /investments/accrue-profits` from a cron/scheduler in production)
- **Deposits** are credited instantly (in production, integrate a blockchain listener)
- **Withdrawals** are marked `pending` (in production, integrate a payment processor)
- **Loans** are auto-approved for demo; add an admin review step in production
- **CORS** is configured to allow all origins for local dev; restrict in production

---

## Customization

### Change JWT secret
Edit `backend/core/config.py`:
```python
SECRET_KEY: str = "your-super-secure-secret-here"
```

### Change database
Edit `backend/core/database.py` to use PostgreSQL:
```python
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/cryptovault"
```
(Remove the `connect_args` parameter for PostgreSQL)

### Production deployment
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## License
MIT — For demonstration and educational purposes.
