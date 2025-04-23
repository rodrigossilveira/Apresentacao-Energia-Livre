import streamlit as st
import pandas as pd

def render_logos():
    """Render the logo section at the top of the page."""
    cemig_logo = "Images/Verde Claro Logo.png"
    energia_livre_logo = "images/Energia Livre Logo.png"

    # Two columns for logos
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        st.image(cemig_logo, width=150)
    with col3:
        st.image(energia_livre_logo, width=150)

def render_header_inputs(Agentes=None, part=1):
    """Render the header input section with agent, product, and flags."""
    if part == 1:
        col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
        with col1:
            agente = st.selectbox("Agente Vendedor", options=Agentes, index=0)
        with col2:
            produto = st.selectbox("Produto", options=["Desconto Garantido", "Curva de Preço", "PMT"], index=1)
        with col3:
            gd = st.checkbox("G.D.", value=False)
        with col4:
            irrigante = st.checkbox("Irrigante", value=False)
        with col5:
            inicio_operacional = st.date_input("Início Operacional", value="2026-01-01", format="DD/MM/YYYY")
        
        return agente, produto, gd, irrigante, inicio_operacional
    
    elif part == 2:
        # Company information section
        col1, col2, col3 = st.columns([5, 2, 1])
        with col1:
            Razao_Social = st.text_input("Razão Social", value="")
        with col2: 
            Instalacao = st.text_input("Instalação", value="")
        with col3: 
            fat_ref = st.date_input("Fatura de Referência", format="DD/MM/YYYY")
        
        return Razao_Social, Instalacao, fat_ref

def render_distribuidora_section():
    """Render the distribuidora, duration, flag, subgroup, and modality inputs."""
    col1, col2, col3, col4, col5 = st.columns([4, 1, 1, 1, 1])
    with col1:
        distribuidora = st.selectbox(
            "Distribuidora", 
            options=st.session_state.Distribuidora, 
            index=st.session_state.Distribuidora.index("CEMIG-D")
        )
    with col2: 
        duracao_meses = st.number_input("Duração (Meses)", min_value=1, value=60)
    with col3:
        bandeira = st.selectbox("Bandeira", options=["Verde", "Amarela", "Vermelha 1", "Vermelha 2"], index=0)
    with col4:
        subgrupo = st.selectbox("Subgrupo Tarifário", options=["A4", "A3", "AS", "A2", "A1", "A3a", "B"], index=0)
    with col5:
        modalidade = st.selectbox("Modalidade Tarifária", options=["Verde", "Azul"], index=0)
    
    return distribuidora, duracao_meses, bandeira, subgrupo, modalidade

def render_tax_inputs(irrigante):
    """Render the tax input section, conditionally showing irrigante fields."""
    # Define columns based on irrigante condition
    if irrigante:
        col1, col2, col3, col4, col5, col6 = st.columns([4, 1, 1, 1, 1, 1])
    else:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        resolucao = st.selectbox("Resolução Homologatória", options=st.session_state.Res_Hom, index=0)
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
    else: 
        icms_hr, desc_irrig = 0.0, 0.0
    
    return resolucao, paseb, cofins, icms, icms_hr, desc_irrig

def render_energy_grid(irrigante, gd):
    """Render the energy grid inputs section."""
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
            grid_data[energia_compensada_row[0][0]] = st.number_input(
                energia_compensada_row[0][0], min_value=0.0, value=0.0, key=f"{energia_compensada_row[0][0]}_3"
            )
        with cols[1]:
            grid_data[energia_compensada_row[0][1]] = st.number_input(
                energia_compensada_row[0][1], min_value=0.0, value=0.0, key=f"{energia_compensada_row[0][1]}_3"
            )
        if irrigante:
            with cols[2]:
                grid_data[energia_compensada_row[0][2]] = st.number_input(
                    energia_compensada_row[0][2], min_value=0.0, value=0.0, key=f"{energia_compensada_row[0][2]}_3"
                )
    
    return grid_data


def render_yearly_prices(produto, years):
    """Render the yearly prices section."""
    if produto == "Desconto Garantido":
        # Just create the number input widget - Streamlit will automatically
        # update st.session_state.desconto when the user interacts with it
        st.number_input(
            "Desconto (%)", min_value=0.0, value=0.0, format="%.2f", key="desconto"
        )
        # Remove the line: st.session_state.desconto = desconto
    else:
        # Initialize desconto to 0 when not using Desconto Garantido
        # Only do this if we haven't already processed another widget with key="desconto"
        if "desconto" not in st.session_state:
            st.session_state.desconto = 0.0
            
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
            
            if year not in st.session_state.yearly_data:
                st.session_state.yearly_data[year] = {}
            
            st.session_state.yearly_data[year]["Preço"] = preco
            
        if years:
            st.write([st.session_state.yearly_data[year]["Preço"] for year in st.session_state.yearly_data if year in years])


def render_consumption_history():
    """Render the consumption history section."""
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


def apply_css_spacing():
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




