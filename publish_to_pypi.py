#!/usr/bin/env python3
"""
Script per pubblicare il pacchetto su PyPI.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Esegue un comando e gestisce gli errori."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completato con successo")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore durante {description}:")
        print(f"   Comando: {command}")
        print(f"   Codice di uscita: {e.returncode}")
        if e.stdout:
            print(f"   STDOUT: {e.stdout}")
        if e.stderr:
            print(f"   STDERR: {e.stderr}")
        return False


def main():
    """Funzione principale per la pubblicazione."""
    print("🚀 Pubblicazione di FlukeReader su PyPI")
    print("=" * 50)
    
    # Verifica che siamo nella directory corretta
    if not Path("pyproject.toml").exists():
        print("❌ File pyproject.toml non trovato. Assicurati di essere nella directory del progetto.")
        sys.exit(1)
    
    # Verifica che i file necessari esistano
    required_files = ["README.md", "requirements.txt"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ File {file} non trovato")
            sys.exit(1)
    
    # Verifica che la directory fluke_thermal_reader esista
    if not Path("fluke_thermal_reader").exists():
        print("❌ Directory fluke_thermal_reader non trovata")
        sys.exit(1)
    
    print("✅ Tutti i file necessari sono presenti")
    
    # Pulisce i build precedenti
    if not run_command("if exist build rmdir /s /q build && if exist dist rmdir /s /q dist && if exist *.egg-info rmdir /s /q *.egg-info", "Pulizia build precedenti"):
        print("⚠️  Avviso: Non è stato possibile pulire i build precedenti")
    
    # Installa le dipendenze di build
    if not run_command("pip install build twine", "Installazione dipendenze di build"):
        sys.exit(1)
    
    # Costruisce il pacchetto
    if not run_command("python -m build", "Costruzione del pacchetto"):
        sys.exit(1)
    
    # Verifica il pacchetto
    if not run_command("twine check dist/*", "Verifica del pacchetto"):
        sys.exit(1)
    
    print("\n📦 Pacchetto pronto per la pubblicazione!")
    print("\nPer pubblicare su PyPI, esegui:")
    print("   twine upload dist/*")
    print("\nPer pubblicare su Test PyPI (per test), esegui:")
    print("   twine upload --repository testpypi dist/*")
    
    # Chiedi conferma per la pubblicazione
    response = input("\nVuoi pubblicare su PyPI ora? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        # Chiedi il token PyPI all'utente per sicurezza
        print("\n🔐 Per sicurezza, inserisci il tuo token PyPI:")
        pypi_token = input("Token PyPI: ").strip()
        if not pypi_token:
            print("❌ Token PyPI richiesto per la pubblicazione")
            sys.exit(1)
        upload_command = f"twine upload --username __token__ --password {pypi_token} dist/*"
        if not run_command(upload_command, "Pubblicazione su PyPI"):
            sys.exit(1)
        print("\n🎉 Pacchetto pubblicato con successo su PyPI!")
    else:
        print("\n📦 Pacchetto pronto per la pubblicazione manuale.")


if __name__ == "__main__":
    main()

