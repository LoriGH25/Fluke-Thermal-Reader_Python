#!/usr/bin/env python3
"""
Debug script to plot GH file data and see the differences clearly
"""

import numpy as np
from fluke_thermal_reader import read_is2

# Optional: matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Note: matplotlib not available. Install with: pip install matplotlib")

def load_fluke_txt_data(filename):
    """Load temperature data from Fluke exported txt file."""
    print(f"Loading Fluke data from {filename}...")
    
    # Read the file and skip header lines
    for encoding in ['utf-8', 'utf-16', 'latin-1', 'cp1252']:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                lines = f.readlines()
            print(f"Successfully read file with {encoding} encoding")
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("Could not decode file with any encoding")
    
    # Find where the data starts (skip header)
    data_start = 0
    print(f"Total lines: {len(lines)}")
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped and line_stripped[0].isdigit() and '\t' in line_stripped:
            parts = line_stripped.split('\t')
            if len(parts) > 100:
                if len(parts) > 1:
                    try:
                        second_val = float(parts[1])
                        if '.' in parts[1]:
                            data_start = i
                            print(f"Found data start at line {i}: '{line_stripped[:50]}...'")
                            break
                        else:
                            print(f"Skipping header at line {i}")
                            continue
                    except ValueError:
                        continue
    
    # Extract temperature data
    temp_data = []
    for i, line in enumerate(lines[data_start:]):
        if line.strip():
            values = line.strip().split('\t')[1:]
            row_data = []
            for val in values:
                try:
                    row_data.append(float(val))
                except ValueError:
                    break
            if row_data and len(row_data) >= 240:
                temp_data.append(row_data)
    
    print(f"Loaded {len(temp_data)} rows of temperature data")
    return np.array(temp_data)

def main():
    # Load our parsed data
    print("Loading GH data with our parser...")
    our_data = read_is2("GHtempe2_2429.IS2")
    our_temps = our_data['data']
    
    # Load real Fluke data
    real_data = load_fluke_txt_data("GHtempe2_2429.txt")
    
    print(f"Our data shape: {our_temps.shape}")
    print(f"Real data shape: {real_data.shape}")
    print(f"Our temp range: {our_temps.min():.1f}°C - {our_temps.max():.1f}°C")
    print(f"Real temp range: {real_data.min():.1f}°C - {real_data.max():.1f}°C")
    
    # Create detailed comparison plots (if matplotlib available)
    if not HAS_MATPLOTLIB:
        print("\nMatplotlib not available. Install with: pip install matplotlib")
        print("Data analysis completed without visualization.")
        return
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Our data heatmap
    im1 = axes[0,0].imshow(our_temps, cmap='hot', aspect='auto')
    axes[0,0].set_title('Our Parser Data (GH)')
    axes[0,0].set_xlabel('X (pixels)')
    axes[0,0].set_ylabel('Y (pixels)')
    plt.colorbar(im1, ax=axes[0,0], label='Temperature (°C)')
    
    # Real data heatmap
    im2 = axes[0,1].imshow(real_data, cmap='hot', aspect='auto')
    axes[0,1].set_title('Real Fluke Data (GH)')
    axes[0,1].set_xlabel('X (pixels)')
    axes[0,1].set_ylabel('Y (pixels)')
    plt.colorbar(im2, ax=axes[0,1], label='Temperature (°C)')
    
    # Difference plot
    if our_temps.shape == real_data.shape:
        diff = our_temps - real_data
        im3 = axes[0,2].imshow(diff, cmap='RdBu_r', aspect='auto')
        axes[0,2].set_title('Difference (Our - Real)')
        axes[0,2].set_xlabel('X (pixels)')
        axes[0,2].set_ylabel('Y (pixels)')
        plt.colorbar(im3, ax=axes[0,2], label='Temperature Difference (°C)')
        
        # Histogram of differences
        axes[1,0].hist(diff.flatten(), bins=50, alpha=0.7, edgecolor='black')
        axes[1,0].set_title('Temperature Difference Distribution')
        axes[1,0].set_xlabel('Temperature Difference (°C)')
        axes[1,0].set_ylabel('Frequency')
        axes[1,0].axvline(0, color='red', linestyle='--', alpha=0.7)
        
        # First row comparison
        axes[1,1].plot(our_temps[0, :], 'b-', label='Our data', alpha=0.7)
        axes[1,1].plot(real_data[0, :], 'r-', label='Real data', alpha=0.7)
        axes[1,1].set_title('First Row Comparison')
        axes[1,1].set_xlabel('X (pixels)')
        axes[1,1].set_ylabel('Temperature (°C)')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        # Middle row comparison
        middle_row = our_temps.shape[0] // 2
        axes[1,2].plot(our_temps[middle_row, :], 'b-', label='Our data', alpha=0.7)
        axes[1,2].plot(real_data[middle_row, :], 'r-', label='Real data', alpha=0.7)
        axes[1,2].set_title(f'Middle Row ({middle_row}) Comparison')
        axes[1,2].set_xlabel('X (pixels)')
        axes[1,2].set_ylabel('Temperature (°C)')
        axes[1,2].legend()
        axes[1,2].grid(True, alpha=0.3)
        
        print(f"\nDifference statistics:")
        print(f"Mean difference: {diff.mean():.2f}°C")
        print(f"Std difference: {diff.std():.2f}°C")
        print(f"Max difference: {diff.max():.2f}°C")
        print(f"Min difference: {diff.min():.2f}°C")
        
        # Check for potential shift
        print(f"\nFirst row analysis:")
        print(f"Our first 10 pixels: {our_temps[0, :10]}")
        print(f"Real first 10 pixels: {real_data[0, :10]}")
        print(f"Our last 10 pixels: {our_temps[0, -10:]}")
        print(f"Real last 10 pixels: {real_data[0, -10:]}")
        
    else:
        axes[0,2].text(0.5, 0.5, 'Shape mismatch!', ha='center', va='center', transform=axes[0,2].transAxes)
        axes[1,0].text(0.5, 0.5, 'Cannot compare', ha='center', va='center', transform=axes[1,0].transAxes)
        axes[1,1].text(0.5, 0.5, 'Cannot compare', ha='center', va='center', transform=axes[1,1].transAxes)
        axes[1,2].text(0.5, 0.5, 'Cannot compare', ha='center', va='center', transform=axes[1,2].transAxes)
        print(f"\nShape mismatch: Our {our_temps.shape} vs Real {real_data.shape}")
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
