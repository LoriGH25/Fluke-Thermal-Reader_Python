"""
Modelli di dati per i file termografici Fluke.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import numpy as np


@dataclass
class MeasurementData:
    """Rappresenta i dati di misurazione termografica."""
    
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
    
    # Metadati aggiuntivi
    metadata: Dict[str, Any]
    
    def get_temperature_range(self) -> tuple:
        """Restituisce il range di temperature (min, max)."""
        return float(np.min(self.temperature_data)), float(np.max(self.temperature_data))
    
    def get_average_temperature(self) -> float:
        """Restituisce la temperatura media."""
        return float(np.mean(self.temperature_data))


@dataclass
class ThermalImage:
    """Rappresenta un'immagine termografica completa."""
    
    measurement_data: MeasurementData
    image_width: int
    image_height: int
    pixel_data: np.ndarray
    
    def get_image_shape(self) -> tuple:
        """Restituisce le dimensioni dell'immagine."""
        return (self.image_height, self.image_width)
    
    def get_temperature_at_pixel(self, x: int, y: int) -> float:
        """Restituisce la temperatura al pixel specificato."""
        if 0 <= x < self.image_width and 0 <= y < self.image_height:
            return float(self.measurement_data.temperature_data[y, x])
        raise IndexError(f"Coordinate pixel ({x}, {y}) fuori dai limiti dell'immagine")

