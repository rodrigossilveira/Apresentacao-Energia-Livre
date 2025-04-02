import pandas as pd
import sqlite3
import streamlit as st

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
