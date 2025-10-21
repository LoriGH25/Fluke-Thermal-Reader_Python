#!/usr/bin/env python3
"""
Simple Usage Example for fluke_thermal_reader

This example shows basic usage of the fluke_thermal_reader package:
- Reading IS2 thermal files
- Accessing basic metadata
- Working with thermal data

Author: Your Name
Date: 2024
"""

from fluke_thermal_reader import read_is2
import matplotlib.pyplot as plt

def main():
    """
    Simple example showing basic usage
    """
    print("🔍 Fluke Thermal Reader - Simple Usage Example")
    print("=" * 50)
    
    # Load thermal data from IS2 file
    data = read_is2("Compressor1.is2")
    
    # Basic information
    print(f"📁 File: {data['FileName']}")
    print(f"📷 Camera: {data['CameraModel']} (Serial: {data['CameraSerial']})")
    print(f"📐 Size: {data['size']}")
    
    # Temperature information
    print(f"🌡️ Temperature Range: {data['MinTemp']:.1f}°C - {data['MaxTemp']:.1f}°C")
    print(f"🌡️ Average: {data['AvgTemp']:.1f}°C")
    
    # Measurement parameters
    print(f"⚙️ Emissivity: {data['Emissivity']}")
    print(f"⚙️ Background: {data['BackgroundTemp']:.1f}°C")
    
    # Access thermal data
    thermal_data = data['data']
    print(f"📊 Thermal Data: {thermal_data.shape} array")
    
    # Display thermal image
    plt.figure(figsize=(10, 8))
    plt.imshow(thermal_data, cmap='hot')
    plt.colorbar(label='Temperature (°C)')
    plt.title(f'Thermal Image - {data["CameraModel"]}')
    plt.show()
    
    print("✅ Simple example completed!")

if __name__ == "__main__":
    main()