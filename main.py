import streamlit as st
import pandas as pd
import threading
from dateutil.relativedelta import relativedelta
from modules.data_utils import (
    fetch_and_update_tarifas_background, update_event, fetch_distribuidoras, fetch_res_hom, fetch_contatos_agentes
)                               
from modules.ui_components import (
    render_logos, render_header_inputs,  render_distribuidora_section, render_tax_inputs,
    render_energy_grid, render_yearly_prices,  render_consumption_history, apply_css_spacing
)
from modules.data_utils import setup_logger
from modules.proposal_generator import generate_proposal
import logging

st.set_page_config(layout="wide")

def main():
    print("Hello from apresentacao-energia-livre!")

    # Initialize logger
    logger = setup_logger("Proposal_Generator", level=logging.DEBUG)
    # Define file path
    db_path = "DataBase.db"
    
    # Start background update if not already running
    if 'update_thread' not in st.session_state:
        st.session_state.update_thread = threading.Thread(target=fetch_and_update_tarifas_background)
        st.session_state.update_thread.start()
        st.write("As tarifas estão sendo atualizadas em segundo plano no site da Aneel.")

    print(f"update_event.is_set(): {update_event.is_set()}", flush=True)

    # Check if update is complete and refresh data
    if update_event.is_set():
         st.session_state.Res_Hom = fetch_res_hom(db_path, st.session_state.Distribuidora[0], update_event.is_set())

    if 'Distribuidora' not in st.session_state:
        st.session_state.Distribuidora = fetch_distribuidoras(db_path, update_event.is_set())

    Agentes = fetch_contatos_agentes(db_path)

    # Initialize session state variables
    if "consumption_history" not in st.session_state:
        st.session_state.consumption_history = pd.DataFrame(
            columns=["Month/Year", "Demanda Ponta", "Demanda Fora Ponta", "Demanda Horário Reservado", 
                     "Energia Ponta", "Energia Fora Ponta"],
            data=[["", 0.0, 0.0, 0.0, 0.0, 0.0]]  # Start with one empty row
        )
    
    if "yearly_data" not in st.session_state:
        st.session_state.yearly_data = {}

    desconto = st.session_state.get("desconto", 0.0)

    # Render UI components
    render_logos()
    
    # Render header input section
    agente, produto, gd, irrigante, inicio_operacional = render_header_inputs(Agentes)
    
    # Render company info section
    Razao_Social, Instalacao, fat_ref = render_header_inputs(part=2)
    
    # Render distribuidora section
    distribuidora, duracao_meses, bandeira, subgrupo, modalidade = render_distribuidora_section()
    
    # Fetch resolution homologatoria after distribuidora selection
    if distribuidora:
        st.session_state.Res_Hom = fetch_res_hom(db_path, distribuidora, update_event.is_set())
    
    # Render tax inputs
    resolucao, paseb, cofins, icms, icms_hr, desc_irrig = render_tax_inputs(irrigante)

    # Apply CSS for spacing
    apply_css_spacing()

    # Calculate the year range for yearly prices
    end_date = inicio_operacional + relativedelta(months=+duracao_meses)
    years = list(range(inicio_operacional.year, end_date.year + 1))

    # Split layout into two side-by-side sections
    col1, col2 = st.columns([3, 1])  # 3/4 for energy inputs, 1/4 for yearly prices

    # Render energy grid inputs in left column
    with col1:
        grid_data = render_energy_grid(irrigante, gd)

        # Generate Proposal Button
        if st.button("Gerar Proposta"):
            generate_proposal(
                Instalacao, produto, years, grid_data, gd, irrigante, icms, paseb, cofins, 
                bandeira, icms_hr, desc_irrig, distribuidora, subgrupo, modalidade, 
                resolucao, desconto, Razao_Social, Instalacao, fat_ref, agente, duracao_meses
            )

    # Render yearly prices in right column
    with col2:
        render_yearly_prices(produto, years)
    
    # Render consumption history section
    render_consumption_history()



if __name__ == "__main__":
    main()
