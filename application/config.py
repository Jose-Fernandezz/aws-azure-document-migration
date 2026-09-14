import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")


class Config:
    APP_NAME = os.getenv(
        "APP_NAME",
        "Cloud Document Management System",
    )

    APP_ENV = os.getenv(
        "APP_ENV",
        "development",
    )

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-only-change-me",
    )

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/aws_azure_document_migration",
    )

    STORAGE_PROVIDER = os.getenv(
        "STORAGE_PROVIDER",
        "local",
    ).lower()

    LOCAL_STORAGE_PATH = Path(
        os.getenv(
            "LOCAL_STORAGE_PATH",
            str(PROJECT_ROOT / "local-storage"),
        )
    )

    AWS_REGION = os.getenv(
        "AWS_REGION",
        "us-east-1",
    )

    S3_BUCKET_NAME = os.getenv(
        "S3_BUCKET_NAME",
        "",
    )

    AZURE_STORAGE_ACCOUNT = os.getenv(
        "AZURE_STORAGE_ACCOUNT",
        "",
    )

    AZURE_STORAGE_CONTAINER = os.getenv(
        "AZURE_STORAGE_CONTAINER",
        "documents",
    )

    MAX_UPLOAD_SIZE_MB = int(
        os.getenv(
            "MAX_UPLOAD_SIZE_MB",
            "10",
        )
    )

    MAX_CONTENT_LENGTH = (
        MAX_UPLOAD_SIZE_MB
        * 1024
        * 1024
    )

    ALLOWED_EXTENSIONS = {
        "pdf",
        "docx",
        "xlsx",
        "csv",
        "txt",
        "png",
        "jpg",
        "jpeg",
    }

    DEPARTMENTS = [
        "Finance",
        "Human Resources",
        "Sales",
        "Operations",
        "Information Technology",
    ]


def validate_config():
    supported_storage_providers = {
        "local",
        "s3",
        "azure",
    }

    if Config.STORAGE_PROVIDER not in supported_storage_providers:
        raise ValueError(
            f"Unsupported STORAGE_PROVIDER: "
            f"{Config.STORAGE_PROVIDER}. "
            f"Expected one of: "
            f"{', '.join(sorted(supported_storage_providers))}"
        )

    if (
        Config.STORAGE_PROVIDER == "s3"
        and not Config.S3_BUCKET_NAME
    ):
        raise ValueError(
            "S3_BUCKET_NAME is required when "
            "STORAGE_PROVIDER=s3."
        )

    if Config.STORAGE_PROVIDER == "azure":
        if not Config.AZURE_STORAGE_ACCOUNT:
            raise ValueError(
                "AZURE_STORAGE_ACCOUNT is required when "
                "STORAGE_PROVIDER=azure."
            )

        if not Config.AZURE_STORAGE_CONTAINER:
            raise ValueError(
                "AZURE_STORAGE_CONTAINER is required when "
                "STORAGE_PROVIDER=azure."
            )