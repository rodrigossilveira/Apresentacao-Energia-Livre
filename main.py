import streamlit as st
import pandas as pd
import threading
import os
from dateutil.relativedelta import relativedelta
from modules.data_utils import fetch_and_update_tarifas_background, update_event, get_tariffs
from modules.calculations import calcular_fatura_cativa, calcular_fatura_uso, calcular_fatura_livre, gerar_graficos
from modules.pdf_builder import process_page1, process_page5, process_page10, merge_svgs_to_pdf
from modules.ui_components import (
    render_logos, 
    render_header_inputs,
    render_distribuidora_section,
    render_tax_inputs,
    render_energy_grid, 
    render_yearly_prices,
    render_consumption_history,
    apply_css_spacing
)
from modules.db_utils import fetch_distribuidoras, fetch_res_hom, fetch_contatos_agentes

st.set_page_config(layout="wide")

def main():
    print("Hello from apresentacao-energia-livre!")

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
                produto, years, grid_data, irrigante, icms, paseb, cofins, 
                bandeira, icms_hr, desc_irrig, distribuidora, subgrupo, modalidade, 
                resolucao, desconto, Razao_Social, Instalacao, fat_ref, agente, duracao_meses
            )

    # Render yearly prices in right column
    with col2:
        render_yearly_prices(produto, years)
    
    # Render consumption history section
    render_consumption_history()

def generate_proposal(produto, years, grid_data, irrigante, icms, paseb, cofins, 
                     bandeira, icms_hr, desc_irrig, distribuidora, subgrupo, modalidade, 
                     resolucao, desconto, Razao_Social, Instalacao, fat_ref, agente, duracao_meses):
    print(f"produto: {produto}", flush=True)
    print(f"years: {years}", flush=True)
    print(f"st.session_state.yearly_data: {st.session_state.yearly_data}", flush=True)
    
    quantidade = {
        "Demanda HFP": grid_data["Demanda - Fora Ponta"], 
        "Demanda HFP sICMS": grid_data["Demanda s/ ICMS - Fora Ponta"],  
        "Demanda HP": grid_data["Demanda - Ponta"],    
        "Demanda HP sICMS": grid_data["Demanda s/ ICMS - Ponta"],  
        "Demanda HR": grid_data.get("Demanda - Horário Reservado", 0),    
        "Demanda HR sICMS": grid_data.get("Demanda s/ ICMS - Horário Reservado", 0),  
        "Energia HFP": grid_data["Energia Ativa - Fora Ponta"], 
        "Energia HP": grid_data["Energia Ativa - Ponta"],   
        "Energia HR": grid_data.get("Energia Ativa - Horário Reservado", 0),   
        "Energia Compensada HFP": grid_data.get("Energia Compensada - Fora Ponta", 0), 
        "Energia Compensada HP": grid_data.get("Energia Compensada - Ponta", 0) 
    }

    impostos_bandeira = {
        "icms": icms/100,
        "paseb": paseb/100,
        "cofins": cofins/100,
        "bandeira": bandeira,
        "icms_hr": icms_hr,  
        "desc_irr": desc_irrig
    }

    tarifa = get_tariffs(distribuidora, subgrupo, modalidade, resolucao)
    
    preco = {
        "preco": [st.session_state.yearly_data[year]["Preço"] for year in years],
        "produto": produto,
        "anos": years,
        "duracao_meses": duracao_meses,
        "desconto": desconto/100
    }

    # Calculate various invoices
    fatura_cativa = calcular_fatura_cativa(quantidade, tarifa, impostos_bandeira)["Fatura Cativa"]
    fatura_uso = calcular_fatura_uso(quantidade, tarifa, impostos_bandeira)["Fatura de Uso"]
    fatura_livre = calcular_fatura_livre(quantidade, preco, impostos_bandeira, fatura_uso, fatura_cativa)["Fatura Livre"]
    
    # Calculate savings
    economia_mensal = fatura_cativa - fatura_uso - fatura_livre[0]
    economia_anual = economia_mensal * 12
    
    # Debug prints
    print(f"fatura_cativa: {fatura_cativa}", flush=True)
    print(f"fatura_uso: {fatura_uso}", flush=True)
    print(f"fatura_livre: {fatura_livre}", flush=True)
    print(f"economia_mensal: {economia_mensal}", flush=True)
    print(f"economia_anual: {economia_anual}", flush=True)
    
    st.write(fatura_livre)
    desconto = preco["desconto"] if produto == "Desconto Garantido" else economia_mensal/fatura_cativa
    # Generate graphics and process pages
    gerar_graficos(preco, quantidade, tarifa, impostos_bandeira, fatura_uso, fatura_cativa, fatura_livre)
    process_page1(Razao_Social, Instalacao, fat_ref)
    process_page5(economia_mensal, economia_anual, economia_mensal/fatura_cativa, 0.12)
    process_page10(agente)

    # Create PDF from SVGs
    svg_list = [
        'Temp_ppt/page 1.svg',
        'Proposta PPT/page 2.svg', 
        'Proposta PPT/page 3.svg', 
        'Temp_ppt/page 5.svg',
        'Proposta PPT/page 8.svg', 
        'Proposta PPT/page 9.svg', 
        'Temp_ppt/page 10.svg'
    ]

    download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    pdf_path = os.path.join(download_folder, 'Proposta_' + Razao_Social + '_' + Instalacao + '.pdf')
    merge_svgs_to_pdf(svg_list, pdf_path, dpi=300)

    # Open the PDF with the default viewer
    if os.name == "posix":  # macOS/Linux
        os.system(f"open {pdf_path}")  # macOS
        # Use "xdg-open" for Linux: os.system(f"xdg-open {pdf_path}")
    elif os.name == "nt":  # Windows
        os.system(f"start {pdf_path}")

if __name__ == "__main__":
    main()
