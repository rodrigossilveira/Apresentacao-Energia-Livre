import pandas as pd
import requests
import os
from datetime import datetime, date
import threading
import tempfile
import shutil
from io import StringIO
import sqlite3
import streamlit as st

update_event = threading.Event()  # Initially unset (False)

def fetch_and_update_tarifas_background():

    print("Thread started...", flush=True)
    # Define file paths
    #tarifas_csv = r"DBases/tarifas.csv"
    tarifas_parquet = r"DBases/tarifas.parquet"
    last_updated_file = r"DBases/last_updated.txt"
    db_path = r"DataBase.db"

    # Check if last updated date exists
    last_updated = None
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS last_updated_date (
                    key TEXT PRIMARY KEY,
                    value TEXT
                    )
                   """
                )    

    # Check for the last update date
    cursor.execute("SELECT value FROM last_updated_date WHERE key = 'last_updated'")
    result = cursor.fetchone()
    if result:
        last_updated = datetime.strptime(result[0], "%d-%m-%Y").date()
        print(f"Last updated: {last_updated}, Today: {date.today()}")
    conn.close()

    # Update only if last_updated is None or older than today
    if last_updated is None or last_updated < date.today():
        try:
            # Fetch the CSV from the ANEEL API
            url = "https://dadosabertos.aneel.gov.br/dataset/5a583f3e-1646-4f67-bf0f-69db4203e89e/resource/fcf2906c-7c32-4b9b-a637-054e7a5234f4/download/tarifas-homologadas-distribuidoras-energia-eletrica.csv"
            response = requests.get(url, stream=True)
            response.raise_for_status()
            df_tarifas = pd.read_csv(StringIO(response.content.decode("windows-1252")), delimiter=";")
            df_tarifas = preprocess_tarifas(df_tarifas)

            # Connect to the database and update the ANEEL_DB table
            conn = sqlite3.connect(db_path)
            try:
                # Replace the existing data in ANEEL_DB (drop and recreate for simplicity)
                df_tarifas.to_sql('ANEEL_DB', conn, if_exists='replace', index=False)
            except Exception as e:
                print(f"Database write failed: {e}")
                raise  # Re-raise to trigger cleanup in the except block
            finally:
                conn.close()

            # Update the last_updated value in the metadata table
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO last_updated_date (key, value)
                VALUES ('last_updated', ?)
            """, (date.today().strftime("%d-%m-%Y"),))
            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Update failed: {e}")
            update_event.set()  # Still signal completion on failure
            return

        update_event.set()  # Signal completion
        print("Thread finished, UPDATE_COMPLETE set to True", flush=True)
    print("update runned", flush=True)

def preprocess_tarifas(df):

    replacements = {
        "ETO": "Energisa Tocantins",
        "CERON": "Energisa Rondônia",
        "EPB": "Energisa Paraíba",
        "ESE": "Energisa Sergipe",
        "EMT": "Energisa Mato Grosso",
        "EMS": "Energia Mato Grosso do Sul",
        "ESS": "Energisa Sul Sudeste - ESS",
        "EMR": "Energisa Minas Rio",
        "ELETROPAULO": "ENEL SP",
        "ENF": "Energisa Nova Friburgo",
        "AME": "AME - Amazonas Energia",
        "CEA": "Equatorial Amapá - CEA",
        "CPFL-PIRATINING": "CPFL-PIRATININGA",
        "ERO": "Energisa Rondônia - ERO",
        "EAC": "Energisa Acre - EAC",
        "Neoenergia PE": "Neoenergia Pernambuco",
    }

    type_dict = {
        "DatGeracaoConjuntoDados": "datetime64[ns]",
        "DscREH": "string",
        "SigAgente": "string",
        "NumCNPJDistribuidora": "Int64",
        "DatInicioVigencia": "datetime64[ns]",
        "DatFimVigencia": "datetime64[ns]",
        "DscBaseTarifaria": "string",
        "DscSubGrupo": "string",
        "DscModalidadeTarifaria": "string",
        "DscDetalhe": "string",
        "NomPostoTarifario": "string",
        "DscUnidadeTerciaria": "string",
        "SigAgenteAcessante": "string",
    }

    df['VlrTE'] = df['VlrTE'].str.replace(',00', '0,00').str.replace(',','.').astype(float)
    df['VlrTUSD'] = df['VlrTUSD'].str.replace(',00', '0,00').str.replace(',','.').astype(float)
    df["NomPostoTarifario"] = df["NomPostoTarifario"].replace("Não se aplica", "Fora ponta")
    df = df.drop(columns=["DscClasse", "DscSubClasse"])
    df = df[
        (df["DscDetalhe"] == "Não se aplica") &
        (df["DscBaseTarifaria"] == "Tarifa de Aplicação") &
        (df["SigAgenteAcessante"] == "Não se aplica") &
        df["DscModalidadeTarifaria"].isin(["Azul", "Verde"])
    ]
    df = df.astype(type_dict)
    df["SigAgente"] = df["SigAgente"].replace(replacements)
    df = df.sort_values(by="DatInicioVigencia", ascending=False)
    
    return df

def get_tariffs(distribuidora, subgrupo, modalidade, resolucao):
    """
    Get the tariffs for a given combination of filters.
    
    Args:
        distribuidora (str): The distributor filter.
        subgrupo (str): The subgroup filter.
        modalidade (str): The tariff modality filter.
        resolucao (str): The resolution filter.
    
    Returns:
        dict: A dictionary containing the computed tariff components.
    """
    # Filter the data based on the provided criteria

    conn = sqlite3.connect("DataBase.db")
    query = f"SELECT * FROM ANEEL_DB WHERE SigAgente = '{distribuidora}' AND DscSubGrupo = '{subgrupo}' AND DscModalidadeTarifaria = '{modalidade}' AND DscREH = '{resolucao}'"
    try:
        filtered_df = pd.read_sql_query(query, conn)
    finally: conn.close()

    # Initialize the tariffs dictionary with default values
    tariffs = {
        "Demanda_HFP": 0,
        "Demanda_HP": 0,
        "Consumo_HFP_TE": 0,
        "Consumo_HFP_TUSD": 0,
        "Consumo_HFP": 0,
        "Consumo_HP_TE": 0,
        "Consumo_HP_TUSD": 0,
        "Consumo_HP": 0
    }

    # Helper function to safely extract a single value
    def get_single_value(sub_df, column):
        if not sub_df.empty:
            return sub_df.iloc[0][column]
        return 0

    # Calculate each tariff component
    tariffs["Demanda_HFP"] = get_single_value(
        filtered_df[
            (filtered_df['DscUnidadeTerciaria'] == 'kW') &
            (filtered_df['NomPostoTarifario'] == 'Fora ponta')
        ],
        'VlrTUSD'
    )

    tariffs["Demanda_HP"] = get_single_value(
        filtered_df[
            (filtered_df['DscUnidadeTerciaria'] == 'kW') &
            (filtered_df['NomPostoTarifario'] == 'Ponta')
        ],
        'VlrTUSD'
    )

    tariffs["Consumo_HFP_TE"] = get_single_value(
        filtered_df[
            (filtered_df['DscUnidadeTerciaria'] == 'MWh') &
            (filtered_df['NomPostoTarifario'] == 'Fora ponta')
        ],
        'VlrTE'
    )/1000

    tariffs["Consumo_HFP_TUSD"] = get_single_value(
        filtered_df[
            (filtered_df['DscUnidadeTerciaria'] == 'MWh') &
            (filtered_df['NomPostoTarifario'] == 'Fora ponta')
        ],
        'VlrTUSD'
    )/1000

    tariffs["Consumo_HP_TE"] = get_single_value(
        filtered_df[
            (filtered_df['DscUnidadeTerciaria'] == 'MWh') &
            (filtered_df['NomPostoTarifario'] == 'Ponta')
        ],
        'VlrTE'
    )/1000

    tariffs["Consumo_HP_TUSD"] = get_single_value(
        filtered_df[
            (filtered_df['DscUnidadeTerciaria'] == 'MWh') &
            (filtered_df['NomPostoTarifario'] == 'Ponta')
        ],
        'VlrTUSD'
    )/1000

    # Calculate total consumption values
    tariffs["Consumo_HFP"] = tariffs["Consumo_HFP_TE"] + tariffs["Consumo_HFP_TUSD"]
    tariffs["Consumo_HP"] = tariffs["Consumo_HP_TE"] + tariffs["Consumo_HP_TUSD"]

    return tariffs

def get_flags():
    """def get_flags():
    conn = sqlite3.connect("DataBase.db")
    query = f"SELECT * FROM tariff_flags"
    try:
        flags = pd.read_sql_query(query, conn).to_dict(orient='records')[0]
    finally:
        conn.close()
    return flags
    """
    conn = sqlite3.connect("DataBase.db")
    query = f"SELECT * FROM tariff_flags"
    try:
        flags = pd.read_sql_query(query, conn).to_dict(orient='records')[0]
    finally:
        conn.close()
    return flags

@st.cache_data
def load_tarifas(db_path):
    """Load tariffs from the database."""
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM ANEEL_DB", conn)
        return df if not df.empty else None
    finally:
        conn.close()
        return None  # Return None if table doesn't exist or is empty
    
@st.cache_data
def fetch_distribuidoras(db_path, update_event_status):
    """Fetch list of distribuidoras from the database."""
    conn = sqlite3.connect(db_path)
    try:
        distribuidoras = pd.read_sql_query("SELECT DISTINCT SigAgente FROM ANEEL_DB ORDER BY SigAgente ASC", conn)
        return distribuidoras["SigAgente"].tolist() if not distribuidoras.empty else []
    finally:
        conn.close()

@st.cache_data
def fetch_res_hom(db_path, distribuidora, update_event_status):
    """Fetch resolution homologatoria options for a given distribuidora."""
    conn = sqlite3.connect(db_path)
    try:
        query = "SELECT DISTINCT DscREH FROM ANEEL_DB WHERE SigAgente = ? ORDER BY DscREH DESC"
        res_hom = pd.read_sql_query(query, conn, params=(distribuidora,))
        return res_hom["DscREH"].tolist() if not res_hom.empty else []
    finally:
        conn.close()

@st.cache_data
def fetch_contatos_agentes(db_path):
    """Fetch agent contacts from the database."""
    conn = sqlite3.connect(db_path)
    try:
        query = "SELECT DISTINCT Agente FROM Contatos_Agentes ORDER BY Agente ASC"
        contatos_agentes = pd.read_sql_query(query, conn)
        return contatos_agentes["Agente"].tolist() if not contatos_agentes.empty else []
    finally:
        conn.close()

@st.cache_data
def fetch_agent_contact_info(agente, db_path="DataBase.db"):
    """
    Fetch the email and phone number of an agent from the database.

    Args:
        agente (str): The agent's name to query.
        db_path (str): Path to the SQLite database.

    Returns:
        dict: A dictionary containing the agent's email and phone, or None if not found.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            query = """
            SELECT "e-mail", telefone 
            FROM Contatos_Agentes 
            WHERE agente = ?
            """
            df = pd.read_sql_query(query, conn, params=(agente,))
            
            if df.empty:
                print(f"No results found for agent '{agente}' in the database.")
                return None
            
            # Return the first row as a dictionary
            return {"email": df.iloc[0]["e-mail"], "phone": df.iloc[0]["telefone"]}
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None



