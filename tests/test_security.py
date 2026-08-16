import pytest
from fastapi import HTTPException, UploadFile
from io import BytesIO
from backend.utils.security import sanitize_filename, validate_uploaded_file, secure_filepath_join

def test_sanitize_filename():
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("my resume (1).pdf") == "my_resume__1_.pdf"
    assert sanitize_filename("script<bad>.exe") == "script_bad_.exe"

def test_validate_unsupported_extension():
    fake_file = UploadFile(filename="malicious.exe", file=BytesIO(b"binary content"))
    with pytest.raises(HTTPException) as exc_info:
        validate_uploaded_file(fake_file, 100)
    assert exc_info.value.status_code == 400
    assert "Unsupported file format" in exc_info.value.detail

def test_validate_file_size_exceeded():
    fake_file = UploadFile(filename="large.pdf", file=BytesIO(b"0" * (11 * 1024 * 1024)))
    with pytest.raises(HTTPException) as exc_info:
        validate_uploaded_file(fake_file, 11 * 1024 * 1024)
    assert exc_info.value.status_code == 400
    assert "exceeds maximum allowed limit" in exc_info.value.detail

def test_secure_filepath_join():
    base_dir = "/tmp/uploads"
    safe_path = secure_filepath_join(base_dir, "../secret.txt")
    assert "secret.txt" in safe_path
    assert not safe_path.startswith("/secret")
