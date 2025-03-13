import pandas as pd
import requests
import os
from datetime import datetime, date

def fetch_and_update_tarifas():
    # Define file paths
    tarifas_csv = r"DBases/tarifas.csv"
    tarifas_parquet = r"DBases/tarifas.parquet"
    last_updated_file = r"DBases/last_updated.txt"

    # Check if last updated date exists
    last_updated = None
    if os.path.exists(last_updated_file):
        with open(last_updated_file, "r") as f:
            last_updated = datetime.strptime(f.read().strip(), "%d-%m-%Y").date()

    # Update only if last_updated is None or older than today
    if last_updated is None or last_updated < date.today():
        # Fetch the CSV from the ANEEL API
        url = "https://dadosabertos.aneel.gov.br/dataset/5a583f3e-1646-4f67-bf0f-69db4203e89e/resource/fcf2906c-7c32-4b9b-a637-054e7a5234f4/download/tarifas-homologadas-distribuidoras-energia-eletrica.csv"
        response = requests.get(url)

        # Save the CSV locally
        with open(tarifas_csv, "wb") as f:
            f.write(response.content)

        # Read the CSV with semicolon delimiter and Windows-1252 encoding
        df_tarifas = pd.read_csv(tarifas_csv, delimiter=";", encoding="windows-1252")

        # Save as Parquet
        df_tarifas.to_parquet(tarifas_parquet, index=False)

        # Update last updated date
        with open(last_updated_file, "w") as f:
            f.write(date.today().strftime("%d-%m-%Y"))

    # Return the DataFrame (for use in main.py if needed)
    return pd.read_parquet(tarifas_parquet)