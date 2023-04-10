from unittest.mock import MagicMock, patch

import pytest

from file_handler import FileHandler


def test_create_directory():
    with patch('os.makedirs', MagicMock()) as mocked_makedirs:
        file_handler = FileHandler("test_directory")
        file_handler.create_directory()
        mocked_makedirs.assert_called_once_with("test_directory", exist_ok=True)


def test_delete_old_output():
    with patch('os.path.exists', MagicMock(return_value=True)):
        with patch('os.remove', MagicMock()) as mocked_remove:
            file_handler = FileHandler("test_directory")
            file_handler.delete_old_output("test_directory/output.json")
            mocked_remove.assert_called_once_with("test_directory/output.json")


if __name__ == "__main__":
    pytest.main()

