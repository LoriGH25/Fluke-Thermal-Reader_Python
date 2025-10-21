"""
Interfaccia a riga di comando per FlukeReader.
"""

import argparse
import sys
from pathlib import Path
from .reader import FlukeReader


def main():
    """Funzione principale per l'interfaccia CLI."""
    parser = argparse.ArgumentParser(
        description="Lettore di file termografici Fluke (.is2 e .is3)"
    )
    
    parser.add_argument(
        "file_path",
        help="Percorso del file termografico da leggere"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Mostra informazioni sui dati termografici"
    )
    
    parser.add_argument(
        "--export-csv",
        type=str,
        help="Esporta i dati di temperatura in formato CSV"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Mostra statistiche sui dati di temperatura"
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
            print(f"Dati esportati in: {args.export_csv}")
        
        if not any([args.info, args.stats, args.export_csv]):
            print(f"File caricato con successo: {args.file_path}")
            print(f"Dimensioni immagine: {thermal_image.get_image_shape()}")
            print(f"Temperatura media: {thermal_image.measurement_data.get_average_temperature():.2f}°C")
    
    except Exception as e:
        print(f"Errore: {e}", file=sys.stderr)
        sys.exit(1)


def print_info(thermal_image):
    """Stampa informazioni sui dati termografici."""
    data = thermal_image.measurement_data
    
    print("\n=== INFORMAZIONI TERMOGRAFICHE ===")
    print(f"Timestamp: {data.timestamp}")
    print(f"Modello dispositivo: {data.device_model}")
    print(f"Dimensioni immagine: {thermal_image.get_image_shape()}")
    print(f"Emissività: {data.emissivity}")
    print(f"Distanza: {data.distance}m")
    print(f"Temperatura ambiente: {data.ambient_temperature}°C")
    print(f"Umidità relativa: {data.relative_humidity}%")


def print_stats(thermal_image):
    """Stampa statistiche sui dati di temperatura."""
    data = thermal_image.measurement_data
    temp_min, temp_max = data.get_temperature_range()
    temp_avg = data.get_average_temperature()
    
    print("\n=== STATISTICHE TEMPERATURA ===")
    print(f"Temperatura minima: {temp_min:.2f}°C")
    print(f"Temperatura massima: {temp_max:.2f}°C")
    print(f"Temperatura media: {temp_avg:.2f}°C")
    print(f"Range di temperatura: {temp_max - temp_min:.2f}°C")


def export_to_csv(thermal_image, output_path):
    """Esporta i dati di temperatura in formato CSV."""
    import csv
    import numpy as np
    
    data = thermal_image.measurement_data.temperature_data
    
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow(['X', 'Y', 'Temperature_C'])
        
        # Dati
        for y in range(data.shape[0]):
            for x in range(data.shape[1]):
                writer.writerow([x, y, data[y, x]])


if __name__ == "__main__":
    main()

