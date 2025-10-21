"""
Main class for reading Fluke thermal files.
"""

import os
from typing import Union, List, Optional, Dict, Any
from pathlib import Path
from .parsers import IS2Parser, IS3Parser


def fluke_load(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Main function to load Fluke thermal files.
    
    This is the function that users should use to load Fluke files.
    Returns a dictionary with all data extracted from the file.
    
    Args:
        file_path: Path to the thermal file (.is2 or .is3)
        
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
            - 'thumbnail': thumbnail image (if available)
            - 'photo': visible image (if available)
    
    Usage example:
        import fluke_reader
        
        # Load a .is2 file
        data = fluke_reader.fluke_load("thermal_image.is2")
        
        # Access temperature data
        temperature_data = data['data']
        print(f"Dimensions: {data['size']}")
        print(f"Average temperature: {temperature_data.mean():.2f}°C")
        print(f"Emissivity: {data['emissivity']}")
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_extension = file_path.suffix.lower()
    
    if file_extension == '.is2':
        parser = IS2Parser()
        return parser.parse(str(file_path))
    elif file_extension == '.is3':
        parser = IS3Parser()
        return parser.parse(str(file_path))
    else:
        raise ValueError(f"Unsupported file format: {file_extension}. "
                       f"Supported formats: .is2, .is3")


class FlukeReader:
    """
    Main class for reading Fluke thermal files (.is2 and .is3).
    
    Usage example:
        reader = FlukeReader()
        data = reader.read_file("thermal_image.is2")
        print(f"Average temperature: {data['data'].mean():.2f}°C")
    """
    
    def __init__(self):
        """Initialize the FlukeReader."""
        self.is2_parser = IS2Parser()
        self.is3_parser = IS3Parser()
    
    def read_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Read a Fluke thermal file and return a dictionary with the data.
        
        Args:
            file_path: Path to the file (.is2 or .is3)
            
        Returns:
            Dict[str, Any]: Dictionary containing thermal data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is not supported
        """
        return fluke_load(file_path)
    
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
                    print(f"Error reading {file_path}: {e}")
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
