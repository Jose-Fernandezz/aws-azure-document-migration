CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    record_number INTEGER NOT NULL UNIQUE,

    original_filename VARCHAR(255) NOT NULL,
    object_key VARCHAR(512) NOT NULL UNIQUE,

    title VARCHAR(255) NOT NULL,
    description TEXT,

    department VARCHAR(100) NOT NULL,
    uploaded_by VARCHAR(150) NOT NULL,

    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL CHECK (file_size >= 0),

    storage_provider VARCHAR(50) NOT NULL,
    storage_location VARCHAR(512) NOT NULL,

    checksum CHAR(64) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_documents_department
    ON documents (department);

CREATE INDEX IF NOT EXISTS idx_documents_uploaded_by
    ON documents (uploaded_by);

CREATE INDEX IF NOT EXISTS idx_documents_file_type
    ON documents (file_type);

CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at
    ON documents (uploaded_at DESC);

CREATE INDEX IF NOT EXISTS idx_documents_title
    ON documents (title);