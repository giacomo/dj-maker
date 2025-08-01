"""
Tests for the main entry point function in __init__.py
"""
import sys
from unittest.mock import patch
import pytest
from dj_maker import main


def test_main_function_no_args():
    """Test main function when no arguments are provided."""
    with patch('sys.argv', ['django-cli']), \
         patch('dj_maker.app', side_effect=SystemExit(0)) as mock_app:

        # The main function calls app() which should raise SystemExit
        with pytest.raises(SystemExit):
            main()

        # Should call app with --help when no args provided
        mock_app.assert_called_once_with(["--help"])


def test_main_function_with_args():
    """Test main function when arguments are provided."""
    with patch('sys.argv', ['django-cli', 'urls', 'list']), \
         patch('dj_maker.app', side_effect=SystemExit(1)) as mock_app:

        # The main function calls app() which should raise SystemExit
        with pytest.raises(SystemExit):
            main()

        # Should call app with the provided arguments
        mock_app.assert_called_once_with(['urls', 'list'])


def test_main_function_with_version():
    """Test main function with version argument."""
    with patch('sys.argv', ['django-cli', '--version']), \
         patch('dj_maker.app', side_effect=SystemExit(0)) as mock_app:

        # The main function calls app() which should raise SystemExit
        with pytest.raises(SystemExit):
            main()

        # Should call app with --version
        mock_app.assert_called_once_with(['--version'])
