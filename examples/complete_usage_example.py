#!/usr/bin/env python3
"""
Complete Usage Example for fluke_thermal_reader

This example demonstrates all the main features of the fluke_thermal_reader package:
- Reading IS2 thermal files
- Extracting metadata and thermal data
- Displaying thermal images
- Accessing all available information

Author: Your Name
Date: 2024
"""

from fluke_thermal_reader import read_is2
import matplotlib.pyplot as plt
import numpy as np
import os

def main():
    """
    Main function demonstrating complete usage of fluke_thermal_reader
    """
    print("🔍 Fluke Thermal Reader - Complete Usage Example")
    print("=" * 60)
    
    # Example file path - replace with your actual IS2 file
    is2_file = "Compressor1.is2"
    
    # Check if file exists
    if not os.path.exists(is2_file):
        print(f"❌ Error: File '{is2_file}' not found!")
        print("Please provide a valid IS2 file path.")
        return
    
    print(f"📁 Loading thermal data from: {is2_file}")
    
    try:
        # Load thermal data from IS2 file
        data = read_is2(is2_file)
        print("✅ File loaded successfully!")
        
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return
    
    # Display basic information
    print_basic_info(data)
    
    # Display camera information
    print_camera_info(data)
    
    # Display temperature statistics
    print_temperature_stats(data)
    
    # Display measurement parameters
    print_measurement_params(data)
    
    # Display temporal information
    print_temporal_info(data)
    
    # Display file paths
    print_file_paths(data)
    
    # Display technical information
    print_technical_info(data)
    
    # Display thermal data statistics
    print_thermal_data_stats(data)
    
    # Display all extracted keys (summary)
    print_all_keys_summary(data)
    
    # Display thermal image
    display_thermal_image(data)
    
    print("\n" + "=" * 60)
    print("✅ Complete usage example finished!")
    print("📚 This example shows all available features of fluke_thermal_reader")

def print_basic_info(data):
    """Print basic file information"""
    print("\n📊 BASIC INFORMATION:")
    print(f"  File Name: {data.get('FileName', 'N/A')}")
    print(f"  Image Size: {data.get('size', 'N/A')}")
    print(f"  IR Resolution: {data.get('IRWidth', 'N/A')}x{data.get('IRHeight', 'N/A')}")
    print(f"  VL Resolution: {data.get('VLWidth', 'N/A')}x{data.get('VLHeight', 'N/A')}")

def print_camera_info(data):
    """Print camera information"""
    print("\n📷 CAMERA INFORMATION:")
    print(f"  Manufacturer: {data.get('CameraManufacturer', 'N/A')}")
    print(f"  Model: {data.get('CameraModel', 'N/A')}")
    print(f"  Serial Number: {data.get('CameraSerial', 'N/A')}")
    print(f"  Engine Serial: {data.get('EngineSerial', 'N/A')}")
    print(f"  IR Lenses: {data.get('IRLenses', 'N/A')}")
    print(f"  IR Lenses Serial: {data.get('IRLensesSerial', 'N/A')}")
    print(f"  Calibration Date: {data.get('CalibrationDate', 'N/A')}")

def print_temperature_stats(data):
    """Print temperature statistics"""
    print("\n🌡️ TEMPERATURE STATISTICS:")
    print(f"  Minimum: {data.get('MinTemp', 'N/A'):.2f}°C")
    print(f"  Maximum: {data.get('MaxTemp', 'N/A'):.2f}°C")
    print(f"  Average: {data.get('AvgTemp', 'N/A'):.2f}°C")
    print(f"  Center: {data.get('CenterTemp', 'N/A'):.2f}°C")
    print(f"  Background: {data.get('BackgroundTemp', 'N/A'):.2f}°C")
    
    # Calculate temperature range
    if 'MinTemp' in data and 'MaxTemp' in data:
        temp_range = data['MaxTemp'] - data['MinTemp']
        print(f"  Range: {temp_range:.2f}°C")

def print_measurement_params(data):
    """Print measurement parameters"""
    print("\n⚙️ MEASUREMENT PARAMETERS:")
    print(f"  Emissivity: {data.get('Emissivity', 'N/A')}")
    print(f"  Background Temperature: {data.get('BackgroundTemp', 'N/A'):.2f}°C")
    print(f"  Transmission: {data.get('Transmission', 'N/A')}")
    print(f"  Range: {data.get('range', 'N/A')}")

def print_temporal_info(data):
    """Print temporal information"""
    print("\n📅 TEMPORAL INFORMATION:")
    print(f"  Capture Date/Time: {data.get('CaptureDateTime', 'N/A')}")
    print(f"  Title: {data.get('Title', 'N/A')}")
    print(f"  Comments: {data.get('Comments', 'N/A')}")

def print_file_paths(data):
    """Print file paths for images"""
    print("\n🖼️ IMAGE FILES:")
    print(f"  Thumbnail Path: {data.get('thumbnail_path', 'N/A')}")
    print(f"  Photo Path: {data.get('photo_path', 'N/A')}")
    
    # Check if files exist
    if data.get('thumbnail_path'):
        exists = "✅" if os.path.exists(data['thumbnail_path']) else "❌"
        print(f"  Thumbnail Exists: {exists}")
    
    if data.get('photo_path'):
        exists = "✅" if os.path.exists(data['photo_path']) else "❌"
        print(f"  Photo Exists: {exists}")

def print_technical_info(data):
    """Print technical information"""
    print("\n🔧 TECHNICAL INFORMATION:")
    print(f"  Contains Annotations: {data.get('ContainsAnnotations', 'N/A')}")
    print(f"  Contains Audio: {data.get('ContainsAudio', 'N/A')}")
    print(f"  Contains CNX Readings: {data.get('ContainsCNXReadings', 'N/A')}")

def print_thermal_data_stats(data):
    """Print thermal data statistics"""
    print("\n📊 THERMAL DATA STATISTICS:")
    if 'data' in data and data['data'].size > 0:
        thermal_data = data['data']
        print(f"  Array Shape: {thermal_data.shape}")
        print(f"  Data Type: {thermal_data.dtype}")
        print(f"  Total Pixels: {thermal_data.size}")
        print(f"  Standard Deviation: {np.std(thermal_data):.2f}°C")
        print(f"  Median: {np.median(thermal_data):.2f}°C")
        print(f"  25th Percentile: {np.percentile(thermal_data, 25):.2f}°C")
        print(f"  75th Percentile: {np.percentile(thermal_data, 75):.2f}°C")
        
        # Hot spots analysis
        mean_temp = np.mean(thermal_data)
        std_dev = np.std(thermal_data)
        hot_spots = thermal_data > (mean_temp + 2 * std_dev)
        hot_spot_count = np.sum(hot_spots)
        hot_spot_percentage = (hot_spot_count / thermal_data.size) * 100
        print(f"  Hot Spots (>2σ): {hot_spot_count} pixels ({hot_spot_percentage:.1f}%)")
    else:
        print("  ❌ No thermal data available")

def print_all_keys_summary(data):
    """Print summary of all extracted keys"""
    print("\n🔍 ALL EXTRACTED DATA KEYS:")
    print(f"  Total keys extracted: {len(data.keys())}")
    
    # Categorize keys
    basic_keys = ['FileName', 'size', 'CaptureDateTime', 'Title', 'Comments']
    camera_keys = [k for k in data.keys() if 'Camera' in k or 'Engine' in k or 'IR' in k or 'VL' in k or 'Calibration' in k]
    temp_keys = [k for k in data.keys() if 'Temp' in k or 'temp' in k]
    param_keys = [k for k in data.keys() if k in ['Emissivity', 'Transmission', 'range', 'emissivity', 'backgroundtemperature']]
    file_keys = [k for k in data.keys() if 'path' in k or 'thumbnail' in k or 'photo' in k]
    data_keys = ['data', 'conversion']
    other_keys = [k for k in data.keys() if k not in basic_keys + camera_keys + temp_keys + param_keys + file_keys + data_keys]
    
    print(f"  📊 Basic Info: {len(basic_keys)} keys")
    print(f"  📷 Camera Info: {len(camera_keys)} keys")
    print(f"  🌡️ Temperature: {len(temp_keys)} keys")
    print(f"  ⚙️ Parameters: {len(param_keys)} keys")
    print(f"  🖼️ Files: {len(file_keys)} keys")
    print(f"  📈 Data Arrays: {len(data_keys)} keys")
    print(f"  🔧 Other: {len(other_keys)} keys")
    
    # Show some example keys from each category
    print("\n  Example keys by category:")
    if camera_keys:
        print(f"    Camera: {camera_keys[:3]}{'...' if len(camera_keys) > 3 else ''}")
    if temp_keys:
        print(f"    Temperature: {temp_keys}")
    if param_keys:
        print(f"    Parameters: {param_keys}")
    if file_keys:
        print(f"    Files: {file_keys}")

def display_thermal_image(data):
    """Display thermal image using matplotlib"""
    print("\n🖼️ DISPLAYING THERMAL IMAGE:")
    
    if 'data' in data and data['data'].size > 0:
        try:
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Main thermal image
            im1 = ax1.imshow(data['data'], cmap='hot', aspect='equal')
            ax1.set_title(f'Thermal Image - {data.get("CameraModel", "Unknown")}')
            ax1.set_xlabel('Width (pixels)')
            ax1.set_ylabel('Height (pixels)')
            
            # Add colorbar
            cbar1 = plt.colorbar(im1, ax=ax1)
            cbar1.set_label('Temperature (°C)')
            
            # Temperature histogram
            thermal_data = data['data']
            ax2.hist(thermal_data.flatten(), bins=50, alpha=0.7, color='red', edgecolor='black')
            ax2.set_title('Temperature Distribution')
            ax2.set_xlabel('Temperature (°C)')
            ax2.set_ylabel('Pixel Count')
            ax2.grid(True, alpha=0.3)
            
            # Add statistics to histogram
            ax2.axvline(thermal_data.mean(), color='blue', linestyle='--', label=f'Mean: {thermal_data.mean():.1f}°C')
            ax2.axvline(thermal_data.min(), color='green', linestyle='--', label=f'Min: {thermal_data.min():.1f}°C')
            ax2.axvline(thermal_data.max(), color='orange', linestyle='--', label=f'Max: {thermal_data.max():.1f}°C')
            ax2.legend()
            
            plt.tight_layout()
            plt.show()
            
            print("✅ Thermal image displayed successfully!")
            
        except Exception as e:
            print(f"❌ Error displaying thermal image: {e}")
    else:
        print("❌ No thermal data available for display")

if __name__ == "__main__":
    main()
