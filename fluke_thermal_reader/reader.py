"""
Main class for reading Fluke thermal files.
"""

from typing import Union, List, Dict, Any
from pathlib import Path
from .parsers import IS2Parser


def read_is2(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Main function to read Fluke thermal .is2 files.
    
    This is the function that users should use to load .is2 files.
    Returns a dictionary with all data extracted from the file.
    
    Args:
        file_path: Path to the thermal .is2 file
        
    Returns:
        Dict[str, Any]: Dictionary containing all thermal data:
            - 'data': numpy array with temperature data
            - 'size': image dimensions [width, height]
            - 'emissivity': emissivity
            - 'transmission': transmission
            - 'backgroundtemperature': background temperature
            - 'CameraManufacturer': camera manufacturer
            - 'CameraModel': camera model
            - 'CameraSerial': camera serial
            - 'FileName': file name
            - 'thumbnail_path': path to thumbnail image (if available)
            - 'photo_path': path to visible image (if available)
    
    Usage example:
        import fluke_thermal_reader
        
        # Load a .is2 file
        data = fluke_thermal_reader.read_is2("thermal_image.is2")
        
        # Access temperature data
        temperature_data = data['data']
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_extension = file_path.suffix.lower()
    
    if file_extension == '.is2':
        parser = IS2Parser()
        return parser.parse(str(file_path))
    else:
        raise ValueError(f"Unsupported file format: {file_extension}. "
                       f"Supported formats: .is2")


def read_is3(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Function to read Fluke thermal .is3 files (FUTURE WORK).
    
    WARNING: This function is not yet implemented.
    Support for .is3 files is planned for a future version.
    
    Args:
        file_path: Path to the thermal .is3 file
        
    Returns:
        Dict[str, Any]: Dictionary containing thermal data
        
    Raises:
        NotImplementedError: Always, since not yet implemented
    """
    raise NotImplementedError(
        "Support for .is3 files is not yet implemented. "
        "This functionality is planned for a future version."
    )


class FlukeReader:
    """
    Main class for reading Fluke thermal files (.is2 supported, .is3 future work).
    
    Usage example:
        reader = FlukeReader()
        data = reader.read_file("thermal_image.is2")
    """
    
    def __init__(self):
        """Initialize the FlukeReader."""
        self.is2_parser = IS2Parser()
        # IS3Parser not yet implemented (future work)
    
    def read_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Read a Fluke thermal file and return a dictionary with the data.
        
        Args:
            file_path: Path to the file (.is2 supported, .is3 future work)
            
        Returns:
            Dict[str, Any]: Dictionary containing thermal data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is not supported
            NotImplementedError: For .is3 files (future work)
        """
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.is2':
            return read_is2(file_path)
        elif file_extension == '.is3':
            return read_is3(file_path)  # Will raise NotImplementedError
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def read_directory(self, directory_path: Union[str, Path], 
                      recursive: bool = False) -> List[Dict[str, Any]]:
        """
        Read all thermal files in a directory.
        
        Args:
            directory_path: Path to the directory
            recursive: If True, search recursively in subdirectories
            
        Returns:
            List[Dict[str, Any]]: List of dictionaries with thermal data
        """
        directory_path = Path(directory_path)
        thermal_data = []
        
        if not directory_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory_path}")
        
        # Search for .is2 and .is3 files
        pattern = "**/*" if recursive else "*"
        for file_path in directory_path.glob(pattern):
            if file_path.suffix.lower() in ['.is2', '.is3']:
                try:
                    data = self.read_file(file_path)
                    thermal_data.append(data)
                except Exception as e:
                    continue
        
        return thermal_data
    
    def get_supported_formats(self) -> List[str]:
        """
        Return the list of supported formats.
        
        Returns:
            List[str]: List of supported formats
        """
        return ['.is2', '.is3']
    
    def validate_file(self, file_path: Union[str, Path]) -> bool:
        """
        Validate if a file is a valid Fluke thermal file.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            bool: True if the file is valid, False otherwise
        """
        try:
            self.read_file(file_path)
            return True
        except Exception:
            return False
