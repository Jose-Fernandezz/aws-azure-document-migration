import logging
from abc import ABC, abstractmethod
from pathlib import Path

import boto3
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from application.config import Config


logger = logging.getLogger(__name__)


class StorageProvider(ABC):
    """Common interface for all supported storage backends."""

    @abstractmethod
    def upload_file(self, source_path, object_key):
        pass

    @abstractmethod
    def download_file(self, object_key, destination_path):
        pass

    @abstractmethod
    def delete_file(self, object_key):
        pass

    @abstractmethod
    def file_exists(self, object_key):
        pass


class LocalStorageProvider(StorageProvider):
    """Store documents on the local filesystem during development."""

    def __init__(self):
        self.base_path = Path(Config.LOCAL_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def upload_file(self, source_path, object_key):
        source_path = Path(source_path)
        destination_path = self.base_path / object_key

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_bytes(source_path.read_bytes())

        logger.info("Stored local file: %s", object_key)

        return str(destination_path)

    def download_file(self, object_key, destination_path):
        source_path = self.base_path / object_key
        destination_path = Path(destination_path)

        if not source_path.exists():
            raise FileNotFoundError(
                f"Local storage object does not exist: {object_key}"
            )

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_bytes(source_path.read_bytes())

        return str(destination_path)

    def delete_file(self, object_key):
        file_path = self.base_path / object_key

        if file_path.exists():
            file_path.unlink()
            logger.info("Deleted local file: %s", object_key)

    def file_exists(self, object_key):
        return (self.base_path / object_key).exists()


class S3StorageProvider(StorageProvider):
    """Store documents in Amazon S3."""

    def __init__(self):
        if not Config.S3_BUCKET_NAME:
            raise ValueError(
                "S3_BUCKET_NAME must be configured when using S3 storage."
            )

        self.bucket_name = Config.S3_BUCKET_NAME

        self.client = boto3.client(
            "s3",
            region_name=Config.AWS_REGION,
        )

    def upload_file(self, source_path, object_key):
        self.client.upload_file(
            str(source_path),
            self.bucket_name,
            object_key,
        )

        logger.info(
            "Uploaded file to S3: s3://%s/%s",
            self.bucket_name,
            object_key,
        )

        return f"s3://{self.bucket_name}/{object_key}"

    def download_file(self, object_key, destination_path):
        destination_path = Path(destination_path)
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        self.client.download_file(
            self.bucket_name,
            object_key,
            str(destination_path),
        )

        return str(destination_path)

    def delete_file(self, object_key):
        self.client.delete_object(
            Bucket=self.bucket_name,
            Key=object_key,
        )

        logger.info("Deleted S3 object: %s", object_key)

    def file_exists(self, object_key):
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=object_key,
            )
            return True
        except self.client.exceptions.ClientError as error:
            response_code = error.response.get("Error", {}).get("Code")

            if response_code in ("404", "NoSuchKey", "NotFound"):
                return False

            raise


class AzureBlobStorageProvider(StorageProvider):
    """Store documents in Azure Blob Storage."""

    def __init__(self):
        if not Config.AZURE_STORAGE_ACCOUNT:
            raise ValueError(
                "AZURE_STORAGE_ACCOUNT must be configured "
                "when using Azure storage."
            )

        account_url = (
            f"https://{Config.AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"
        )

        credential = DefaultAzureCredential()

        self.service_client = BlobServiceClient(
            account_url=account_url,
            credential=credential,
        )

        self.container_client = self.service_client.get_container_client(
            Config.AZURE_STORAGE_CONTAINER
        )

    def upload_file(self, source_path, object_key):
        blob_client = self.container_client.get_blob_client(object_key)

        with Path(source_path).open("rb") as file:
            blob_client.upload_blob(file, overwrite=True)

        logger.info("Uploaded Azure blob: %s", object_key)

        return (
            f"https://{Config.AZURE_STORAGE_ACCOUNT}"
            f".blob.core.windows.net/"
            f"{Config.AZURE_STORAGE_CONTAINER}/"
            f"{object_key}"
        )

    def download_file(self, object_key, destination_path):
        blob_client = self.container_client.get_blob_client(object_key)

        destination_path = Path(destination_path)
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        with destination_path.open("wb") as file:
            download_stream = blob_client.download_blob()
            file.write(download_stream.readall())

        return str(destination_path)

    def delete_file(self, object_key):
        blob_client = self.container_client.get_blob_client(object_key)
        blob_client.delete_blob()

        logger.info("Deleted Azure blob: %s", object_key)

    def file_exists(self, object_key):
        blob_client = self.container_client.get_blob_client(object_key)
        return blob_client.exists()


def get_storage_provider():
    """Return the configured storage backend."""

    provider = Config.STORAGE_PROVIDER

    if provider == "local":
        return LocalStorageProvider()

    if provider == "s3":
        return S3StorageProvider()

    if provider == "azure":
        return AzureBlobStorageProvider()

    raise ValueError(
        f"Unsupported STORAGE_PROVIDER: {provider}"
    )