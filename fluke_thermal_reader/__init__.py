"""
Fluke Thermal Reader - Python library for reading Fluke thermal files (.is2 supported, .is3 future work)

This library allows you to read and analyze thermal files generated
by Fluke measurement devices.

Package name: fluke-thermal-reader
Module name: fluke_thermal_reader

Main usage:
    import fluke_thermal_reader
    
    # Load a thermal .is2 file
    data = fluke_thermal_reader.read_is2("thermal_image.is2")
    
    # Access the data
    temperature_data = data['data']
    
    # NOTE: Support for .is3 is planned for the future
"""

__version__ = "0.1.0"
__author__ = "Lorenzo Ghidini"
__email__ = "lorigh46@gmail.com"

from .reader import read_is2, read_is3, FlukeReader
from .parsers import IS2Parser

__all__ = [
    "read_is2",    # Main function for .is2 files
    "read_is3",    # Function for .is3 files (future work)
    "FlukeReader",
    "IS2Parser"
]
