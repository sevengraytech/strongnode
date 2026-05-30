# TODO — Referral system

- [x] Inspect/implement DB changes in `backend/models/models.py` (referrer relation, referral_earnings ledger, referral codes).
- [x] Ensure schema validation support in `backend/schemas/schemas.py` (referral config + user referral endpoints).
- [x] Add admin settings endpoints in `backend/routers/admin.py` for referral percentage.
- [x] Update deposit approval endpoint in `backend/routers/admin.py` to credit referrer bonus only on first completed deposit.
- [x] Add user endpoints in `backend/routers/referrals.py` to apply referral code (blocked after first deposit).
- [x] Add admin UI for referral settings in `frontend/admin.html`.
- [ ] Update registration frontend (`frontend/register.html`) to accept `?ref=CODE` (or input field) and send to backend during registration.
- [ ] Add minimal frontend UI to show the user their referral code (likely `frontend/dashboard.html` or after register success).
- [ ] Run quick smoke test: register with referral, approve deposit in admin, verify referrer balance + transaction.
- [ ] If needed, extend SQLite migrations in `main.py` for new columns.

