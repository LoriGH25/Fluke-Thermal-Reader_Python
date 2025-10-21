# Fluke Thermal Reader

A Python library for reading and parsing Fluke thermal imaging files (.is2 and .is3 formats).

## Features

- **Complete .is2 support**: Parse Fluke .is2 thermal imaging files
- **Accurate temperature conversion**: Convert raw thermal data to temperature values with high precision
- **Metadata extraction**: Extract camera information, calibration data, and image properties
- **Fusion offset correction**: Automatic correction for horizontal shift in thermal images
- **Tested camera models**: Ti300 and Ti480P (other models supported with user feedback)

## Installation

```bash
pip install fluke-reader
```

## Quick Start

```python
from fluke_reader import fluke_load

# Load a Fluke .is2 file
data = fluke_load("thermal_image.is2")

# Access thermal data
thermal_data = data['data']  # 2D numpy array of temperatures
print(f"Temperature range: {thermal_data.min():.1f}°C - {thermal_data.max():.1f}°C")

# Access metadata
print(f"Camera: {data['CameraModel']}")
print(f"Image size: {data['size']}")
print(f"Emissivity: {data['Emissivity']}")
print(f"Background temperature: {data['BackgroundTemp']}°C")
```

## Supported File Formats

- **.is2**: Fluke thermal imaging format (fully supported)
- **.is3**: Fluke thermal imaging format (planned for future release)

## Tested Camera Models

- **Ti300**: Fully tested and supported
- **Ti480P**: Fully tested and supported

**Other Fluke camera models**: If you have files from other Fluke thermal cameras, please share them so we can add support for additional models.

## API Reference

### `fluke_load(file_path)`

Load and parse a Fluke thermal imaging file.

**Parameters:**
- `file_path` (str): Path to the .is2 or .is3 file

**Returns:**
- `dict`: Dictionary containing thermal data and metadata

**Returned Data Structure:**
```python
{
    'data': numpy.ndarray,           # 2D array of temperature values
    'FileName': str,                 # Original filename
    'CameraModel': str,              # Camera model
    'CameraSerial': str,             # Camera serial number
    'size': [width, height],         # Image dimensions
    'MinTemp': float,               # Minimum temperature
    'MaxTemp': float,               # Maximum temperature
    'AvgTemp': float,               # Average temperature
    'Emissivity': float,            # Emissivity setting
    'BackgroundTemp': float,        # Background temperature
    'CaptureDateTime': str,         # Capture date and time
    'thumbnail': numpy.ndarray,     # Thumbnail image (if available)
    'photo': numpy.ndarray,         # Visible light image (if available)
}
```

## Examples

### Basic Usage

```python
from fluke_reader import fluke_load
import matplotlib.pyplot as plt

# Load thermal data
data = fluke_load("thermal_image.is2")

# Display thermal image
plt.imshow(data['data'], cmap='hot')
plt.colorbar(label='Temperature (°C)')
plt.title(f'Thermal Image - {data["CameraModel"]}')
plt.show()
```

### Batch Processing

```python
import os
from fluke_reader import fluke_load

# Process multiple files
for filename in os.listdir("thermal_images/"):
    if filename.endswith(".is2"):
        data = fluke_load(f"thermal_images/{filename}")
        print(f"Processed {filename}: {data['MinTemp']:.1f}°C - {data['MaxTemp']:.1f}°C")
```

### Temperature Analysis

```python
import numpy as np
from fluke_reader import fluke_load

# Load data
data = fluke_load("thermal_image.is2")
temperatures = data['data']

# Statistical analysis
print(f"Temperature statistics:")
print(f"  Mean: {temperatures.mean():.1f}°C")
print(f"  Std: {temperatures.std():.1f}°C")
print(f"  Min: {temperatures.min():.1f}°C")
print(f"  Max: {temperatures.max():.1f}°C")

# Find hot spots
hot_spots = temperatures > (temperatures.mean() + 2 * temperatures.std())
print(f"Hot spots: {np.sum(hot_spots)} pixels")
```

## Accuracy

The library provides highly accurate temperature readings with:
- **Mean difference**: < 0.5°C compared to Fluke's official software
- **Correlation**: > 0.999 with reference data
- **Precision**: 16 decimal places for temperature values
- **Tested on**: Ti300 and Ti480P cameras with real-world data

## Requirements

- Python 3.7+
- numpy
- matplotlib (optional, for visualization)

## Development

### Project Structure

```
fluke_reader/
├── fluke_reader/          # Main library code
│   ├── __init__.py
│   ├── parsers.py         # File parsers
│   ├── reader.py          # Main reader functions
│   └── models.py          # Data models
├── examples/              # Usage examples
├── test/                  # Test files and analysis scripts
├── legacy/                # Legacy code and references
└── README.md
```

### Running Tests

```bash
# Run basic tests
python -m pytest

# Run with coverage
python -m pytest --cov=fluke_reader
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

**Adding support for new camera models**: If you have .is2 files from other Fluke thermal cameras, please share them so we can extend support to additional models. You can:
- Open an issue with sample files
- Submit a pull request with test data
- Contact the maintainers directly

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Fluke Corporation for the thermal imaging technology
- The open-source community for inspiration and tools

## Changelog

### Version 1.0.0
- Initial release
- Full .is2 support
- Accurate temperature conversion (< 0.5°C difference from Fluke software)
- Metadata extraction
- Fusion offset correction
- Support for Ti300 and Ti480P cameras
- Ready for additional camera model support with user feedback
