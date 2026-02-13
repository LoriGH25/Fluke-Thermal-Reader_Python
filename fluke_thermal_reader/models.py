"""
Data models for Fluke thermal files.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import numpy as np


@dataclass
class MeasurementData:
    """Thermographic measurement data."""

    temperature_data: np.ndarray
    timestamp: str
    device_model: str
    emissivity: float
    distance: float
    ambient_temperature: float
    relative_humidity: float
    atmospheric_temperature: float
    reflected_temperature: float
    object_distance: float
    object_emissivity: float
    atmospheric_transmission: float
    
    # Additional metadata
    metadata: Dict[str, Any]
    
    def get_temperature_range(self) -> tuple:
        """Return the temperature range (min, max)."""
        return float(np.min(self.temperature_data)), float(np.max(self.temperature_data))
    
    def get_average_temperature(self) -> float:
        """Return the average temperature."""
        return float(np.mean(self.temperature_data))


@dataclass
class ThermalImage:
    """A complete thermographic image."""
    
    measurement_data: MeasurementData
    image_width: int
    image_height: int
    pixel_data: np.ndarray
    
    def get_image_shape(self) -> tuple:
        """Return the image dimensions."""
        return (self.image_height, self.image_width)
    
    def get_temperature_at_pixel(self, x: int, y: int) -> float:
        """Return the temperature at the given pixel."""
        if 0 <= x < self.image_width and 0 <= y < self.image_height:
            return float(self.measurement_data.temperature_data[y, x])
        raise IndexError(f"Pixel coordinates ({x}, {y}) out of image bounds")

