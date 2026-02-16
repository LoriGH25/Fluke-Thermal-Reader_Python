"""Test IS2 reading with fluke_thermal_reader: print camera model and thermal plot."""
import matplotlib.pyplot as plt
import numpy as np
#import fluke_thermal_reader
from fluke_thermal_reader import read_is2

FILE = "IS2ref/00002.IS2"
#FILE = "IS2ref/CBH_300s.IS2"

data = read_is2(FILE)

# Camera model and info
camera_model = data.get("CameraModel", "?")
print("CameraModel:", camera_model)
print("Size:", data.get("size"))
print("Emissivity:", data.get("Emissivity"))
print("Transmission:", data.get("Transmission"))
print("BackgroundTemp:", data.get("BackgroundTemp"))
if data.get("data") is not None and data["data"].size > 0:
    d = np.asarray(data["data"])
    print("Temp min/max (°C):", float(np.nanmin(d)), "/", float(np.nanmax(d)))
else:
    print("Thermal data: empty or missing")

# Thermal plot
if data.get("data") is not None and data["data"].size > 0:
    fig, ax = plt.subplots()
    im = ax.imshow(data["data"], cmap="jet", aspect="equal")
    ax.set_title(f"Thermal image — {camera_model}")
    plt.colorbar(im, ax=ax, label="Temperature (°C)")
    plt.tight_layout()
    plt.show()
else:
    print("No data to plot.")
