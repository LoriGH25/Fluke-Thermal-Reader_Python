"""Read Fluke .is2 thermal files; returns dict with data (numpy °C), size, metadata, paths."""

from typing import Union, List, Dict, Any
from pathlib import Path
from .parsers import IS2Parser


def read_is2(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Read .is2 file; return dict with 'data' (temperature array °C), 'size', metadata, thumbnail_path, photo_path."""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_extension = file_path.suffix.lower()

    if file_extension == ".is2":
        parser = IS2Parser()
        return parser.parse(str(file_path))
    else:
        raise ValueError(
            f"Unsupported file format: {file_extension}. Supported formats: .is2"
        )


def read_is3(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Not implemented."""
    raise NotImplementedError(".is3 support not implemented")


class FlukeReader:
    """Read .is2 (and .is3 when implemented) thermal files."""

    def __init__(self):
        self.is2_parser = IS2Parser()

    def read_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Read .is2 file and return thermal data dict."""
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower()
        if file_extension == ".is2":
            return read_is2(file_path)
        elif file_extension == ".is3":
            return read_is3(file_path)
        raise ValueError(f"Unsupported file format: {file_extension}")

    def read_directory(self, directory_path: Union[str, Path], recursive: bool = False) -> List[Dict[str, Any]]:
        """Return list of thermal data dicts for .is2/.is3 in directory."""
        directory_path = Path(directory_path)
        if not directory_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")
        out = []
        pattern = "**/*" if recursive else "*"
        for file_path in directory_path.glob(pattern):
            if file_path.suffix.lower() in [".is2", ".is3"]:
                try:
                    out.append(self.read_file(file_path))
                except Exception:
                    pass
        return out

    def get_supported_formats(self) -> List[str]:
        return [".is2", ".is3"]

    def validate_file(self, file_path: Union[str, Path]) -> bool:
        """Return True if file can be read without error."""
        try:
            self.read_file(file_path)
            return True
        except Exception:
            return False
