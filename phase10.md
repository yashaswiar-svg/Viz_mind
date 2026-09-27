# VIZMIND — PHASE 10

# PRODUCTIONIZATION, SECURITY, DEPLOYMENT & FINAL INTEGRATION

You are working on the existing VizMind project.

VizMind is an AI-powered data analysis platform whose completed pipeline is:

```text
Phase 1 → Project Foundation
Phase 2 → Dataset Ingestion
Phase 3 → Data Profiling & Quality
Phase 4 → Automated Preprocessing
Phase 5 → Smart Visualization Intelligence
Phase 6 → Pattern Discovery
Phase 7 → Anomaly Detection + Prediction
Phase 8 → AI Insight Engine
Phase 9 → Natural-Language Data Analyst
Phase 10 → Productionization, Security, Deployment & Final Integration
```

The Phase 9 walkthrough confirms:

```text
Backend:
94 PASSED
29 SKIPPED
0 FAILED

Alembic:
009_add_phase9_analyst_tables = HEAD

Frontend:
npm run build = PASS
```

Phase 1–9 functionality is already implemented.

Your job now is to implement **ONLY Phase 10**.

---

# 1. PRIMARY OBJECTIVE

Transform the current VizMind application from a development/hackathon-ready application into a **production-ready deployable system**.

Phase 10 must focus on:

```text
Security
Production Configuration
Authentication
Authorization
Dockerization
Production PostgreSQL
Deployment Configuration
API Hardening
Observability
Health Monitoring
Logging
Error Handling
Backup/Recovery
CI/CD
Frontend Production Configuration
Backend Production Configuration
Final Integration
Performance Hardening
Production Documentation
```

The final architecture should be deployable using containers and suitable for a real hosted environment.

---

# 2. MOST IMPORTANT RULE

DO NOT modify or redesign the analytical architecture from Phases 1–9 unless a production issue requires a minimal compatibility change.

Do NOT create:

* Phase 11
* new analytics engines
* new ML algorithms
* new visualization algorithms
* new pattern algorithms
* new anomaly algorithms
* new prediction algorithms
* new insight algorithms
* new natural-language analyst features

Phase 10 is a **productionization phase**, not another feature-development phase.

---

# 3. BEFORE WRITING CODE

First inspect the entire existing repository.

Inspect at minimum:

```text
backend/
frontend/
docker/
alembic/
tests/
docs/
.env*
docker-compose*
requirements*
package.json
README*
```

Inspect:

* current configuration
* database configuration
* Alembic configuration
* FastAPI application
* routers
* middleware
* logging
* CORS
* exception handling
* file storage
* dataset lifecycle
* LLM provider configuration
* Phase 8 provider system
* Phase 9 analyst
* frontend API configuration
* existing tests
* existing Docker configuration if any

Do not assume filenames or architecture.

Reuse existing abstractions.

Do not duplicate services that already exist.

---

# 4. PRODUCTION ARCHITECTURE

Target architecture:

```text
                    INTERNET
                       │
                       ▼
                ┌───────────────┐
                │ Reverse Proxy │
                │ HTTPS / TLS   │
                └───────┬───────┘
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
       ┌───────────┐        ┌──────────────┐
       │ Frontend  │        │ FastAPI API  │
       │ React     │        │ Backend      │
       └───────────┘        └──────┬───────┘
                                   │
                     ┌─────────────┼─────────────┐
                     │             │             │
                     ▼             ▼             ▼
                PostgreSQL      File Storage   LLM APIs
                Production      Dataset Files  Optional
```

Optional components may be introduced only if actually required.

Do NOT introduce Kubernetes, Redis, Celery, Kafka, or microservices merely for architectural complexity.

The production deployment should remain understandable and maintainable.

---

# 5. PRODUCTION ENVIRONMENT MODEL

Support at least:

```text
development
test
production
```

Configuration must be environment-driven.

Never hard-code:

* passwords
* API keys
* JWT secrets
* database credentials
* production URLs
* cloud credentials
* encryption keys

---

# 6. CONFIGURATION MANAGEMENT

Review:

```text
backend/app/core/config.py
```

Create a clean production configuration strategy.

Use environment variables.

Recommended variables:

```text
APP_ENV
APP_VERSION
DEBUG
LOG_LEVEL

DATABASE_URL
DATABASE_TEST_URL

CORS_ORIGINS

SECRET_KEY
JWT_SECRET_KEY
JWT_ACCESS_TOKEN_EXPIRE_MINUTES

STORAGE_PATH
MAX_UPLOAD_SIZE_MB

LLM_ENABLED
LLM_PROVIDER
LLM_MODEL

GEMINI_API_KEY
OPENAI_API_KEY

FRONTEND_URL

RATE_LIMIT_ENABLED
RATE_LIMIT_REQUESTS
RATE_LIMIT_WINDOW_SECONDS

SENTRY_DSN
```

Only add variables that are actually used.

Do not create configuration values that are never consumed.

---

# 7. ENVIRONMENT VALIDATION

Production startup must fail fast if required configuration is missing.

Example:

```text
production + missing DATABASE_URL
→ startup failure

production + insecure/default SECRET_KEY
→ startup failure

production + DEBUG=true
→ startup failure or explicit warning according to policy
```

Development may use safer defaults.

Test environment must remain isolated from production.

---

# 8. SECRETS

Never commit:

```text
.env
.env.production
API keys
database passwords
JWT secrets
private certificates
cloud credentials
```

Update:

```text
.gitignore
```

Add:

```text
.env
.env.*
!.env.example
```

Create:

```text
.env.example
```

with placeholder values only.

Example:

```text
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/vizmind
SECRET_KEY=replace-with-secure-random-value
JWT_SECRET_KEY=replace-with-secure-random-value
GEMINI_API_KEY=
OPENAI_API_KEY=
```

Never place real credentials in `.env.example`.

---

# 9. AUTHENTICATION

Implement production authentication.

Use a standard JWT-based authentication system unless the existing project already contains another secure authentication architecture.

Create appropriate modules, for example:

```text
backend/app/services/auth/
backend/app/api/routes/auth.py
backend/app/schemas/auth.py
```

Potential endpoints:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
POST /api/v1/auth/refresh
```

Do not add unnecessary authentication complexity.

---

# 10. PASSWORD SECURITY

Passwords must NEVER be stored as plaintext.

Use a secure password hashing algorithm such as:

```text
Argon2
```

or an existing secure password hashing library already present in the project.

Requirements:

```text
plaintext password
       ↓
secure password hash
       ↓
database
```

Authentication must compare hashes securely.

---

# 11. USER MODEL

Introduce a minimal production User model if no equivalent exists.

Fields:

```text
id
email
password_hash
full_name
is_active
is_verified
created_at
updated_at
```

Email must be unique.

Do not store plaintext passwords.

Add indexes where useful.

Migration should follow the existing Alembic sequence.

Expected migration:

```text
010_add_production_authentication.py
```

Do not assume this exact filename if repository state differs; inspect first.

---

# 12. AUTHORIZATION

Every dataset must belong to a user.

Current relationship:

```text
User
  ↓
Dataset
  ↓
Profile
  ↓
Processed Dataset
  ↓
Visualizations
  ↓
Patterns
  ↓
Anomalies
  ↓
Predictions
  ↓
Insights
  ↓
Analyst Conversations
```

Add ownership safely.

A user must NEVER be able to access another user's:

* dataset
* profile
* processed dataset
* visualization
* pattern
* anomaly
* prediction
* insight
* conversation
* uploaded file

This is one of the most important Phase 10 requirements.

---

# 13. MULTI-TENANT DATA ISOLATION

Every dataset-related API must enforce ownership.

For example:

```text
GET /datasets/{dataset_id}
```

must verify:

```text
dataset.user_id == authenticated_user.id
```

Otherwise return:

```text
404
```

Prefer not to reveal whether another user's dataset exists.

Apply ownership checks to ALL Phase 1–9 routes.

Audit:

```text
datasets
profiles
preprocessing
visualizations
patterns
anomalies
predictions
insights
analyst conversations
files
```

---

# 14. OWNERSHIP PROPAGATION

Review existing models.

Where appropriate, use:

```text
Dataset.user_id
```

as the ownership root.

Do NOT unnecessarily add user_id to every analytical table if relationships already safely derive ownership from Dataset.

However, verify every query path eventually checks dataset ownership.

Do not rely solely on frontend filtering.

Authorization must be enforced server-side.

---

# 15. AUTHENTICATED API DEPENDENCY

Create a reusable dependency such as:

```text
get_current_user()
```

Use it for protected endpoints.

Example:

```text
current_user
      ↓
dataset ownership check
      ↓
operation
```

Never trust:

```text
user_id
```

provided by the client.

The authenticated identity must come from the validated token.

---

# 16. AUTHENTICATION SECURITY

Implement:

* short-lived access tokens
* secure refresh strategy if refresh tokens are implemented
* token expiration
* invalid-token handling
* inactive-user rejection
* password hashing
* secure secret configuration

Do not log tokens.

Do not return password hashes.

Do not include secrets in API responses.

---

# 17. RATE LIMITING

Introduce basic API rate limiting.

At minimum protect:

```text
login
register
dataset upload
profile
preprocess
visualization generation
pattern discovery
anomaly detection
prediction
insights
analyst messages
```

Do not allow unrestricted repeated expensive operations.

Use a simple production-compatible strategy.

Do NOT introduce Redis solely for rate limiting unless actually necessary.

For a single-instance deployment, an in-memory limiter may be acceptable but must be clearly documented as instance-local.

If using a distributed deployment, use an appropriate shared mechanism.

---

# 18. FILE UPLOAD HARDENING

Review Phase 2 upload handling.

Production must enforce:

```text
extension validation
MIME/content validation
maximum size
empty file rejection
path traversal protection
safe generated filenames
storage isolation
checksum verification
```

Never use user-provided filenames as filesystem paths.

Never expose:

```text
/storage/...
/home/...
/var/...
```

to the client.

---

# 19. FILE STORAGE SECURITY

Dataset files must not be directly publicly accessible.

Do NOT expose:

```text
/storage/datasets/
```

through the web server.

Downloads must pass through authenticated API endpoints.

The API must verify:

```text
authenticated user
↓
dataset ownership
↓
file existence
↓
safe file access
```

---

# 20. DATA PRIVACY

Production logs must never contain:

* raw dataset rows
* entire CSV content
* API keys
* passwords
* access tokens
* filesystem secrets
* complete LLM prompts if they contain sensitive data

Continue the Phase 9 principle:

> Dataset content is untrusted data.

---

# 21. CORS

Production CORS must NOT use:

```text
*
```

unless explicitly justified.

Configure:

```text
CORS_ORIGINS
```

from environment.

Allow only the deployed frontend origin(s).

Review:

```text
allow_credentials
allow_methods
allow_headers
```

and use the minimum required configuration.

---

# 22. SECURITY HEADERS

Add production security headers where appropriate.

Examples:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy
```

Do not blindly add incompatible headers.

Document the chosen policy.

---

# 23. API HARDENING

Review every FastAPI endpoint.

Ensure:

* request validation
* response validation
* authentication
* authorization
* consistent errors
* no stack traces in production
* no internal filesystem paths
* no SQL details
* no secrets
* reasonable request sizes

---

# 24. ERROR HANDLING

Production errors should return structured responses.

Example:

```json
{
  "error": {
    "code": "DATASET_NOT_FOUND",
    "message": "Dataset not found."
  },
  "request_id": "..."
}
```

Do not expose:

```text
Traceback
SQLAlchemy error details
database hostname
filesystem path
Python source code
```

in production responses.

---

# 25. REQUEST ID

Every request should have a request ID.

If provided:

```text
X-Request-ID
```

validate/sanitize it.

Otherwise generate one.

Include it in:

* logs
* errors
* responses where appropriate

Example:

```text
request_id=abc123
```

---

# 26. STRUCTURED LOGGING

Production logs should be structured.

Include:

```text
timestamp
level
request_id
user_id where safe
dataset_id where safe
route
method
status_code
duration_ms
event
```

Never log:

```text
password
token
API key
raw CSV data
full LLM prompt containing sensitive data
```

---

# 27. LOG LEVELS

Development:

```text
DEBUG
```

Production:

```text
INFO
```

or configurable through:

```text
LOG_LEVEL
```

Do not leave noisy debug logging enabled in production by default.

---

# 28. HEALTH ENDPOINTS

Preserve:

```text
GET /api/v1/health
GET /api/v1/health/db
```

Enhance carefully.

Recommended:

```text
GET /api/v1/health
```

should indicate application availability.

Example:

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

Database health:

```text
GET /api/v1/health/db
```

must verify database connectivity.

Do not expose:

* database URL
* credentials
* internal host information

---

# 29. READINESS AND LIVENESS

If useful for deployment, add:

```text
GET /api/v1/health/live
GET /api/v1/health/ready
```

Liveness:

```text
application process is alive
```

Readiness:

```text
application can serve requests
database available
required configuration valid
```

Do not make liveness depend on PostgreSQL.

---

# 30. DATABASE PRODUCTIONIZATION

Review PostgreSQL usage.

Ensure:

* async SQLAlchemy remains supported
* connection pooling configured
* pool size configurable
* pool timeout configured
* connection recycling configured if appropriate
* migrations are applied before application readiness

Example configuration:

```text
DB_POOL_SIZE
DB_MAX_OVERFLOW
DB_POOL_TIMEOUT
DB_POOL_RECYCLE
```

Only add settings actually consumed.

---

# 31. DATABASE MIGRATIONS

Production startup must NOT blindly run:

```text
alembic upgrade head
```

inside every application process if multiple replicas may start simultaneously.

Prefer a dedicated migration step:

```text
deployment
   ↓
migration job
   ↓
application startup
```

Document the workflow.

---

# 32. DATABASE BACKUPS

Define a production PostgreSQL backup strategy.

At minimum document:

```text
daily backup
retention policy
restore procedure
```

Do not claim automated cloud backups unless actually configured.

Create documentation for:

```text
backup
restore
migration recovery
```

---

# 33. DATASET BACKUP STRATEGY

Database backups alone do NOT protect uploaded dataset files.

Document backup strategy for:

```text
PostgreSQL
+
dataset storage
```

The system should clearly state that restoring the database without dataset files may produce incomplete recovery.

---

# 34. DOCKER BACKEND

Create or improve:

```text
backend/Dockerfile
```

Requirements:

* production Python base image
* non-root user
* minimal dependencies
* no development server
* no unnecessary packages
* predictable working directory
* environment-based configuration
* healthcheck where appropriate

Use:

```text
uvicorn
```

or a production-compatible ASGI process configuration.

Do not use:

```text
--reload
```

in production.

---

# 35. DOCKER FRONTEND

Create:

```text
frontend/Dockerfile
```

Use multi-stage build:

```text
Node
 ↓
npm install
 ↓
npm run build
 ↓
minimal web server image
```

The final image should contain only production assets and required web-server files.

---

# 36. FRONTEND ENVIRONMENT

Do not hard-code:

```text
http://localhost:8000
```

in production code.

Use a configurable frontend API base URL.

For example:

```text
VITE_API_BASE_URL
```

Ensure:

```text
development
test
production
```

can use different API URLs.

---

# 37. DOCKER COMPOSE

Create or update:

```text
docker-compose.yml
```

or an appropriately named production compose file.

Recommended services:

```text
frontend
backend
postgres
reverse-proxy
```

Only add reverse proxy if needed.

The compose configuration must define:

* environment
* volumes
* health checks
* dependency conditions
* networking
* persistent PostgreSQL storage
* persistent dataset storage

Do not use ephemeral storage for production PostgreSQL.

---

# 38. PERSISTENT STORAGE

PostgreSQL:

```text
named volume
```

Dataset files:

```text
persistent volume
```

Never assume container filesystem persistence.

---

# 39. REVERSE PROXY

If implementing Nginx or another reverse proxy:

Responsibilities:

```text
HTTPS termination
frontend routing
API routing
request size limits
security headers
compression where appropriate
```

Do not duplicate business logic in the proxy.

---

# 40. HTTPS

Production documentation must require HTTPS.

Never transmit:

```text
JWT
password
dataset data
```

over plain HTTP in production.

Local development may use HTTP.

Do not pretend TLS is configured if certificates are not actually provisioned.

Document:

```text
How to provide TLS certificates
```

without committing private certificates.

---

# 41. API DOCUMENTATION

FastAPI OpenAPI should remain available.

Production may optionally restrict public docs.

Make configurable:

```text
ENABLE_API_DOCS
```

For example:

```text
development → true
production → configurable
```

Do not accidentally expose internal/debug endpoints.

---

# 42. PRODUCTION DEPENDENCY AUDIT

Review:

```text
requirements.txt
pyproject.toml
package.json
package-lock.json
```

Remove:

* unused dependencies
* development-only packages from runtime images where possible
* accidental duplicate libraries

Do not upgrade major dependencies blindly.

Preserve versions known to work.

---

# 43. FRONTEND SECURITY

Review frontend for:

* unsafe HTML rendering
* exposed API keys
* localStorage token risks
* XSS
* unsafe URLs
* uncontrolled redirects
* debug information

Do not put:

```text
GEMINI_API_KEY
OPENAI_API_KEY
DATABASE_URL
SECRET_KEY
```

in frontend environment variables.

Only public configuration may use `VITE_*`.

---

# 44. AUTH TOKEN STORAGE

Choose a secure token strategy.

Prefer an architecture appropriate for production, such as:

```text
HttpOnly Secure SameSite cookie
```

where practical.

If using bearer tokens in frontend storage, explicitly document the security tradeoff and do not store sensitive refresh tokens insecurely.

Do not store credentials in plain application state beyond what is required.

---

# 45. CSRF

If authentication uses cookies, implement CSRF protection for state-changing requests.

If authentication is strictly bearer-token based and not cookie-authenticated, document why CSRF protection is not required.

Do not claim CSRF protection without implementing it.

---

# 46. USER DATA DELETION

Production must support user-level data deletion.

At minimum:

```text
DELETE user account
```

must safely remove or anonymize associated data according to the application's retention policy.

The deletion chain must consider:

```text
User
 ↓
Dataset
 ↓
Profiles
 ↓
Processed datasets
 ↓
Visualizations
 ↓
Patterns
 ↓
Anomalies
 ↓
Predictions
 ↓
Insights
 ↓
Conversations
 ↓
Dataset files
```

Be extremely careful with filesystem cleanup.

Do not claim atomic filesystem/database transactions.

Use coordinated deletion with cleanup and failure logging.

---

# 47. DATASET DELETE SAFETY

Review existing dataset deletion.

Ensure:

```text
database records deleted
dataset files deleted
derived datasets handled
analytical records handled
conversations handled
```

No orphaned records.

No orphaned files.

Add tests.

---

# 48. OBSERVABILITY

Introduce basic production observability.

At minimum:

```text
structured logs
request IDs
health checks
request latency
HTTP status metrics
database connectivity
error tracking hooks
```

If Sentry or another service is added:

```text
SENTRY_DSN
```

must be optional.

The application must still work when Sentry is disabled.

Do not add a complex monitoring stack unless required.

---

# 49. PERFORMANCE HARDENING

Review:

* database queries
* indexes
* repeated dataset loading
* repeated checksum calculation
* large result serialization
* frontend bundle
* API response sizes
* expensive analytical endpoints

Do NOT prematurely optimize.

Focus on measurable bottlenecks.

---

# 50. EXPENSIVE OPERATION PROTECTION

Phase 6–8 and Phase 9 can perform expensive work.

Ensure expensive endpoints cannot be abused through unlimited repeated requests.

At minimum:

```text
profile
preprocess
visualization
patterns
anomalies
predictions
insights
analyst
```

must have reasonable limits and validation.

Do not add a background job system unless current workload actually requires it.

If a synchronous endpoint is retained, enforce request limits and timeouts.

---

# 51. TIMEOUTS

Configure appropriate timeouts for:

```text
database operations
LLM requests
HTTP requests
large analytical operations
```

Do not allow an external LLM request to hang the API indefinitely.

Phase 8/9 fallback behavior must continue working when LLM requests fail.

---

# 52. LLM PRODUCTION SECURITY

Review Phase 8 and Phase 9 LLM integration.

Requirements:

```text
API keys only on backend
no API keys in frontend
timeouts
failure handling
fallback
provider abstraction
logging without secrets
```

Default production behavior may remain:

```text
LLM_ENABLED=false
```

until the operator explicitly configures a provider.

---

# 53. LLM COST PROTECTION

Add configurable limits where appropriate:

```text
maximum prompt size
maximum context size
maximum answer size
request timeout
```

Do not allow unlimited conversation context to be sent to an LLM.

Continue Phase 9's:

```text
MAX_CONTEXT_MESSAGES
MAX_CONTEXT_TOKENS
```

controls.

---

# 54. CI/CD

Create a CI workflow.

If GitHub Actions is appropriate, create:

```text
.github/workflows/ci.yml
```

The workflow should run:

```text
backend tests
frontend build
lint/static checks where configured
migration validation
```

Do not require production secrets for ordinary CI.

LLM tests must use mock mode.

---

# 55. CI TEST DATABASE

CI must use an isolated test database.

Never point tests to production.

Prefer:

```text
PostgreSQL service container
```

for CI integration tests.

This is important because the current local environment reports:

```text
94 PASSED
29 SKIPPED
```

The productionization goal should be to make PostgreSQL-dependent tests executable in CI rather than treating skips as permanent success.

---

# 56. TEST POLICY

Final CI must clearly report:

```text
PASSED
FAILED
SKIPPED
```

Skipped tests must not be counted as passed.

Phase 10 should aim to reduce avoidable PostgreSQL skips by providing a test PostgreSQL service in CI.

---

# 57. PRODUCTION TEST SUITE

Add:

```text
test_auth.py
test_authorization.py
test_user_dataset_isolation.py
test_production_config.py
test_security_headers.py
test_rate_limiting.py
test_file_access_security.py
test_user_deletion.py
test_health.py
```

Adapt filenames to existing conventions.

---

# 58. AUTH TESTS

Test:

```text
registration
duplicate email
login
wrong password
expired token
invalid token
inactive user
/me
```

Ensure:

```text
password_hash != password
```

and password hashes are never returned.

---

# 59. AUTHORIZATION TESTS

Create users:

```text
User A
User B
```

Create dataset:

```text
Dataset A → User A
```

Then attempt:

```text
User B → Dataset A
```

Expected:

```text
404 or appropriate authorization-safe response
```

Test this for:

```text
profile
preprocessing
visualization
patterns
anomalies
predictions
insights
analyst
file access
```

---

# 60. FILE SECURITY TESTS

Test:

```text
path traversal
unauthorized download
unauthorized delete
invalid file extension
oversized file
empty file
fake extension
```

No unauthorized user should obtain dataset content.

---

# 61. USER DELETION TEST

Create:

```text
User
Dataset
Profile
Processed Dataset
Visualization
Pattern
Anomaly
Prediction
Insight
Conversation
Dataset files
```

Delete the user.

Verify:

```text
database records removed
files removed
no orphan analytical records
no orphan conversations
```

---

# 62. PRODUCTION CONFIG TESTS

Test:

```text
production + missing DATABASE_URL
production + missing SECRET_KEY
production + DEBUG=true
test configuration isolation
```

Ensure configuration fails safely.

---

# 63. HEALTH TESTS

Test:

```text
/health
/health/db
/health/live
/health/ready
```

where implemented.

Test database unavailable behavior.

The application should distinguish:

```text
liveness
readiness
database health
```

---

# 64. FINAL E2E TEST

The final production-like E2E flow must be:

```text
Register
 ↓
Login
 ↓
Create/Upload Dataset
 ↓
Profile
 ↓
Preprocess
 ↓
Generate Visualizations
 ↓
Discover Patterns
 ↓
Run Anomaly Detection / Prediction
 ↓
Generate AI Insights
 ↓
Open Analyst
 ↓
Ask Natural-Language Question
 ↓
Ask Follow-Up
 ↓
View Evidence
 ↓
View Visualization
 ↓
Delete Dataset
 ↓
Verify Files Removed
 ↓
Logout
```

Then test:

```text
User B cannot access User A's data.
```

---

# 65. DOCKER E2E

Run the complete application using production-like containers.

Verify:

```text
docker compose build
docker compose up
```

Then:

```text
frontend accessible
backend accessible
database healthy
migration applied
authentication works
upload works
analysis works
analyst works
```

Do not use development hot reload.

---

# 66. DATABASE MIGRATION E2E

Test:

```text
empty PostgreSQL
↓
run migrations
↓
application startup
↓
health check
```

Then test:

```text
existing database
↓
migration
↓
application startup
```

Never delete existing production data during migration testing.

---

# 67. BACKWARD COMPATIBILITY

Phase 10 must preserve all existing APIs unless a security change requires authentication.

If authentication is newly introduced:

* update frontend API client
* update protected routes
* update tests
* update documentation

Do not silently break Phase 1–9 functionality.

---

# 68. API VERSIONING

Preserve:

```text
/api/v1
```

Do not introduce:

```text
/api/v2
```

during Phase 10 unless a genuine breaking change is unavoidable.

---

# 69. FRONTEND PRODUCTION UX

Review the final UI.

Ensure:

```text
authentication pages
login
register
logout
current user
dataset ownership
loading states
error states
session expiration
```

The existing VizMind dashboard should remain intact.

Do not completely redesign the UI.

---

# 70. SESSION EXPIRATION

If the access token expires:

```text
API → 401
      ↓
Frontend detects session expiration
      ↓
attempt refresh if supported
      OR
redirect to login
```

Do not leave the user in a broken state.

---

# 71. PRODUCTION ERROR UI

Frontend should display human-readable messages.

Never show:

```text
Python traceback
SQL error
filesystem path
stack trace
```

Example:

```text
Something went wrong while processing the dataset.
Request ID: abc123
```

---

# 72. FINAL API AUDIT

Audit every route.

Create a table in documentation:

```text
Endpoint
Method
Authentication
Authorization
Purpose
Rate limited
```

Include all Phase 1–10 endpoints.

---

# 73. SECURITY AUDIT

Before declaring completion, search the repository for:

```text
eval(
exec(
os.system(
subprocess
password =
SECRET_KEY =
API_KEY =
localhost
0.0.0.0
CORS *
```

Review each result.

Do not blindly remove legitimate development configuration.

Identify which are:

```text
development-only
test-only
production-safe
security issue
```

---

# 74. DEPENDENCY SECURITY

Run available dependency audits.

For Python:

```text
pip-audit
```

if available.

For frontend:

```text
npm audit
```

Review results.

Do not blindly upgrade packages because of every warning.

Document unresolved vulnerabilities and rationale if necessary.

---

# 75. CONTAINER SECURITY

Review images for:

* root execution
* unnecessary packages
* exposed secrets
* excessive permissions
* writable filesystem where unnecessary
* development tooling

Run containers as non-root wherever practical.

---

# 76. RESOURCE LIMITS

Production Docker configuration should define reasonable resource expectations.

Do not create arbitrary extreme limits.

Document expected:

```text
CPU
RAM
disk
database storage
dataset storage
```

especially because Pandas-based analysis operates in memory.

---

# 77. LARGE DATASET LIMITATION

Document the current architecture honestly.

VizMind uses:

```text
Pandas
in-memory analytical processing
```

Therefore it is not an unlimited big-data platform.

Do not falsely claim:

```text
petabyte-scale
unlimited datasets
real-time distributed analytics
```

unless actually implemented.

---

# 78. STORAGE LIMITATION

Document:

```text
MAX_UPLOAD_SIZE_MB
dataset storage requirements
database storage
backup requirements
```

Do not claim cloud object storage unless actually configured.

---

# 79. PRODUCTION README

Rewrite/update README with:

```text
Project overview
Architecture
Features
Phase 1–10
Technology stack
Local development
Environment configuration
Database setup
Docker setup
Production deployment
Authentication
Security
Backups
Testing
CI/CD
Known limitations
```

Include architecture diagram.

---

# 80. DEPLOYMENT GUIDE

Create:

```text
docs/deployment.md
```

Include:

```text
Prerequisites
Environment variables
Database setup
Migration
Backend deployment
Frontend deployment
Reverse proxy
HTTPS
Dataset storage
Backups
Health checks
Logging
Rollback
Troubleshooting
```

---

# 81. SECURITY DOCUMENTATION

Create:

```text
docs/security.md
```

Document:

* authentication
* authorization
* password hashing
* dataset isolation
* file security
* LLM key security
* prompt injection protection
* rate limiting
* CORS
* security headers
* secrets
* backups
* deletion
* known limitations

---

# 82. OPERATIONS DOCUMENTATION

Create:

```text
docs/operations.md
```

Document:

```text
start
stop
restart
migration
backup
restore
logs
health
troubleshooting
rollback
```

---

# 83. ARCHITECTURE DOCUMENTATION

Update:

```text
docs/architecture.md
```

Final architecture should show:

```text
User
 ↓
Frontend
 ↓
Reverse Proxy
 ↓
FastAPI
 ├── Authentication
 ├── Dataset Management
 ├── Profiling
 ├── Preprocessing
 ├── Visualization
 ├── Pattern Discovery
 ├── Anomaly / Prediction
 ├── AI Insights
 └── Natural-Language Analyst
       ↓
PostgreSQL
       +
Dataset Storage
       +
Optional LLM Provider
```

---

# 84. PRODUCTION DEPLOYMENT TARGET

The implementation must support at least one concrete deployment method.

Recommended baseline:

```text
Docker Compose
+
PostgreSQL
+
Backend
+
Frontend
+
Reverse Proxy
```

Do not implement multiple cloud providers.

Do not create AWS + Azure + GCP deployment simultaneously.

One clean deployment path is sufficient.

---

# 85. OPTIONAL CLOUD DEPLOYMENT

If the repository already targets a platform, preserve it.

Otherwise, provide deployment documentation rather than hard-coding cloud-specific infrastructure.

Do NOT introduce Terraform, Kubernetes, Helm, ECS, GKE, AKS, etc. unless explicitly required.

Phase 10 is about production readiness, not infrastructure complexity.

---

# 86. FINAL PERFORMANCE REVIEW

Measure or inspect:

```text
API response time
dataset upload
profile time
preprocessing time
visualization generation
pattern discovery
anomaly detection
prediction
insight generation
analyst response
```

Do not invent benchmark numbers.

Report measured values only.

---

# 87. FINAL SECURITY CHECKLIST

Before completion confirm:

```text
✓ Authentication
✓ Password hashing
✓ Authorization
✓ Dataset ownership
✓ File access protection
✓ Secret protection
✓ CORS restriction
✓ Security headers
✓ Request validation
✓ Rate limiting
✓ Query limits
✓ Upload limits
✓ Error sanitization
✓ Request IDs
✓ Structured logging
✓ HTTPS deployment guidance
✓ Dependency audit
✓ Container security
✓ Backup documentation
✓ User deletion
```

---

# 88. FINAL ANALYTICAL REGRESSION

Phase 10 must prove that productionization did not break:

```text
Phase 1 health
Phase 2 upload
Phase 3 profile
Phase 4 preprocessing
Phase 5 visualization
Phase 6 patterns
Phase 7 anomaly/prediction
Phase 8 insights
Phase 9 analyst
```

All existing functionality must remain operational.

---

# 89. TEST EXECUTION

Run backend tests:

```bash
cd backend
python -m pytest tests/ -v
```

Run frontend:

```bash
cd frontend
npm run build
```

Run migrations:

```bash
cd backend
alembic upgrade head
alembic current
alembic heads
```

Run production-like containers:

```bash
docker compose build
docker compose up
```

Run CI tests against PostgreSQL.

---

# 90. TEST RESULT REPORTING

The completion report MUST distinguish:

```text
PASSED
FAILED
SKIPPED
```

Never say:

```text
100% passed
```

if tests were skipped.

Example:

```text
Backend:
Passed: X
Failed: 0
Skipped: 0

Frontend:
Build: PASS

Database:
Migration: PASS

Docker:
Build: PASS
Startup: PASS

E2E:
PASS
```

If something is skipped, explain why.

---

# 91. FINAL PRODUCTION SMOKE TEST

Perform:

```text
1. Start PostgreSQL
2. Run migrations
3. Start backend
4. Start frontend/reverse proxy
5. Register user
6. Login
7. Upload CSV
8. Profile
9. Preprocess
10. Generate visualizations
11. Discover patterns
12. Run anomaly detection/prediction
13. Generate insights
14. Open Analyst
15. Ask question
16. Ask follow-up
17. Verify evidence
18. Verify authorization
19. Delete dataset
20. Verify file deletion
21. Logout
```

All critical steps must succeed.

---

# 92. FINAL ACCEPTANCE CRITERIA

Phase 10 is complete only if:

## Application

```text
✓ Frontend production build works
✓ Backend production startup works
✓ PostgreSQL works
✓ Migrations work
✓ Docker build works
✓ Docker startup works
```

## Security

```text
✓ Users authenticate
✓ Users cannot access other users' datasets
✓ Passwords are hashed
✓ Secrets are protected
✓ Files are protected
✓ LLM keys remain backend-only
✓ Rate limits exist
✓ Production errors are sanitized
```

## Analytics

```text
✓ Phase 1–9 functionality remains intact
✓ Dataset upload works
✓ Profiling works
✓ Preprocessing works
✓ Visualization works
✓ Pattern discovery works
✓ Anomaly/prediction works
✓ AI insights work
✓ Natural-language analyst works
```

## Operations

```text
✓ Health checks
✓ Logging
✓ Request IDs
✓ Backups documented
✓ Restore procedure documented
✓ Deployment documented
✓ Rollback documented
```

## CI/CD

```text
✓ Backend tests
✓ PostgreSQL integration tests
✓ Frontend build
✓ Migration validation
✓ Security checks
```

---

# 93. FINAL COMPLETION REPORT

After implementation, provide:

## 1. Implementation Summary

Explain exactly what Phase 10 added.

## 2. Files Created

List every new file.

## 3. Files Modified

List every modified file.

## 4. Database Changes

List:

```text
migration
tables
columns
indexes
foreign keys
cascade rules
```

## 5. Authentication

Explain:

```text
login
registration
token strategy
password hashing
authorization
```

## 6. Security

Explain:

```text
ownership
file protection
CORS
headers
rate limiting
secrets
LLM security
```

## 7. Deployment

Explain:

```text
Docker
PostgreSQL
frontend
backend
reverse proxy
environment configuration
```

## 8. CI/CD

List the pipeline stages.

## 9. Tests

Report:

```text
PASSED: X
FAILED: X
SKIPPED: X
```

## 10. Build

Report:

```text
Frontend build: PASS/FAIL
Backend tests: PASS/FAIL
Docker build: PASS/FAIL
Migration: PASS/FAIL
```

## 11. E2E

Report the complete:

```text
Register
→ Login
→ Upload
→ Profile
→ Preprocess
→ Visualize
→ Discover
→ Anomaly/Prediction
→ Insights
→ Analyst
→ Follow-up
→ Delete
→ Authorization test
```

## 12. Known Limitations

Be honest.

Examples may include:

```text
Pandas-based in-memory processing
single-node deployment
no distributed job queue
cloud provider deployment not automated
LLM provider optional
```

Do not claim features that were not implemented.

---

# 94. STRICT PHASE BOUNDARY

Phase 10 is the FINAL planned phase.

Do not create a Phase 11.

Do not add:

```text
new analytics
new ML models
new AI agents
new data science features
new visualization algorithms
```

unless explicitly requested after Phase 10.

---

# 95. MANDATORY IMPLEMENTATION RULE

Follow this sequence:

```text
1. Inspect existing Phase 1–9 implementation
2. Identify production gaps
3. Create implementation plan
4. Review existing architecture for conflicts
5. Implement authentication
6. Implement authorization/data isolation
7. Harden configuration/secrets
8. Harden API/file security
9. Productionize database
10. Dockerize backend
11. Dockerize frontend
12. Add production compose
13. Add health/readiness
14. Add observability
15. Add CI/CD
16. Add backups/documentation
17. Add production tests
18. Run complete regression
19. Run Docker E2E
20. Fix failures
21. Update documentation
22. Produce final completion report
23. STOP
```

---

# 96. DO NOT BREAK EXISTING FUNCTIONALITY

Before changing an existing component:

```text
inspect
understand
modify minimally
test
```

Do not rewrite working Phase 1–9 systems.

Do not create duplicate:

* Dataset models
* Processed Dataset models
* LLM providers
* visualization services
* pattern engines
* anomaly engines
* prediction engines
* insight engines
* analyst engines

Reuse existing architecture.

---

# 97. FINAL ARCHITECTURAL PRINCIPLE

The final VizMind architecture must remain:

```text
                    VIZMIND
                       │
              ┌────────┴────────┐
              │                 │
          Frontend            API
              │                 │
              │          Authentication
              │                 │
              │          Authorization
              │                 │
              │          Dataset Layer
              │                 │
              │        ┌────────┴────────┐
              │        │                 │
              │    Data Intelligence   AI Intelligence
              │        │                 │
              │   Phase 3–7          Phase 8–9
              │        │                 │
              │        └────────┬────────┘
              │                 │
              └────────────┬────┘
                           │
                     PostgreSQL
                           +
                    Dataset Storage
                           +
                    Optional LLM
```

The production system must preserve the fundamental VizMind principle:

> **Deterministic analytical engines produce the evidence. AI explains the evidence. Production infrastructure securely delivers the system to users.**

Implement Phase 10 only, verify it thoroughly, document it completely, and then STOP.
