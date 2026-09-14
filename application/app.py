import hashlib
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from flask import (
    Flask,
    after_this_request,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from application.config import Config

from application.database import (
    execute_query,
    fetch_all,
    fetch_one,
)

from application.storage import get_storage_provider


app = Flask(__name__)
app.config.from_object(Config)

storage = get_storage_provider()

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_documents_from_database():
    return fetch_all(
        """
        SELECT
            record_number,
            original_filename,
            object_key,
            title,
            description,
            department,
            uploaded_by,
            uploaded_at,
            file_type,
            file_size,
            storage_provider,
            storage_location,
            checksum
        FROM documents
        ORDER BY record_number;
        """
    )


def load_document_from_database(record_number):
    return fetch_one(
        """
        SELECT
            record_number,
            original_filename,
            object_key,
            title,
            description,
            department,
            uploaded_by,
            uploaded_at,
            file_type,
            file_size,
            storage_provider,
            storage_location,
            checksum
        FROM documents
        WHERE record_number = %s;
        """,
        (record_number,),
    )


def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()

    with Path(file_path).open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()


@app.route("/")
def index():
    documents = load_documents_from_database()

    return render_template(
        "index.html",
        documents=documents,
    )


@app.route("/documents/<int:record_number>")
def document_detail(record_number):
    document = load_document_from_database(
        record_number
    )

    if document is None:
        return "Document not found", 404

    return render_template(
        "document.html",
        document=document,
    )


@app.route("/documents/<int:record_number>/download")
def download_document(record_number):
    document = load_document_from_database(
        record_number
    )

    if document is None:
        return "Document not found", 404

    file_suffix = Path(
        document["original_filename"]
    ).suffix

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=file_suffix,
    )

    temp_path = Path(temp_file.name)
    temp_file.close()

    try:
        storage.download_file(
            document["object_key"],
            temp_path,
        )

    except FileNotFoundError:
        if temp_path.exists():
            temp_path.unlink()

        return "Stored file not found", 404

    @after_this_request
    def remove_temp_file(response):
        try:
            os.remove(temp_path)
        except OSError:
            pass

        return response

    return send_file(
        temp_path,
        as_attachment=True,
        download_name=document["original_filename"],
    )


@app.route(
    "/documents/<int:record_number>/delete",
    methods=["POST"],
)
def delete_document(record_number):
    document = load_document_from_database(
        record_number
    )

    if document is None:
        return "Document not found", 404

    storage.delete_file(
        document["object_key"]
    )

    execute_query(
        """
        DELETE FROM documents
        WHERE record_number = %s;
        """,
        (record_number,),
    )

    return redirect(
        url_for("index")
    )


@app.route("/upload", methods=["GET", "POST"])
def upload_document():
    if request.method == "GET":
        return render_template("upload.html")

    uploaded_file = request.files.get(
        "document"
    )

    if (
        uploaded_file is None
        or uploaded_file.filename == ""
    ):
        return "No file selected", 400

    title = request.form.get(
        "title",
        "",
    ).strip()

    department = request.form.get(
        "department",
        "",
    ).strip()

    description = request.form.get(
        "description",
        "",
    ).strip()

    uploaded_by = request.form.get(
        "uploaded_by",
        "",
    ).strip()

    if (
        not title
        or not department
        or not uploaded_by
    ):
        return (
            "Title, department, and uploader are required",
            400,
        )

    original_filename = uploaded_file.filename

    file_extension = (
        Path(original_filename)
        .suffix
        .lower()
        .lstrip(".")
    )

    if file_extension not in Config.ALLOWED_EXTENSIONS:
        return "Unsupported file type", 400

    result = fetch_one(
        """
        SELECT
            COALESCE(MAX(record_number), 0) + 1
            AS next_record_number
        FROM documents;
        """
    )

    next_record_number = result[
        "next_record_number"
    ]

    unique_filename = (
        f"{uuid4().hex}-{original_filename}"
    )

    object_key = (
        f"uploads/{unique_filename}"
    )

    temp_path = (
        PROJECT_ROOT
        / "local-storage"
        / "temp"
        / unique_filename
    )

    temp_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    uploaded_file.save(temp_path)

    try:
        file_size = temp_path.stat().st_size

        checksum = calculate_sha256(
            temp_path
        )

        storage_location = storage.upload_file(
            temp_path,
            object_key,
        )

        uploaded_at = datetime.now(
            timezone.utc
        )

        try:
            execute_query(
                """
                INSERT INTO documents (
                    record_number,
                    original_filename,
                    object_key,
                    title,
                    description,
                    department,
                    uploaded_by,
                    uploaded_at,
                    file_type,
                    file_size,
                    storage_provider,
                    storage_location,
                    checksum
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                );
                """,
                (
                    next_record_number,
                    original_filename,
                    object_key,
                    title,
                    description,
                    department,
                    uploaded_by,
                    uploaded_at,
                    file_extension,
                    file_size,
                    "local",
                    str(storage_location),
                    checksum,
                ),
            )

        except Exception:
            storage.delete_file(
                object_key
            )
            raise

    finally:
        if temp_path.exists():
            temp_path.unlink()

    return redirect(
        url_for(
            "document_detail",
            record_number=next_record_number,
        )
    )


@app.route("/health")
def health():
    return {
        "status": "ok",
        "storage_provider": type(storage).__name__,
    }


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True,
    )