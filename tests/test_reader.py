"""
Test per FlukeReader.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from fluke_reader import FlukeReader
from fluke_reader.models import ThermalImage, MeasurementData


class TestFlukeReader:
    """Test per la classe FlukeReader."""
    
    def setup_method(self):
        """Setup per ogni test."""
        self.reader = FlukeReader()
    
    def test_supported_formats(self):
        """Test per i formati supportati."""
        formats = self.reader.get_supported_formats()
        assert '.is2' in formats
        assert '.is3' in formats
        assert len(formats) == 2
    
    def test_read_nonexistent_file(self):
        """Test per file inesistente."""
        with pytest.raises(FileNotFoundError):
            self.reader.read_file("nonexistent.is2")
    
    def test_read_unsupported_format(self):
        """Test per formato non supportato."""
        with patch('pathlib.Path.exists', return_value=True):
            with pytest.raises(ValueError, match="Formato file non supportato"):
                self.reader.read_file("test.txt")
    
    def test_validate_file_nonexistent(self):
        """Test validazione file inesistente."""
        assert not self.reader.validate_file("nonexistent.is2")
    
    def test_read_directory_nonexistent(self):
        """Test lettura directory inesistente."""
        with pytest.raises(NotADirectoryError):
            self.reader.read_directory("nonexistent_dir")


class TestThermalImage:
    """Test per la classe ThermalImage."""
    
    def setup_method(self):
        """Setup per ogni test."""
        # Crea dati di test
        self.temperature_data = np.array([[20.0, 21.0], [22.0, 23.0]])
        self.measurement_data = MeasurementData(
            temperature_data=self.temperature_data,
            timestamp="2024-01-01 12:00:00",
            device_model="Test Device",
            emissivity=0.95,
            distance=1.0,
            ambient_temperature=20.0,
            relative_humidity=50.0,
            atmospheric_temperature=20.0,
            reflected_temperature=20.0,
            object_distance=1.0,
            object_emissivity=0.95,
            atmospheric_transmission=1.0,
            metadata={}
        )
        
        self.thermal_image = ThermalImage(
            measurement_data=self.measurement_data,
            image_width=2,
            image_height=2,
            pixel_data=self.temperature_data
        )
    
    def test_get_image_shape(self):
        """Test per ottenere le dimensioni dell'immagine."""
        assert self.thermal_image.get_image_shape() == (2, 2)
    
    def test_get_temperature_at_pixel(self):
        """Test per ottenere la temperatura a un pixel."""
        temp = self.thermal_image.get_temperature_at_pixel(0, 0)
        assert temp == 20.0
        
        temp = self.thermal_image.get_temperature_at_pixel(1, 1)
        assert temp == 23.0
    
    def test_get_temperature_at_pixel_out_of_bounds(self):
        """Test per pixel fuori dai limiti."""
        with pytest.raises(IndexError):
            self.thermal_image.get_temperature_at_pixel(10, 10)


class TestMeasurementData:
    """Test per la classe MeasurementData."""
    
    def setup_method(self):
        """Setup per ogni test."""
        self.temperature_data = np.array([[20.0, 21.0], [22.0, 23.0]])
        self.measurement_data = MeasurementData(
            temperature_data=self.temperature_data,
            timestamp="2024-01-01 12:00:00",
            device_model="Test Device",
            emissivity=0.95,
            distance=1.0,
            ambient_temperature=20.0,
            relative_humidity=50.0,
            atmospheric_temperature=20.0,
            reflected_temperature=20.0,
            object_distance=1.0,
            object_emissivity=0.95,
            atmospheric_transmission=1.0,
            metadata={}
        )
    
    def test_get_temperature_range(self):
        """Test per ottenere il range di temperature."""
        min_temp, max_temp = self.measurement_data.get_temperature_range()
        assert min_temp == 20.0
        assert max_temp == 23.0
    
    def test_get_average_temperature(self):
        """Test per ottenere la temperatura media."""
        avg_temp = self.measurement_data.get_average_temperature()
        assert avg_temp == 21.5

