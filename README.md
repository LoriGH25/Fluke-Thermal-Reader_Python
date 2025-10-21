# Fluke Thermal Reader

A Python library for reading and analyzing Fluke thermal files (.is2 and .is3 formats).

**Package**: `fluke_thermal_reader` | **Import**: `import fluke_thermal_reader`

## Features

- **Complete .is2 support**: Parse Fluke .is2 thermal imaging files
- **Accurate temperature conversion**: Convert raw thermal data to temperature values with high precision
- **Metadata extraction**: Extract camera information, calibration data, and image properties
- **Fusion offset correction**: Automatic correction for horizontal shift in thermal images
- **Lightweight design**: Minimal dependencies (only numpy required)
- **Optional image loading**: Images are returned as paths, not loaded automatically
- **Tested camera models**: Ti300 and Ti480P (other models supported with user feedback)

## Installation

```bash
pip install fluke_thermal_reader
```

**Important**: package name and import are identical: `fluke_thermal_reader`.

## Quick Start

```python
from fluke_thermal_reader import read_is2

# Load a Fluke .is2 file
data = read_is2("thermal_image.is2")

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

- **IS2 (images)**: Fluke thermal image format — FULLY SUPPORTED
- **IS3 (video)**: Fluke thermal video format — FUTURE WORK (not implemented yet)

All the examples and usage below refer to IS2 image files only.

## Image Handling

The library is designed to be lightweight and efficient. Images (thumbnails and visible photos) are handled as follows:

- **Paths only**: Images are returned as file paths, not loaded automatically
- **Optional loading**: You choose when and how to load images
- **Memory efficient**: No automatic image loading saves memory
- **Flexible**: Use any image library you prefer (matplotlib, PIL, opencv, etc.)

```python
# Images are returned as paths
data = read_is2("thermal_image.is2")
print(f"Thumbnail path: {data['thumbnail_path']}")
print(f"Photo path: {data['photo_path']}")

# Load images only when needed
if data['thumbnail_path']:
    # Option 1: Using matplotlib
    import matplotlib.pyplot as plt
    thumbnail = plt.imread(data['thumbnail_path'])
    
    # Option 2: Using PIL (lighter)
    from PIL import Image
    thumbnail = Image.open(data['thumbnail_path'])
```

## Tested Camera Models

- **Ti300**: Fully tested and supported
- **Ti480P**: Fully tested and supported

**Other Fluke camera models**: If you have files from other Fluke thermal cameras, please share them so we can add support for additional models.

## API Reference

### `read_is2(file_path)`

Load and parse a Fluke thermal .is2 file.

**Parameters:**
- `file_path` (str): Path to the .is2 file

**Returns:**
- `dict`: Dictionary containing thermal data and metadata


**Returned Data Structure (read_is2):**
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
    'thumbnail_path': str,          # Path to thumbnail image (if available)
    'photo_path': str,              # Path to visible light image (if available)
}
```

## Examples

### Simple Usage (No External Dependencies)

```python
from fluke_thermal_reader import read_is2
import numpy as np

# Load thermal data
data = read_is2("thermal_image.is2")

# Basic analysis
temperatures = data['data']
print(f"Temperature range: {temperatures.min():.1f}°C - {temperatures.max():.1f}°C")
print(f"Average: {temperatures.mean():.1f}°C")

# Hot spot analysis
hot_spots = temperatures > (temperatures.mean() + 2 * temperatures.std())
print(f"Hot spots: {np.sum(hot_spots)} pixels")
```

### Basic Usage (With Visualization)

```python
from fluke_thermal_reader import read_is2
import matplotlib.pyplot as plt

# Load thermal data
data = read_is2("thermal_image.is2")

# Display thermal image
plt.imshow(data['data'], cmap='hot')
plt.colorbar(label='Temperature (°C)')
plt.title(f'Thermal Image - {data["CameraModel"]}')
plt.show()

# Load images separately if needed (optional)
if data['thumbnail_path']:
    # Using matplotlib (requires matplotlib)
    thumbnail = plt.imread(data['thumbnail_path'])
    plt.figure()
    plt.imshow(thumbnail)
    plt.title('Thumbnail')
    plt.show()
    
    # Or using PIL (lighter alternative)
    # from PIL import Image
    # thumbnail = Image.open(data['thumbnail_path'])
    # thumbnail.show()
```

### Batch Processing

```python
import os
from fluke_thermal_reader import read_is2

# Process multiple files
for filename in os.listdir("thermal_images/"):
    if filename.endswith(".is2"):
        data = read_is2(f"thermal_images/{filename}")
        print(f"Processed {filename}: {data['MinTemp']:.1f}°C - {data['MaxTemp']:.1f}°C")
```

### Temperature Analysis

```python
import numpy as np
from fluke_thermal_reader import read_is2

# Load data
data = read_is2("thermal_image.is2")
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

- Python 3.8+
- numpy>=1.20.0

**Optional dependencies for visualization:**
- matplotlib (for plotting thermal data)
- PIL/Pillow (for loading images)

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
python -m pytest --cov=fluke_thermal_reader
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

---

## read_is3 (Future Work)

`read_is3(file_path)` is planned for Fluke IS3 (video) files.

- Current status: Not implemented — calling it raises `NotImplementedError`.
- Scope: video streams (multiple thermal frames), video-level metadata.
- Documentation: the returned data structure will be defined once implementation starts.

If you are interested in IS3 support, please open an issue with sample files and requirements.
