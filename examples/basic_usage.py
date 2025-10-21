#!/usr/bin/env python3
"""
Basic Usage Example for fluke_thermal_reader

This example shows basic usage of the fluke_thermal_reader package:
- Reading IS2 thermal files
- Accessing basic metadata and thermal data
- Simple visualization with matplotlib

Author: Your Name
Date: 2024
"""

from fluke_thermal_reader import read_is2
import numpy as np

# Optional: matplotlib for visualization (install with: pip install matplotlib)
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Note: matplotlib not available. Install with: pip install matplotlib")

def main():
    """Basic usage example."""
    
    # Example file path (replace with your actual file)
    file_path = "thermal_image.is2"
    
    try:
        # Load thermal data
        print(f"Loading thermal data from {file_path}...")
        data = read_is2(file_path)
        
        # Display basic information
        print(f"\n=== THERMAL IMAGE INFORMATION ===")
        print(f"File: {data['FileName']}")
        print(f"Camera: {data['CameraModel']} (Serial: {data['CameraSerial']})")
        print(f"Image size: {data['size'][0]}x{data['size'][1]} pixels")
        print(f"Capture date: {data['CaptureDateTime']}")
        
        # Temperature information
        temperatures = data['data']
        print(f"\n=== TEMPERATURE INFORMATION ===")
        print(f"Temperature range: {temperatures.min():.1f}°C - {temperatures.max():.1f}°C")
        print(f"Average temperature: {temperatures.mean():.1f}°C")
        print(f"Standard deviation: {temperatures.std():.1f}°C")
        
        # Camera settings
        print(f"\n=== CAMERA SETTINGS ===")
        print(f"Emissivity: {data['Emissivity']}")
        print(f"Background temperature: {data['BackgroundTemp']}°C")
        
        # Display thermal image (if matplotlib is available)
        if HAS_MATPLOTLIB:
            plt.figure(figsize=(12, 8))
            
            # Thermal image
            plt.subplot(1, 2, 1)
            im1 = plt.imshow(temperatures, cmap='hot', aspect='auto')
            plt.title('Thermal Image')
            plt.xlabel('X (pixels)')
            plt.ylabel('Y (pixels)')
            plt.colorbar(im1, label='Temperature (°C)')
            
            # Temperature histogram
            plt.subplot(1, 2, 2)
            plt.hist(temperatures.flatten(), bins=50, alpha=0.7, edgecolor='black')
            plt.title('Temperature Distribution')
            plt.xlabel('Temperature (°C)')
            plt.ylabel('Frequency')
            plt.axvline(temperatures.mean(), color='red', linestyle='--', 
                       label=f'Mean: {temperatures.mean():.1f}°C')
            plt.legend()
            
            plt.tight_layout()
            plt.show()
        else:
            print("\n=== VISUALIZATION ===")
            print("Install matplotlib to see thermal image visualization:")
            print("pip install matplotlib")
        
        # Find hot spots
        hot_threshold = temperatures.mean() + 2 * temperatures.std()
        hot_spots = temperatures > hot_threshold
        hot_count = np.sum(hot_spots)
        
        print(f"\n=== HOT SPOT ANALYSIS ===")
        print(f"Hot spots (> {hot_threshold:.1f}°C): {hot_count} pixels")
        print(f"Hot spot percentage: {100 * hot_count / temperatures.size:.1f}%")
        
        if hot_count > 0:
            hot_temps = temperatures[hot_spots]
            print(f"Hot spot temperature range: {hot_temps.min():.1f}°C - {hot_temps.max():.1f}°C")
        
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        print("Please replace 'thermal_image.is2' with the path to your actual .is2 file.")
    except Exception as e:
        print(f"Error loading thermal data: {e}")

if __name__ == "__main__":
    main()