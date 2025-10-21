#!/usr/bin/env python3
"""
Simple usage example for fluke_reader library.
This example only requires numpy (no matplotlib or pandas needed).
"""

from fluke_thermal_reader import read_is2
import numpy as np

def main():
    """Simple usage example without external dependencies."""
    
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
        
        # Image paths (if available)
        if data['thumbnail_path']:
            print(f"\n=== IMAGES ===")
            print(f"Thumbnail path: {data['thumbnail_path']}")
        if data['photo_path']:
            print(f"Photo path: {data['photo_path']}")
        
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
        
        # Temperature statistics by quadrant
        height, width = temperatures.shape
        mid_h, mid_w = height // 2, width // 2
        
        quadrants = {
            'Top-Left': temperatures[:mid_h, :mid_w],
            'Top-Right': temperatures[:mid_h, mid_w:],
            'Bottom-Left': temperatures[mid_h:, :mid_w],
            'Bottom-Right': temperatures[mid_h:, mid_w:]
        }
        
        print(f"\n=== QUADRANT ANALYSIS ===")
        for name, quad in quadrants.items():
            print(f"{name}: {quad.min():.1f}°C - {quad.max():.1f}°C (avg: {quad.mean():.1f}°C)")
        
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        print("Please replace 'thermal_image.is2' with the path to your actual .is2 file.")
    except Exception as e:
        print(f"Error loading thermal data: {e}")

if __name__ == "__main__":
    main()
