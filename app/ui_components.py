"""UI components for the Streamlit application."""

import streamlit as st
import pandas as pd
from dateutil.relativedelta import relativedelta
from .config import (
    DEFAULT_DURATION_MONTHS, DEFAULT_PASEP, DEFAULT_COFINS, DEFAULT_ICMS,
    DEFAULT_START_DATE, PRODUCT_OPTIONS, BANDEIRA_OPTIONS,
    MODALIDADE_TARIFARIA_OPTIONS, MODALIDADE_TARIFARIA_VERDE_OPTIONS,
    ENERGY_GRID_ROWS, ENERGIA_COMPENSADA_ROW, LAYOUT_CSS
)

def initialize_session_state():
    """Initialize session state variables."""
    if "consumption_history" not in st.session_state:
        st.session_state.consumption_history = pd.DataFrame(
            columns=["Month/Year", "Demanda Ponta", "Demanda Fora Ponta", 
                    "Demanda Horário Reservado", "Energia Ponta", "Energia Fora Ponta"],
            data=[["", 0.0, 0.0, 0.0, 0.0, 0.0]]
        )

def render_header(df_tarifas, agentes):
    """Render the header section of the application."""
    st.set_page_config(layout="wide")
    st.markdown(LAYOUT_CSS, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns([3,2,1,1,1])
    with col1:
        agente = st.selectbox("Agente Vendedor", options=agentes, index=0)
    with col2:
        produto = st.selectbox("Produto", options=PRODUCT_OPTIONS, index=1)
    with col3:
        gd = st.checkbox("G.D.", value=False)
    with col4:
        irrigante = st.checkbox("Irrigante", value=False)
    with col5:
        inicio_operacional = st.date_input("Início Operacional", value=DEFAULT_START_DATE, format="DD/MM/YYYY")
    
    return {
        "agente": agente,
        "produto": produto,
        "gd": gd,
        "irrigante": irrigante,
        "inicio_operacional": inicio_operacional
    }

def render_company_info(df_tarifas):
    """Render company information section."""
    distribuidora = st.selectbox(
        "Distribuidora", 
        options=df_tarifas["SigAgente"].sort_values(ascending=True).unique().tolist(),
        index=df_tarifas["SigAgente"].sort_values(ascending=True).unique().tolist().index("CEMIG-D")
    )
    
    razao_social = st.text_input("Razão Social", value="")
    
    return {
        "distribuidora": distribuidora,
        "razao_social": razao_social
    }

def render_contract_details():
    """Render contract details section."""
    col1, col2, col3, col4, col5 = st.columns([4,1,1,1,1])
    with col1:
        duracao_meses = st.number_input("Duração (Meses)", min_value=1, value=DEFAULT_DURATION_MONTHS)
    with col2:
        bandeira = st.selectbox("Bandeira", options=BANDEIRA_OPTIONS, index=0)
    with col3:
        modalidade_tarifaria = st.selectbox("Subgrupo Tarifário", options=MODALIDADE_TARIFARIA_OPTIONS, index=0)
    with col4:
        modalidade_tarifaria_verde = st.selectbox("Modalidade Tarifária", options=MODALIDADE_TARIFARIA_VERDE_OPTIONS, index=0)
    
    return {
        "duracao_meses": duracao_meses,
        "bandeira": bandeira,
        "modalidade_tarifaria": modalidade_tarifaria,
        "modalidade_tarifaria_verde": modalidade_tarifaria_verde
    }

def render_tax_inputs():
    """Render tax input section."""
    col1, col2, col3, col4 = st.columns([3,1,1,1])
    with col1:
        pasep = st.number_input("PASEP (%)", min_value=0.0, value=DEFAULT_PASEP, format="%.2f")
    with col2:
        cofins = st.number_input("Cofins (%)", min_value=0.0, value=DEFAULT_COFINS, format="%.2f")
    with col3:
        icms = st.number_input("ICMS (%)", min_value=0.0, value=DEFAULT_ICMS, format="%.2f")
    
    return {
        "pasep": pasep,
        "cofins": cofins,
        "icms": icms
    }

def render_energy_grid(irrigante, gd):
    """Render the energy input grid."""
    grid_data = {}
    
    # Data Rows (excluding Energia Compensada)
    for i, row in enumerate(ENERGY_GRID_ROWS):
        num_columns = 3 if irrigante else 2
        cols = st.columns(num_columns)
        for j in range(num_columns):
            with cols[j]:
                grid_data[row[j]] = st.number_input(row[j], min_value=0.0, value=0.0, key=f"{row[j]}_{i}")
    
    # Conditional row for Energia Compensada
    if gd:
        num_columns = 3 if irrigante else 2
        cols = st.columns(num_columns)
        for j in range(num_columns):
            with cols[j]:
                grid_data[ENERGIA_COMPENSADA_ROW[0][j]] = st.number_input(
                    ENERGIA_COMPENSADA_ROW[0][j], 
                    min_value=0.0, 
                    value=0.0, 
                    key=f"{ENERGIA_COMPENSADA_ROW[0][j]}_3"
                )
    
    return grid_data

def render_consumption_history():
    """Render the consumption history section."""
    st.markdown("### Histórico de Consumo")
    with st.expander("Editar Histórico de Consumo", expanded=False):
        edited_df = st.data_editor(
            st.session_state.consumption_history,
            num_rows="dynamic",
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
    
    if not st.session_state.consumption_history.empty and st.checkbox("Mostrar Histórico de Consumo"):
        st.write("Histórico de Consumo:")
        st.dataframe(st.session_state.consumption_history) 