#!/usr/bin/env python3
"""
Simple function to read Fluke IS2 files.
"""

from fluke_reader.parsers import IS2Parser

def readis2(file_path: str):
    """
    Read a Fluke IS2 file and return all data.
    
    Args:
        file_path: Path to the .is2 file
        
    Returns:
        Dict: Dictionary containing all thermal data and metadata
    """
    parser = IS2Parser()
    return parser.parse(file_path)

if __name__ == "__main__":
    # Test the function
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        data = readis2(file_path)
        print(f"Loaded data for: {data['FileName']}")
        print(f"Camera: {data['CameraModel']} (Serial: {data['CameraSerial']})")
        print(f"Image size: {data['size']}")
        print(f"Temperature range: {data['MinTemp']:.1f}°C - {data['MaxTemp']:.1f}°C")
        print(f"Average temperature: {data['AvgTemp']:.1f}°C")
        print(f"Thermal data shape: {data['data'].shape}")
        print(f"Emissivity: {data['Emissivity']}")
        print(f"Background temperature: {data['BackgroundTemp']:.1f}°C")
    else:
        print("Usage: python readis2.py <file.is2>")
