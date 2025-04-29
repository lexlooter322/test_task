import os
import tempfile
from task_tast.tes11t import Reports
import pytest


@pytest.fixture(scope="module")
def sample_log_files():

    content1 = """2025-03-28 12:05:50,000 INFO django.request: GET /admin/dashboard/ 200 OK [192.168.1.48]
                  2025-03-28 12:38:08,000 DEBUG django.db.backends: (0.28) SELECT * FROM 'checkout' WHERE id = 100;
                  2025-03-28 12:05:46,000 WARNING django.security: PermissionDenied: User does not have permission"""
    content2 = "2025-03-28 12:10:21,000 ERROR django.request: Internal Server Error: /admin/login/ [192.168.1.68] - SuspiciousOperation: Invalid HTTP_HOST header\n"

    with tempfile.NamedTemporaryFile(delete=False) as f1:
        f1.write(content1.encode('utf-8'))
        file1 = f1.name

    with tempfile.NamedTemporaryFile(delete=False) as f2:
        f2.write(content2.encode('utf-8'))
        file2 = f2.name

    yield [file1, file2]

    os.unlink(file1)
    os.unlink(file2)

def test_class_initialization(sample_log_files):
    """Проверка правильной инициализации класса."""
    paths_to_logs = sample_log_files
    name_report = "handlers"
    report = Reports(paths_to_logs, name_report)
    assert report.paths_to_logs == paths_to_logs
    assert report.name_report == name_report
    assert report.report is None

def test_parse_log_file(sample_log_files):
    """Проверка правильности парсинга одного лог-файла."""
    report = Reports(sample_log_files, "")
    parsed_data = report.parse_log_file(sample_log_files[0])
    expected_data = {
        "/admin/dashboard/": {"DEBUG": 1, "INFO": 1, "WARNING": 1, "ERROR": 0, "CRITICAL": 0}
    }
    assert parsed_data == expected_data

def test_multiproc_report_handler(sample_log_files):
    """Проверка параллельного построения отчета."""
    report = Reports(sample_log_files, "handlers")
    result = report.multiproc_report_handler()
    expected_result = {
        "/admin/dashboard/": {"DEBUG": 1, "INFO": 1, "WARNING": 1, "ERROR": 0, "CRITICAL": 0},
        "/admin/login/": {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 1, "CRITICAL": 0}
    }
    assert result == expected_result


def test_invalid_path():

    invalid_paths = ["gde_to_tam/app1.log"]
    report = Reports(invalid_paths, "handlers")
    with pytest.raises(FileNotFoundError):
        report.multiproc_report_handler()

def test_missing_required_fields_in_log_entry():

    content = "Invalid log entry without required fields.\n"
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(content.encode('utf-8'))
        filename = f.name

    report = Reports([filename], "handlers")
    with pytest.raises(Exception):
        report.parse_log_file(filename)

    os.unlink(filename)

def test_unknown_log_level():

    content = "2025-03-28 12:05:50,000 LEVEL_P django.request: GET /admin/dashboard/ 200 OK [192.168.1.48]\n"
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(content.encode('utf-8'))
        filename = f.name

    report = Reports([filename], "handlers")
    with pytest.raises(KeyError):
        report.parse_log_file(filename)

    os.unlink(filename)