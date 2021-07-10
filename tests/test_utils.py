import pytest

from app.utils import import_modules_from_dir


@pytest.fixture
def mock_listdir(mocker):
    mocker.patch(
        "app.utils.listdir",
        return_value=[
            "a.log",
            "ewf",
            "__init__.py",
            "__main__.py",
            "file.py",
            "file2.py",
        ],
    )


@pytest.fixture
def mock_import_module(mocker):
    def mock_import(path: str):
        return path.split(".")[-1] if "." in path else path

    mocker.patch("app.utils.import_module", mock_import)


def test_import_modules_from_dir(mock_listdir, mock_import_module):
    assert import_modules_from_dir("path/to/dir") == ["file", "file2"]
