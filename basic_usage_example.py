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
import tkinter as tk
from tkinter import filedialog

# Optional: matplotlib for visualization (install with: pip install matplotlib)
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Note: matplotlib not available. Install with: pip install matplotlib")

def main():
    """Basic usage example."""
    
    # Seleziona il file .is2 tramite finestra di dialogo
    root = tk.Tk()
    root.withdraw()  # Nasconde la finestra principale
    file_path = filedialog.askopenfilename(
        title="Seleziona il file termico Fluke (.is2)",
        filetypes=[("File Fluke IS2", "*.is2"), ("Tutti i file", "*.*")]
    )
    if not file_path:
        print("Nessun file selezionato. Uscita.")
        return
    
    try:
        # Load thermal data
        print(f"📁 Loading: {file_path}")
        data = read_is2(file_path)
        print("✅ File loaded successfully!")
        
        # Basic information
        print(f"\n📊 BASIC INFO:")
        print(f"  File: {data['FileName']}")
        if 'CameraSerial' in data:
            print(f"  Camera: {data['CameraModel']} (Serial: {data['CameraSerial']})")
        else:
            print(f"  Camera: {data['CameraModel']}")
        print(f"  Size: {data['size']}")
        if 'CaptureDateTime' in data:
            print(f"  Date: {data['CaptureDateTime']}")
        else:
            print(f"  Date: N/A")
        
        # Temperature information
        thermal_data = data['data']
        min_temp = float(thermal_data.min())
        max_temp = float(thermal_data.max())
        min_pos = np.unravel_index(np.argmin(thermal_data), thermal_data.shape)
        max_pos = np.unravel_index(np.argmax(thermal_data), thermal_data.shape)
        print(f"\n🌡️ TEMPERATURE:")
        print(f"  Range: {min_temp:.1f}°C - {max_temp:.1f}°C")
        print(f"  Average: {float(thermal_data.mean()):.1f}°C")
        print(f"  Std Dev: {float(thermal_data.std()):.1f}°C")
        
        # Camera settings
        print(f"\n⚙️ SETTINGS:")
        print(f"  Emissivity: {data['Emissivity']}")
        print(f"  Background: {data['BackgroundTemp']:.1f}°C")
      
        # Display thermal image (if matplotlib is available)
        if HAS_MATPLOTLIB:
            plt.figure(figsize=(8, 6))
            
            # Thermal image
            im1 = plt.imshow(thermal_data, cmap='jet', aspect='auto')
            # Markers for MIN and MAX temperature pixels
            plt.scatter(min_pos[1], min_pos[0], s=60, c='cyan', marker='o',
                        edgecolors='black', label=f"MIN {min_temp:.1f}°C")
            plt.scatter(max_pos[1], max_pos[0], s=60, c='red', marker='o',
                        edgecolors='black', label=f"MAX {max_temp:.1f}°C")
            plt.title('Thermal Image')
            plt.xlabel('X (pixels)')
            plt.ylabel('Y (pixels)')
            plt.colorbar(im1, label='Temperature (°C)')
            plt.legend(loc='best')
            
            plt.tight_layout()
            plt.show()
        else:
            print("\n=== VISUALIZATION ===")
            print("Install matplotlib to see thermal image visualization:")
            print("pip install matplotlib")
        
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        print("Please replace 'thermal_image.is2' with the path to your actual .is2 file.")
    except Exception as e:
        print(f"Error loading thermal data: {e}")

if __name__ == "__main__":
    main()
