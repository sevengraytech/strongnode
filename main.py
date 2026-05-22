from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.core.database import engine, SessionLocal, Base
from backend.models import models
from backend.routers import auth, user, transactions, investments, profits, loans, admin, claimback, password_reset, chatbot

import os
import random
import string
from datetime import datetime



Base.metadata.create_all(bind=engine)

# ── Auto-migrate: add any columns the model defines that the DB doesn't yet have ──
def _run_migrations():
    """
    SQLite doesn't support ALTER TABLE ... ADD COLUMN IF NOT EXISTS, so we inspect
    the live schema and add any columns that the ORM model defines but the DB lacks.
    This is safe to run on every startup — it skips columns that already exist.
    """
    import sqlite3 as _sqlite3
    db_path = engine.url.database  # e.g. "./cryptovault.db"
    conn = _sqlite3.connect(db_path)
    cur = conn.cursor()

    # Map of table → list of (column_name, column_definition)
    # NOTE: SQLite does NOT support ALTER TABLE ... ADD COLUMN with UNIQUE.
    # Uniqueness of activation_token is enforced at the application level (secrets.token_urlsafe).
    migrations = {
        "users": [
            ("registration_completed",      "BOOLEAN NOT NULL DEFAULT 0"),
            ("activation_token",            "VARCHAR"),   # unique enforced in app, not DB
            ("activation_token_expires_at", "DATETIME"),
        ],
    }

    for table, columns in migrations.items():
        cur.execute(f"PRAGMA table_info({table})")
        existing = {row[1] for row in cur.fetchall()}
        for col_name, col_def in columns:
            if col_name not in existing:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
                print(f"✅ Migration: added {table}.{col_name}")

    conn.commit()
    conn.close()

_run_migrations()

app = FastAPI(title="StrongNodeCapital API", version="2.0.0", docs_url="/docs")

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # Extract simple error messages to avoid ValueError serialization issues
    details = []
    for error in exc.errors():
        detail = {
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": str(error["msg"])
        }
        details.append(detail)
    
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation failed",
            "details": details,
            "message": "Please check your input data and try again."
        }
    )

app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(transactions.router)
app.include_router(investments.router)
app.include_router(profits.router)
app.include_router(loans.router)
app.include_router(admin.router)
app.include_router(claimback.router)
app.include_router(password_reset.router)
app.include_router(chatbot.router)


frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
uploads_dir = os.path.join(frontend_dir, "uploads")
os.makedirs(uploads_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/health")
def health_check():
    """Docker healthcheck endpoint."""
    return {"status": "ok", "app": "StrongNode Capitals"}

@app.get("/")
def read_root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/dashboard")
def read_dashboard():
    return FileResponse(os.path.join(frontend_dir, "dashboard.html"))

@app.get("/login")
def read_login():
    return FileResponse(os.path.join(frontend_dir, "login.html"))

@app.get("/reset-password")
def read_reset_password():
    return FileResponse(os.path.join(frontend_dir, "reset_password.html"))

@app.get("/activate")
def read_activate():
    return FileResponse(os.path.join(frontend_dir, "activate.html"))

@app.get("/register")
def read_register():
    return FileResponse(os.path.join(frontend_dir, "register.html"))


@app.get("/admin-panel")
def read_admin():
    return FileResponse(os.path.join(frontend_dir, "admin.html"))

@app.on_event("startup")
def validate_production_config():
    """Fail loudly on startup if required production settings are missing."""
    from backend.core.config import settings
    import logging
    _log = logging.getLogger("startup")

    errors = []
    if not settings.SMTP_PASS:
        errors.append("SMTP_PASS is not set. Email delivery will not work.")
    if not settings.SMTP_USER:
        errors.append("SMTP_USER is not set. Email delivery will not work.")
    if settings.SECRET_KEY in (
        "cryptovault-super-secret-key-change-in-production-2024",
        "change-this-to-a-long-random-secret-in-production",
        "",
    ):
        errors.append("SECRET_KEY is using the default insecure value. Set a strong random secret.")

    if errors:
        for e in errors:
            _log.critical(f"[CONFIG ERROR] {e}")
        raise RuntimeError(
            "Application cannot start: production configuration is incomplete.\n"
            + "\n".join(f"  - {e}" for e in errors)
        )
    _log.info("Production config validated OK.")


@app.on_event("startup")
def seed_data():
    from backend.models.models import InvestmentPlan, User, PromoCode
    from backend.core.security import get_password_hash
    db = SessionLocal()
    try:
        # Seed investment plans
        if db.query(InvestmentPlan).count() == 0:
            db.add_all([
                InvestmentPlan(name="Starter", daily_roi=0.8, min_amount=50, max_amount=999,
                               duration_days=30, description="Perfect for new investors. Low risk, steady returns."),
                InvestmentPlan(name="Growth", daily_roi=1.5, min_amount=1000, max_amount=4999,
                               duration_days=60, description="Accelerated growth for intermediate investors."),
                InvestmentPlan(name="Premium", daily_roi=2.2, min_amount=5000, max_amount=24999,
                               duration_days=90, description="High-yield plan with maximum ROI potential."),
                InvestmentPlan(name="Elite", daily_roi=3.0, min_amount=25000, max_amount=1000000,
                               duration_days=120, description="Institutional-grade returns for serious investors."),
            ])
            print("✅ Investment plans seeded.")

        # Seed default admin account (force verification + login capability)
        # This ensures the admin can always log in even if the DB already has a partial/old record.
        import secrets as sec
        rand_digits = ''.join(str(sec.randbelow(10)) for _ in range(10))
        admin_mobile = "+" + rand_digits

        admin_user = db.query(User).filter(User.email == "strongnodecapital@mailfence.com").first()
        if not admin_user:
            admin_user = User(
                email="strongnodecapital@mailfence.com",
                full_name="Platform Admin",
                mobile=admin_mobile,
                country="N/A",
                address="N/A",
                city="N/A",
                state="N/A",
                date_of_birth="1970-01-01",
                hashed_password=get_password_hash("admin123"),
                wallet_address="0x" + sec.token_hex(20),
                is_admin=True,
                is_active=True,
                email_verified=True,
                kyc_status="approved",
                bonus_credited=True,
            )
            db.add(admin_user)

        # Force admin flags and password on every startup
        admin_user.is_admin = True
        admin_user.is_active = True
        admin_user.email_verified = True
        
        admin_user.kyc_status = "approved"
        admin_user.bonus_credited = True
        admin_user.hashed_password = get_password_hash("admin123")

        # Ensure required profile fields exist
        admin_user.full_name = admin_user.full_name or "Platform Admin"
        admin_user.mobile = admin_user.mobile or admin_mobile
        admin_user.country = admin_user.country or "N/A"
        admin_user.address = admin_user.address or "N/A"
        admin_user.city = admin_user.city or "N/A"
        admin_user.state = admin_user.state or "N/A"
        admin_user.wallet_address = admin_user.wallet_address or ("0x" + sec.token_hex(20))

        db.commit()
        print("✅ Admin ensured & forced login: strongnodecapital@mailfence.com / admin123")

        # Mark sweetmail@gmail.com as admin (only if the user already exists)
        sweet_user = db.query(User).filter(User.email == "sweetmail@gmail.com").first()
        if sweet_user and not sweet_user.is_admin:
            sweet_user.is_admin = True
            sweet_user.is_active = True
            print("✅ Updated admin role for: sweetmail@gmail.com")


        # Seed default promo codes
        if db.query(PromoCode).count() == 0:
            db.add_all([
                PromoCode(code="WELCOME100", bonus_amount=100.0, max_uses=500,
                          description="Standard promo — $100 welcome bonus"),
                PromoCode(code="VIP200", bonus_amount=200.0, max_uses=50,
                          description="VIP promo — $200 welcome bonus"),
                PromoCode(code="LAUNCH50", bonus_amount=150.0, max_uses=200,
                          description="Launch special — $150 bonus"),
            ])
            print("✅ Promo codes seeded: WELCOME100, VIP200, LAUNCH50")

        db.commit()
    finally:
        db.close()
