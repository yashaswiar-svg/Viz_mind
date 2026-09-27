from typing import List, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "VizMind"
    APP_VERSION: str = "0.2.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    API_PREFIX: str = "/api"
    API_VERSION: str = "v1"

    DATABASE_URL: str = "sqlite+aiosqlite:///./storage/vizmind.db"
    DATABASE_TEST_URL: str = "sqlite+aiosqlite:///./storage/vizmind_test.db"

    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Phase 10 — Productionization & Security Settings
    SECRET_KEY: str = "dev-secret-key-change-in-production-123456789"
    JWT_SECRET_KEY: str = "dev-jwt-secret-key-change-in-production-987654321"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    AUTH_ENABLED: bool = True
    AUTH_TEST_BYPASS: bool = False
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    ENABLE_API_DOCS: bool = True
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # Storage Settings
    STORAGE_PATH: str = "./storage/datasets"
    TEST_STORAGE_PATH: str = "./storage/test_datasets"
    MAX_UPLOAD_SIZE_MB: int = 50

    # Placeholders for future phases
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: Optional[str] = "gemini-1.5-flash"

    # Phase 8 — AI Insight Engine Settings
    LLM_ENABLED: bool = False
    LLM_PROVIDER: str = "mock"
    LLM_TIMEOUT_SECONDS: int = 30
    LLM_MAX_TOKENS: int = 1000
    LLM_TEMPERATURE: float = 0.0
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    MAX_PROFILE_EVIDENCE: int = 10
    MAX_VISUALIZATION_EVIDENCE: int = 10
    MAX_PATTERN_EVIDENCE: int = 15
    MAX_ANOMALY_EVIDENCE: int = 20
    MAX_PREDICTION_EVIDENCE: int = 10
    MAX_TOTAL_EVIDENCE_ITEMS: int = 50
    MAX_INSIGHT_CANDIDATES: int = 30
    MAX_INSIGHTS_PER_RUN: int = 15
    INSIGHT_VALIDATION_STRICT: bool = True

    # Phase 9 — Natural-Language Data Analyst Settings
    MAX_QUERY_ROWS: int = 100
    MAX_QUERY_COLUMNS: int = 20
    MAX_QUERY_RESULT_BYTES: int = 1048576  # 1 MB
    MAX_FILTER_VALUES: int = 50
    MAX_GROUP_VALUES: int = 100
    MAX_QUERY_EXECUTION_SECONDS: int = 10
    MAX_CONVERSATION_TURNS: int = 50
    MAX_CONTEXT_MESSAGES: int = 10

    # Phase 7 — Anomaly Detection & Prediction Settings
    ROBUST_Z_THRESHOLD: float = 3.5
    MAX_ANOMALY_COLUMNS: int = 30
    MAX_ANOMALY_RESULTS: int = 500
    MAX_ANOMALY_RESULTS_PER_COLUMN: int = 100
    MIN_ANOMALY_OBSERVATIONS: int = 10

    MIN_PREDICTION_ROWS: int = 50
    MIN_CLASS_COUNT: int = 10
    MIN_FORECAST_POINTS: int = 30

    TEST_SIZE: float = 0.20
    VALIDATION_SIZE: float = 0.20
    RANDOM_STATE: int = 42

    MAX_FEATURES: int = 30
    MAX_CATEGORICAL_CARDINALITY: int = 20
    MAX_PREDICTION_RESULTS: int = 1000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def api_v1_str(self) -> str:
        return f"{self.API_PREFIX}/{self.API_VERSION}"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    def validate_production_config(self) -> None:
        if self.APP_ENV == "production":
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production environment.")
            if self.SECRET_KEY.startswith("dev-"):
                raise ValueError("SECRET_KEY must be configured securely for production environment.")
            if self.JWT_SECRET_KEY.startswith("dev-"):
                raise ValueError("JWT_SECRET_KEY must be configured securely for production environment.")
            if self.AUTH_TEST_BYPASS:
                raise ValueError("AUTH_TEST_BYPASS cannot be True in production environment.")


settings = Settings()
