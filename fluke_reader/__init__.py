"""
FlukeReader - Python library for reading Fluke thermal files (.is2 and .is3)

This library allows you to read and analyze thermal files generated
by Fluke measurement devices.

Main usage:
    import fluke_reader
    
    # Load a thermal file
    data = fluke_reader.fluke_load("thermal_image.is2")
    
    # Access the data
    temperature_data = data['data']
    print(f"Average temperature: {temperature_data.mean():.2f}°C")
"""

__version__ = "0.1.0"
__author__ = "Lorenzo Ghidini"
__email__ = "lorigh46@gmail.com"

from .reader import fluke_load, FlukeReader
from .parsers import IS2Parser, IS3Parser

__all__ = [
    "fluke_load",  # Funzione principale
    "FlukeReader",
    "IS2Parser", 
    "IS3Parser"
]
