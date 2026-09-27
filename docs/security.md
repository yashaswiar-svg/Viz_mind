# VizMind Security Documentation

VizMind implements enterprise-grade multi-layer security protections to guarantee multi-tenant user dataset isolation, token integrity, and platform resilience.

---

## 🔒 Security Architecture & Controls

### 1. User Authentication & JWT Tokens
- Password hashing using **Argon2** / **bcrypt** via `passlib`.
- Dual Token Flow:
  - **Access Tokens**: Short-lived (30 min) HS256 JWTs.
  - **Refresh Tokens**: Long-lived (7 days) HS256 JWTs.
- Automatic password complexity validation (min 8 characters, letters & numbers).

### 2. Multi-Tenant Dataset Ownership Isolation
- Every dataset is owned by a specific `user_id` Foreign Key on `datasets.user_id`.
- Access enforcement handled centrally by `verify_dataset_ownership` FastAPI dependency.
- **Strict Fast-Fail**: Attempting to access or alter another user's dataset yields `404 Not Found` (preventing existence enumeration).

### 3. File Access & Storage Security
- File path traversal protection via safe UUID naming scheme and `validate_path_safety()`.
- File uploads sanitized and restricted by extension (`.csv`) and file size limits (100MB max).
- Coordinated User Deletion: Deleting a user account cascades DB deletion and physically purges all raw and preprocessed CSV storage files from `/app/storage`.

### 4. Middleware & Network Security
- **Security Headers Middleware**:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: strict-origin-when-cross-origin`
- **Rate Limiting**: Single-instance in-memory rate limiter protecting endpoints against brute force attacks.
- **Fast-Fail Startup Config Check**: Refuses to launch in production (`APP_ENV=production`) if default `JWT_SECRET_KEY` or `DEBUG=true` is set.
