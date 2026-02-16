"""
Tests for fluke_thermal_reader.
"""
import pytest
from fluke_thermal_reader import read_is2
from fluke_thermal_reader.parsers import IS2Parser


def test_read_is2_file_not_found():
    """read_is2 raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError, match="File not found"):
        read_is2("nonexistent.is2")


def test_read_is2_unsupported_format():
    """read_is2 raises ValueError for non-.is2 extension."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        read_is2("file.txt")


def test_is2_parser_exists():
    """IS2Parser can be instantiated."""
    p = IS2Parser()
    assert p.temp_dir == "temp_fluke_reader"
