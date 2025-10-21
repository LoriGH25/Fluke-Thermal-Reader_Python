#!/usr/bin/env python3
"""
Example script for fluke_thermal_reader

This script demonstrates basic usage of the fluke_thermal_reader package.
For more comprehensive examples, see the examples/ directory.

Usage:
    python example.py

Make sure to replace "Compressor1.is2" with your actual IS2 file path.
"""

from fluke_thermal_reader import read_is2
import matplotlib.pyplot as plt

def main():
    """Basic example showing thermal data reading and visualization."""
    
    print("🔍 Fluke Thermal Reader - Basic Example")
    print("=" * 50)
    
    # Replace with your actual IS2 file path
    is2_file = "Compressor1.is2"
    
    try:
        # Load thermal data
        print(f"📁 Loading: {is2_file}")
        data = read_is2(is2_file)
        print("✅ File loaded successfully!")
        
        # Basic information
        print(f"\n📊 BASIC INFO:")
        print(f"  File: {data['FileName']}")
        print(f"  Camera: {data['CameraModel']} (Serial: {data['CameraSerial']})")
        print(f"  Size: {data['size']}")
        print(f"  Date: {data['CaptureDateTime']}")
        
        # Temperature information
        thermal_data = data['data']
        print(f"\n🌡️ TEMPERATURE:")
        print(f"  Range: {thermal_data.min():.1f}°C - {thermal_data.max():.1f}°C")
        print(f"  Average: {thermal_data.mean():.1f}°C")
        print(f"  Std Dev: {thermal_data.std():.1f}°C")
        
        # Camera settings
        print(f"\n⚙️ SETTINGS:")
        print(f"  Emissivity: {data['Emissivity']}")
        print(f"  Background: {data['BackgroundTemp']:.1f}°C")
        
        # Display thermal image
        print(f"\n🖼️ DISPLAYING THERMAL IMAGE...")
        plt.figure(figsize=(12, 5))
        
        # Thermal image
        plt.subplot(1, 2, 1)
        plt.imshow(thermal_data, cmap='hot')
        plt.colorbar(label='Temperature (°C)')
        plt.title(f'Thermal Image - {data["CameraModel"]}')
        plt.xlabel('Width (pixels)')
        plt.ylabel('Height (pixels)')
        
        # Temperature histogram
        plt.subplot(1, 2, 2)
        plt.hist(thermal_data.flatten(), bins=50, alpha=0.7, color='red', edgecolor='black')
        plt.title('Temperature Distribution')
        plt.xlabel('Temperature (°C)')
        plt.ylabel('Pixel Count')
        plt.axvline(thermal_data.mean(), color='blue', linestyle='--', 
                   label=f'Mean: {thermal_data.mean():.1f}°C')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        print("✅ Example completed successfully!")
        
    except FileNotFoundError:
        print(f"❌ Error: File '{is2_file}' not found!")
        print("Please replace 'Compressor1.is2' with your actual IS2 file path.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
