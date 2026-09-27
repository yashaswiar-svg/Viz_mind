from typing import Any, Dict
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging import logger


class VizMindException(Exception):
    """Base exception class for VizMind application."""

    def __init__(
        self,
        message: str = "An internal server error occurred.",
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseConnectionException(VizMindException):
    def __init__(self, message: str = "Database connection failed."):
        super().__init__(
            message=message,
            code="DATABASE_CONNECTION_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class EntityNotFoundException(VizMindException):
    def __init__(self, message: str = "Requested resource not found.", code: str = "NOT_FOUND"):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class DatasetNotFoundException(EntityNotFoundException):
    def __init__(self, message: str = "Dataset not found."):
        super().__init__(message=message, code="DATASET_NOT_FOUND")


class ProfileNotFoundException(EntityNotFoundException):
    def __init__(self, message: str = "Dataset profile not found."):
        super().__init__(message=message, code="PROFILE_NOT_FOUND")


class ProfileRequiredException(VizMindException):
    def __init__(self, message: str = "Phase 3 dataset profile is required before preprocessing."):
        super().__init__(message=message, code="PROFILE_REQUIRED", status_code=status.HTTP_400_BAD_REQUEST)


class PreprocessingRequiredException(VizMindException):
    def __init__(self, message: str = "Phase 4 dataset preprocessing is required before generating visualizations."):
        super().__init__(message=message, code="PREPROCESSING_REQUIRED", status_code=status.HTTP_400_BAD_REQUEST)


class PreprocessingNotFoundException(EntityNotFoundException):
    def __init__(self, message: str = "Preprocessing report not found."):
        super().__init__(message=message, code="PREPROCESSING_NOT_FOUND")


class PreprocessingException(VizMindException):
    def __init__(self, message: str = "Preprocessing execution failed.", code: str = "PREPROCESSING_FAILED", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message=message, code=code, status_code=status_code)


class VisualizationNotFoundException(EntityNotFoundException):
    def __init__(self, message: str = "Visualization recommendation not found."):
        super().__init__(message=message, code="VISUALIZATION_NOT_FOUND")


class VisualizationException(VizMindException):
    def __init__(self, message: str = "Visualization generation failed.", code: str = "VISUALIZATION_FAILED", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message=message, code=code, status_code=status_code)


class PatternNotFoundException(EntityNotFoundException):
    def __init__(self, message: str = "Discovered pattern record not found."):
        super().__init__(message=message, code="PATTERN_DISCOVERY_NOT_FOUND")


class PatternDiscoveryException(VizMindException):
    def __init__(self, message: str = "Pattern discovery execution failed.", code: str = "PATTERN_DISCOVERY_FAILED", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message=message, code=code, status_code=status_code)


class PatternVersionMismatchException(VizMindException):
    def __init__(self, message: str = "Processed dataset checksum or version mismatch detected."):
        super().__init__(message=message, code="PATTERN_DATASET_VERSION_MISMATCH", status_code=status.HTTP_400_BAD_REQUEST)


# Phase 7 — Anomaly Detection & Prediction Exceptions
class AnomalyNotFoundException(EntityNotFoundException):
    def __init__(self, message: str = "Anomaly detection run or result not found."):
        super().__init__(message=message, code="ANOMALY_RUN_NOT_FOUND")


class AnomalyDetectionException(VizMindException):
    def __init__(self, message: str = "Anomaly detection execution failed.", code: str = "ANOMALY_DETECTION_FAILED", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message=message, code=code, status_code=status_code)


class AnomalyVersionMismatchException(VizMindException):
    def __init__(self, message: str = "Processed dataset checksum or version mismatch detected during anomaly detection."):
        super().__init__(message=message, code="ANOMALY_DATASET_VERSION_MISMATCH", status_code=status.HTTP_400_BAD_REQUEST)


class PredictionNotFoundException(EntityNotFoundException):
    def __init__(self, message: str = "Prediction run or result not found."):
        super().__init__(message=message, code="PREDICTION_RUN_NOT_FOUND")


class PredictionException(VizMindException):
    def __init__(self, message: str = "Prediction execution failed.", code: str = "MODEL_TRAINING_FAILED", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message=message, code=code, status_code=status_code)


class PredictionVersionMismatchException(VizMindException):
    def __init__(self, message: str = "Processed dataset checksum or version mismatch detected during prediction."):
        super().__init__(message=message, code="PREDICTION_DATASET_VERSION_MISMATCH", status_code=status.HTTP_400_BAD_REQUEST)


class TargetColumnRequiredException(VizMindException):
    def __init__(self, message: str = "A valid target_column is required for prediction."):
        super().__init__(message=message, code="TARGET_COLUMN_REQUIRED", status_code=status.HTTP_400_BAD_REQUEST)


class TargetColumnInvalidException(VizMindException):
    def __init__(self, message: str = "The selected target column is invalid or ineligible."):
        super().__init__(message=message, code="TARGET_COLUMN_INVALID", status_code=status.HTTP_400_BAD_REQUEST)


class InsufficientDataException(VizMindException):
    def __init__(self, message: str = "Insufficient observations to run prediction analysis."):
        super().__init__(message=message, code="INSUFFICIENT_DATA", status_code=status.HTTP_400_BAD_REQUEST)


class InsufficientClassSamplesException(VizMindException):
    def __init__(self, message: str = "Insufficient observations per class for classification."):
        super().__init__(message=message, code="INSUFFICIENT_CLASS_SAMPLES", status_code=status.HTTP_400_BAD_REQUEST)


class UnsupportedProblemTypeException(VizMindException):
    def __init__(self, message: str = "The requested problem type is unsupported for this dataset/target."):
        super().__init__(message=message, code="UNSUPPORTED_PROBLEM_TYPE", status_code=status.HTTP_400_BAD_REQUEST)



class FileValidationException(VizMindException):
    def __init__(self, message: str, code: str = "INVALID_FILE", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message=message, code=code, status_code=status_code)


class StorageException(VizMindException):
    def __init__(self, message: str = "A file storage error occurred."):
        super().__init__(
            message=message,
            code="STORAGE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def vizmind_exception_handler(request: Request, exc: VizMindException) -> JSONResponse:
    logger.error(f"VizMindException [{exc.code}]: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        422: "UNPROCESSABLE_ENTITY",
        500: "INTERNAL_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    error_code = code_map.get(exc.status_code, "HTTP_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": error_code,
                "message": str(exc.detail),
            }
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed.",
                "details": exc.errors(),
            }
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
            }
        },
    )
