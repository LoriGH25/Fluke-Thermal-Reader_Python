# Fluke Thermal Reader

A Python library for reading and analyzing Fluke thermal imaging files in **.is2** format.

**Package**: `fluke-thermal-reader` · **Import**: `import fluke_thermal_reader` or `from fluke_thermal_reader import read_is2`

---

## Features

- **.is2 reading**: Full parsing of Fluke thermal imaging files (.is2)
- **Temperature conversion**: Raw counts to temperature (°C) with emissivity and reflected background correction (radiative formula)
- **Metadata**: Camera model, dimensions, emissivity, transmission, background temperature, min/max/avg from file and from JSON when present
- **Minimal dependencies**: Only `numpy`
- **Tested and working**: Fluke Ti480P and Ti300

---

## Installation

### From PyPI (when published)

```bash
pip install fluke-thermal-reader
```

### From source (development or local release)

From the repository root:

```bash
pip install -e .
```

Or in non-editable mode:

```bash
pip install .
```

---

## Quick start

```python
from fluke_thermal_reader import read_is2

# Load a .is2 file
data = read_is2("thermal_image.is2")

# Thermal matrix (2D, °C)
thermal_data = data["data"]
print(f"Temperature range: {thermal_data.min():.1f}°C - {thermal_data.max():.1f}°C")

# Metadata
print(f"Camera: {data['CameraModel']}")
print(f"Size: {data['size']}")  # [width, height]
print(f"Emissivity: {data['Emissivity']}")
print(f"Background temperature: {data['BackgroundTemp']}°C")
```

### Plot with matplotlib

```python
import matplotlib.pyplot as plt
from fluke_thermal_reader import read_is2

data = read_is2("thermal_image.is2")
plt.imshow(data["data"], cmap="coolwarm", aspect="equal")
plt.colorbar(label="Temperature (°C)")
plt.title(f"Thermal image — {data['CameraModel']}")
plt.show()
```

---

## Returned data structure (`read_is2`)

| Key               | Type       | Description                          |
|-------------------|------------|--------------------------------------|
| `data`            | 2D ndarray | Temperature in °C per pixel          |
| `FileName`        | str        | File name                            |
| `CameraModel`     | str        | Thermal camera model                 |
| `CameraSerial`    | str        | Serial number                        |
| `size`            | [w, h]     | Image dimensions                     |
| `MinTemp`, `MaxTemp`, `AvgTemp` | float | From file/JSON when present   |
| `Emissivity`      | float      | Emissivity                           |
| `Transmission`    | float      | Transmission                         |
| `BackgroundTemp`  | float      | Background temperature               |
| `thumbnail_path`  | str / None | Thumbnail path (if present)          |
| `photo_path`      | str / None | Visible photo path (if present)      |

---

## Requirements

- Python 3.8+
- `numpy >= 1.20.0`

For visualization: `matplotlib` (optional).

---

## Tested camera models

Tested and working with:

- **Fluke Ti480P**
- **Fluke Ti300**

Other Fluke .is2 files may work; feedback and sample files for additional models are welcome.

---

## Project structure

```
Fluke_Python/
├── fluke_thermal_reader/    # Main package
│   ├── __init__.py
│   ├── reader.py            # read_is2, FlukeReader
│   ├── parsers.py           # IS2 parser
│   ├── utilities.py         # UnitConversion, calc_equation
│   ├── models.py
│   └── cli.py
├── examples/                 # Usage examples
├── tests/                    # Tests
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Development and testing

```bash
# Editable install
pip install -e ".[dev]"

# Run tests
pytest
```

---

## read_is3 (Future Work)

`read_is3(file_path)` is planned for Fluke IS3 (video) files.

- **Current status**: Not implemented — calling it raises `NotImplementedError`.
- **Scope**: Video streams (multiple thermal frames), video-level metadata.
- **Documentation**: The returned data structure will be defined once implementation starts.

If you are interested in IS3 support, please open an issue with sample files and requirements.

---

## License

See the `LICENSE` file in the repository.

---

## Changelog

### 0.2.0
- Stable .is2 parser with temperature conversion (emissivity + background temperature)


### 0.1.x
- Initial release, basic .is2 support
