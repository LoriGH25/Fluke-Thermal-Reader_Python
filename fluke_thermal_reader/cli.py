"""
Command-line interface for FlukeReader.
"""

import argparse
import sys
from pathlib import Path
from .reader import FlukeReader


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Fluke thermal file reader (.is2 and .is3)"
    )

    parser.add_argument(
        "file_path",
        help="Path to the thermal file to read"
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Show thermographic data information"
    )

    parser.add_argument(
        "--export-csv",
        type=str,
        help="Export temperature data to CSV file"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show temperature statistics"
    )

    args = parser.parse_args()

    try:
        reader = FlukeReader()
        thermal_image = reader.read_file(args.file_path)

        if args.info:
            print_info(thermal_image)

        if args.stats:
            print_stats(thermal_image)

        if args.export_csv:
            export_to_csv(thermal_image, args.export_csv)
            print(f"Data exported to: {args.export_csv}")

        if not any([args.info, args.stats, args.export_csv]):
            print(f"File loaded successfully: {args.file_path}")
            print(f"Image size: {thermal_image.get_image_shape()}")
            print(f"Average temperature: {thermal_image.measurement_data.get_average_temperature():.2f}°C")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def print_info(thermal_image):
    """Print thermographic data information."""
    data = thermal_image.measurement_data

    print("\n=== THERMOGRAPHIC INFORMATION ===")
    print(f"Timestamp: {data.timestamp}")
    print(f"Device model: {data.device_model}")
    print(f"Image size: {thermal_image.get_image_shape()}")
    print(f"Emissivity: {data.emissivity}")
    print(f"Distance: {data.distance}m")
    print(f"Ambient temperature: {data.ambient_temperature}°C")
    print(f"Relative humidity: {data.relative_humidity}%")


def print_stats(thermal_image):
    """Print temperature statistics."""
    data = thermal_image.measurement_data
    temp_min, temp_max = data.get_temperature_range()
    temp_avg = data.get_average_temperature()

    print("\n=== TEMPERATURE STATISTICS ===")
    print(f"Minimum temperature: {temp_min:.2f}°C")
    print(f"Maximum temperature: {temp_max:.2f}°C")
    print(f"Average temperature: {temp_avg:.2f}°C")
    print(f"Temperature range: {temp_max - temp_min:.2f}°C")


def export_to_csv(thermal_image, output_path):
    """Export temperature data to CSV format."""
    import csv
    import numpy as np

    data = thermal_image.measurement_data.temperature_data

    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Header
        writer.writerow(['X', 'Y', 'Temperature_C'])

        # Data
        for y in range(data.shape[0]):
            for x in range(data.shape[1]):
                writer.writerow([x, y, data[y, x]])


if __name__ == "__main__":
    main()
