"""Business logic for the application."""

import pandas as pd
from dateutil.relativedelta import relativedelta
from utils.data_utils import fetch_and_update_tarifas

def load_initial_data():
    """Load initial data required for the application."""
    df_tarifas = fetch_and_update_tarifas()
    agentes = pd.read_parquet("DBases/Contatos_Agentes.parquet")["Agente"].tolist()
    return df_tarifas, agentes

def calculate_year_range(start_date, duracao_meses):
    """Calculate the range of years for the contract."""
    end_date = start_date + relativedelta(months=+duracao_meses)
    return list(range(start_date.year, end_date.year + 1))

def get_resolucao_homologatoria(df_tarifas, distribuidora):
    """Get the list of Resolução Homologatória for a given distribuidora."""
    return df_tarifas[df_tarifas["SigAgente"] == distribuidora]["DscREH"].sort_values(ascending=False).unique().tolist()

def process_yearly_prices(produto, years, first_price=None):
    """Process yearly prices based on the selected product type."""
    yearly_data = {}
    
    if produto == "Desconto Garantido":
        yearly_data["Desconto"] = {"Valor": 0.0}  # This should be updated with actual value
    else:
        for year in years:
            yearly_data[year] = {"Preço": first_price if first_price is not None else 263.38}
    
    return yearly_data

def validate_inputs(form_data):
    """Validate the form inputs."""
    errors = []
    
    if not form_data["razao_social"]:
        errors.append("Razão Social é obrigatória")
    
    if form_data["duracao_meses"] < 1:
        errors.append("Duração deve ser maior que 0")
    
    return errors

def generate_proposal(form_data, grid_data, yearly_data, consumption_history):
    """Generate a proposal based on the form data."""
    # This is a placeholder for the actual proposal generation logic
    proposal = {
        "form_data": form_data,
        "grid_data": grid_data,
        "yearly_data": yearly_data,
        "consumption_history": consumption_history
    }
    return proposal 