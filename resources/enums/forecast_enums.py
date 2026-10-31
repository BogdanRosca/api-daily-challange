"""Forecast-upload enums."""

from enum import StrEnum


class UploadStatus(StrEnum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
