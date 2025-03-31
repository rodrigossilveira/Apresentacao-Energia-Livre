import streamlit as st
import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from modules.data_utils import fetch_and_update_tarifas_background, update_event, get_tariffs
from modules.calculations import calcular_fatura_cativa, calcular_fatura_uso, calcular_fatura_cativa, calcular_fatura_livre, gerar_graficos
from modules.pdf_builder import process_page1, process_page5, process_page10, merge_svgs_to_pdf
import threading
import os
import sqlite3
st.set_page_config(layout="wide")

def main():
    print("Hello from apresentacao-energia-livre!")

    # Define file path
    #tarifas_parquet = r"DBases/tarifas.parquet"
    db_path = "DataBase.db"
    # Start background update if not already running
    if 'update_thread' not in st.session_state:
        st.session_state.update_thread = threading.Thread(target=fetch_and_update_tarifas_background)
        st.session_state.update_thread.start()
        st.write("As tarifas estão sendo atualizadas em segundo plano no site da Aneel.")

    print(f"update_event.is_set(): {update_event.is_set()}", flush=True)

    # Check if update is complete and refresh data
    if update_event.is_set():
        st.session_state.Distribuidora = fetch_distribuidoras(db_path, update_event.is_set())
        st.session_state.Res_Hom = fetch_res_hom(db_path, st.session_state.Distribuidora[0], update_event.is_set())

    if 'Distribuidora' not in st.session_state:
        st.session_state.Distribuidora = fetch_distribuidoras(db_path, update_event.is_set())

    Agentes = fetch_contatos_agentes(db_path)

    if "consumption_history" not in st.session_state:
        st.session_state.consumption_history = None
    
    if "yearly_data" not in st.session_state:
        st.session_state.yearly_data = {}

    st.session_state.consumption_history = pd.DataFrame(
            columns=["Month/Year", "Demanda Ponta", "Demanda Fora Ponta", "Demanda Horário Reservado", 
                     "Energia Ponta", "Energia Fora Ponta"],
            data=[["", 0.0, 0.0, 0.0, 0.0, 0.0]]  # Start with one empty row
        )
    #precos = st.session_state.get([yearly_data[year]["Preço"] for year in yearly_data])
    desconto = st.session_state.get("desconto", 0.0)

    cemig_logo = "Images/Verde Claro Logo.png"
    energia_livre_logo = "images/Energia Livre Logo.png"

    # Two columns for logos
    col1, col2, col3 = st.columns([1,6,1])
    with col1:
        st.image(cemig_logo, width=150)
    with col3:
        st.image(energia_livre_logo, width=150)

    col1, col2, col3, col4, col5 = st.columns([3,2,1,1,1])
    with col1:
        agente = st.selectbox("Agente Vendedor", options = Agentes, index = 0)
    with col2:
        produto = st.selectbox("Produto", options = ["Desconto Garantido", "Curva de Preço","PMT"], index = 1)
    with col3:
        gd = st.checkbox("G.D.", value=False)
    with col4:
        irrigante = st.checkbox("Irrigante", value=False)
    with col5:
        inicio_operacional = st.date_input("Início Operacional", value="2026-01-01", format="DD/MM/YYYY")

    col1, col2, col3 = st.columns([5,2,1])
    with col1:
        Razao_Social = st.text_input("Razão Social", value="")
    with col2: 
        Instalacao = st.text_input("Instalação", value = "")
    with col3: 
        fat_ref = st.date_input("Fatura de Referência", format="DD/MM/YYYY")

    col1, col2, col3, col4, col5 = st.columns([4,1,1,1,1])
    with col1:
        distribuidora = st.selectbox("Distribuidora", options = st.session_state.Distribuidora, index = st.session_state.Distribuidora.index("CEMIG-D"))
        if distribuidora:
            st.session_state.Res_Hom = fetch_res_hom(db_path, distribuidora, update_event.is_set())
    with col2: 
        duracao_meses = st.number_input("Duração (Meses)", min_value=1, value=60)
    with col3:
        bandeira = st.selectbox("Bandeira", options = ["Verde","Amarela", "Vermelha 1", "Vermelha 2"] ,index = 0)
    with col4:
        subgrupo = st.selectbox("Subgrupo Tarifário", options=["A4", "A3", "AS", "A2", "A1", "A3a", "B"], index=0)
    with col5:
        modalidade = st.selectbox("Modalidade Tarifária", options=["Verde", "Azul"], index=0)



    # Define columns based on irrigante condition
    if irrigante:
        col1, col2, col3, col4, col5, col6 = st.columns([4, 1, 1, 1, 1, 1])
    else:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        resolucao = st.selectbox("Resolução Homologatória", options = st.session_state.Res_Hom, index = 0)
    with col2:
        paseb = st.number_input("PASEB (%)", min_value=0.0, value=0.83, format="%.2f")
    with col3:
        cofins = st.number_input("Cofins (%)", min_value=0.0, value=3.82, format="%.2f")
    with col4:
        icms = st.number_input("ICMS (%)", min_value=0.0, value=18.0, format="%.2f")
        # Additional columns only shown when irrigante is true
    if irrigante:
        with col5:
            icms_hr = st.number_input("ICMS HR (%)", min_value=0.0, value=0.0, format="%.2f")
        with col6:
            desc_irrig = st.number_input("Desc Irrig (%)", min_value=0.0, value=0.0, format="%.2f")    
    else: icms_hr, desc_irrig = 0.0, 0.0


    # Inject CSS to reduce vertical spacing and input field width
    st.markdown("""
        <style>
            /* Reduce vertical spacing between rows */
            div[data-testid="stVerticalBlock"] > div {
                margin-bottom: 0px !important;
                padding-bottom: 0px !important;
            }
            div[data-testid="column"] {
                margin-bottom: 0px !important;
                padding-bottom: 0px !important;
            }
            
        </style>
    """, unsafe_allow_html=True)

    # Inject CSS to reduce vertical spacing
    st.markdown("""
        <style>
            /* Reduce vertical spacing between rows */
            div[data-testid="stVerticalBlock"] > div {
                margin-bottom: 0px !important;
                padding-bottom: 0px !important;
            }
            div[data-testid="column"] {
                margin-bottom: 0px !important;
                padding-bottom: 0px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Calculate the year range for yearly prices using relativedelta
    end_date = inicio_operacional + relativedelta(months=+duracao_meses)
    years = list(range(inicio_operacional.year, end_date.year + 1))

    # Define the grid structure with labels in the inputs
    grid_rows = [
        ["Demanda - Ponta", "Demanda - Fora Ponta", "Demanda - Horário Reservado"],
        ["Demanda s/ ICMS - Ponta", "Demanda s/ ICMS - Fora Ponta", "Demanda s/ ICMS - Horário Reservado"],
        ["Energia Ativa - Ponta", "Energia Ativa - Fora Ponta", "Energia Ativa - Horário Reservado"]
    ]
    energia_compensada_row = [
        ["Energia Compensada - Ponta", "Energia Compensada - Fora Ponta", "Energia Compensada - Horário Reservado"]
    ]

    # Store the input values
    grid_data = {}
    yearly_data = {}

    # Split layout into two side-by-side sections
    col1, col2 = st.columns([3, 1])  # 3/4 for energy inputs, 1/4 for yearly prices

    # Left section (3/4 width) for energy inputs
    with col1:
        # Data Rows (excluding Energia Compensada)
        for i, row in enumerate(grid_rows):
            num_columns = 3 if irrigante else 2
            cols = st.columns(num_columns)
            with cols[0]:
                grid_data[row[0]] = st.number_input(row[0], min_value=0.0, value=0.0, key=f"{row[0]}_{i}")
            with cols[1]:
                grid_data[row[1]] = st.number_input(row[1], min_value=0.0, value=0.0, key=f"{row[1]}_{i}")
            if irrigante:
                with cols[2]:
                    grid_data[row[2]] = st.number_input(row[2], min_value=0.0, value=0.0, key=f"{row[2]}_{i}")

        # Conditional row for Energia Compensada
        if gd:
            num_columns = 3 if irrigante else 2
            cols = st.columns(num_columns)
            with cols[0]:
                grid_data[energia_compensada_row[0][0]] = st.number_input(energia_compensada_row[0][0], min_value=0.0, value=0.0, key=f"{energia_compensada_row[0][0]}_3")
            with cols[1]:
                grid_data[energia_compensada_row[0][1]] = st.number_input(energia_compensada_row[0][1], min_value=0.0, value=0.0, key=f"{energia_compensada_row[0][1]}_3")
            if irrigante:
                with cols[2]:
                    grid_data[energia_compensada_row[0][2]] = st.number_input(energia_compensada_row[0][2], min_value=0.0, value=0.0, key=f"{energia_compensada_row[0][2]}_3")

        # Generate Proposal Button
        if st.button("Gerar Proposta"):
            print(f"produto: {produto}",flush=True)
            print(f"years: {years}",flush=True)
            print(f"st.session_state.yearly_data: {st.session_state.yearly_data}",flush=True)
            quantidade = {
                "Demanda HFP": grid_data["Demanda - Fora Ponta"] , 
                "Demanda HFP sICMS": grid_data["Demanda s/ ICMS - Fora Ponta"],  
                "Demanda HP": grid_data["Demanda - Ponta"],    
                "Demanda HP sICMS": grid_data["Demanda s/ ICMS - Ponta"],  
                "Demanda HR": grid_data.get("Demanda - Horário Reservado",0),    
                "Demanda HR sICMS": grid_data.get("Demanda s/ ICMS - Horário Reservado",0),  
                "Energia HFP": grid_data["Energia Ativa - Fora Ponta"], 
                "Energia HP": grid_data["Energia Ativa - Ponta"],   
                "Energia HR": grid_data.get("Energia Ativa - Horário Reservado",0),   
                "Energia Compensada HFP": grid_data.get("Energia Compensada - Fora Ponta",0), 
                "Energia Compensada HP": grid_data.get("Energia Compensada - Ponta",0) 
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

            fatura_cativa = calcular_fatura_cativa(quantidade, tarifa, impostos_bandeira)["Fatura Cativa"]
            fatura_uso = calcular_fatura_uso(quantidade, tarifa, impostos_bandeira)["Fatura de Uso"]
            fatura_livre = calcular_fatura_livre(quantidade, preco, impostos_bandeira, fatura_uso, fatura_cativa)["Fatura Livre"]
            economia_mensal = fatura_cativa - fatura_uso - fatura_livre[0]
            economia_anual = economia_mensal*12
            print(f"fatura_cativa: {fatura_cativa}",flush=True)
            print(f"fatura_uso: {fatura_uso}",flush=True)
            print(f"fatura_livre: {fatura_livre}",flush=True)
            print(f"economia_mensal: {economia_mensal}",flush=True)
            print(f"economia_anual: {economia_anual}",flush=True)
            st.write(fatura_livre)
            #desconto_contratual = 
            gerar_graficos(preco, quantidade, tarifa, impostos_bandeira, fatura_uso, fatura_cativa, fatura_livre )

            process_page1(Razao_Social, Instalacao, fat_ref)
            process_page5(economia_mensal, economia_anual, preco["desconto"], 0.12)
            process_page10(agente)

            svg_list = ['Temp_ppt/page 1.svg','Proposta PPT/page 2.svg', 'Proposta PPT/page 3.svg', '' ,
                        'Proposta PPT/page 8.svg', 'Proposta PPT/page 9.svg', 'Temp_ppt/page 10.svg']

            svg_list[3] = 'Temp_ppt/page 5.svg'

            pdf_path = 'Proposta_' + Razao_Social + '_' + Instalacao + '.pdf'

            merge_svgs_to_pdf(svg_list, pdf_path, dpi= 300)

            # Open the PDF with the default viewer
            if os.name == "posix":  # macOS/Linux
                os.system(f"open {pdf_path}")  # macOS
                # Use "xdg-open" for Linux: os.system(f"xdg-open {pdf_path}")
            elif os.name == "nt":  # Windows
                os.system(f"start {pdf_path}")

            """with open("images/flags_plot.svg", "r", encoding = 'utf-8') as file:
                svg_content = file.read()
            st.markdown(svg_content, unsafe_allow_html=True)"""
            


    # Right section (1/4 width) for yearly prices
    with col2:
        #st.markdown("### Preços Anuais")
        if produto == "Desconto Garantido":
            desconto = st.number_input("Desconto (%)", min_value=0.0, value=0.0, format="%.2f", key="desconto")
            yearly_data["Desconto"] = {"Valor": st.session_state.desconto}
        else:
            desconto = 0.0 # Assign a default value for desconto when not "Desconto Garantido"
            first_price = None
            for i, year in enumerate(years):
                preco = st.number_input(
                    f"Preço R$ ({year})",
                    min_value=0.0,
                    value=263.38 if i == 0 else first_price if first_price is not None else 263.38,
                    format="%.2f",
                    key=f"preco_{year}",
                    disabled=(produto == "PMT" and i > 0)
                )
                if i == 0:
                    first_price = preco  # Store the first price to propagate to subsequent years
                st.session_state.yearly_data[year] = {"Preço": preco}
                st.write([st.session_state.yearly_data[year]["Preço"] for year in st.session_state.yearly_data])
    #-------------------------------------------------------------------------------------------------------------
    st.markdown("### Histórico de Consumo")
    with st.expander("Editar Histórico de Consumo", expanded=False):
            # Display the editable table
            edited_df = st.data_editor(
                st.session_state.consumption_history,
                num_rows="dynamic",  # Allow adding/removing rows
                column_config={
                    "Month/Year": st.column_config.TextColumn("Mês/Ano", width="medium"),
                    "Demanda Ponta": st.column_config.NumberColumn("Demanda Ponta", min_value=0.0, format="%.1f"),
                    "Demanda Fora Ponta": st.column_config.NumberColumn("Demanda Fora Ponta", min_value=0.0, format="%.1f"),
                    "Demanda Horário Reservado": st.column_config.NumberColumn("Demanda Horário Reservado", min_value=0.0, format="%.1f"),
                    "Energia Ponta": st.column_config.NumberColumn("Energia Ponta", min_value=0.0, format="%.1f"),
                    "Energia Fora Ponta": st.column_config.NumberColumn("Energia Fora Ponta", min_value=0.0, format="%.1f"),
                },
                use_container_width=True,
                key="consumption_editor"
            )
            if st.button("Salvar Histórico", key="save_history"):
                st.session_state.consumption_history = edited_df
                st.success("Histórico de consumo salvo com sucesso!")

        # Display the saved consumption history (optional, for debugging)
    if not st.session_state.consumption_history.empty and st.checkbox("Mostrar Histórico de Consumo"):
            st.write("Histórico de Consumo:")
            st.dataframe(st.session_state.consumption_history)
@st.cache_data
def load_tarifas(_db_path):
    conn = sqlite3.connect(_db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM ANEEL_DB", conn)
        return df if not df.empty else None
    finally:
        conn.close()
        return None  # Return None if table doesn’t exist or is empty
    
@st.cache_data
def fetch_distribuidoras(_db_path, _update_event_status):
    conn = sqlite3.connect(_db_path)
    try:
        distribuidoras = pd.read_sql_query("SELECT DISTINCT SigAgente FROM ANEEL_DB ORDER BY SigAgente ASC", conn)
        return distribuidoras["SigAgente"].tolist() if not distribuidoras.empty else []
    finally:
        conn.close()

@st.cache_data
def fetch_res_hom(_db_path, distribuidora, _update_event_status):
    conn = sqlite3.connect(_db_path)
    try:
        query = "SELECT DISTINCT DscREH FROM ANEEL_DB WHERE SigAgente = ? ORDER BY DscREH DESC"
        res_hom = pd.read_sql_query(query, conn, params=(distribuidora,))
        return res_hom["DscREH"].tolist() if not res_hom.empty else []
    finally:
        conn.close()

@st.cache_data
def fetch_contatos_agentes(_db_path):
    conn = sqlite3.connect(_db_path)
    try:
        query = "SELECT DISTINCT Agente FROM Contatos_Agentes ORDER BY Agente ASC"
        contatos_agentes = pd.read_sql_query(query, conn)
        return contatos_agentes["Agente"].tolist() if not contatos_agentes.empty else []
    finally:
        conn.close()


if __name__ == "__main__":
    main()
