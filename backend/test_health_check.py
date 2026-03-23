import pytest
from unittest.mock import patch
from services.health_check import SystemValidator

def test_check_binaries_all_installed():
    """Test when all binaries are installed."""
    with patch("shutil.which") as mock_which:
        mock_which.return_value = "/usr/bin/dummy_path"

        results = SystemValidator.check_binaries()

        for binary in SystemValidator.BINARIES:
            assert binary in results
            assert results[binary] == "INSTALLED ✅"

def test_check_binaries_all_missing():
    """Test when all binaries are missing."""
    with patch("shutil.which") as mock_which:
        mock_which.return_value = None

        results = SystemValidator.check_binaries()

        for binary in SystemValidator.BINARIES:
            assert binary in results
            assert results[binary] == "MISSING ❌"

def test_check_binaries_mixed():
    """Test when some binaries are installed and some are missing."""
    installed_binaries = {"python", "node"}

    def mock_which_side_effect(binary):
        if binary in installed_binaries:
            return f"/usr/bin/{binary}"
        return None

    with patch("shutil.which", side_effect=mock_which_side_effect):
        results = SystemValidator.check_binaries()

        for binary in SystemValidator.BINARIES:
            assert binary in results
            if binary in installed_binaries:
                assert results[binary] == "INSTALLED ✅"
            else:
                assert results[binary] == "MISSING ❌"
