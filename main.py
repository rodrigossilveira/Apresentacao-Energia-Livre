def main():
    print("Hello from apresentacao-energia-livre!")

    import streamlit as st
    import pandas as pd
    import requests
    from dateutil.relativedelta import relativedelta
    from utils.data_utils import fetch_and_update_tarifas
    st.set_page_config(layout="wide")

    df_tarifas = fetch_and_update_tarifas()

    Distribuidora = df_tarifas["SigAgente"].sort_values(ascending=True).unique().tolist()

    Agentes = pd.read_parquet(r"DBases/Contatos_Agentes.parquet")["Agente"].tolist()

    if "consumption_history" not in st.session_state:
        st.session_state.consumption_history = None
    
    st.session_state.consumption_history = pd.DataFrame(
            columns=["Month/Year", "Demanda Ponta", "Demanda Fora Ponta", "Demanda Horário Reservado", 
                     "Energia Ponta", "Energia Fora Ponta"],
            data=[["", 0.0, 0.0, 0.0, 0.0, 0.0]]  # Start with one empty row
        )
    

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


    Razao_Social = st.text_input("Razão Social", value="")

    col1, col2, col3, col4, col5 = st.columns([4,1,1,1,1])
    with col1:
        distribuidora = st.selectbox("Distribuidora", options = Distribuidora, index = Distribuidora.index("CEMIG-D"))
    with col2: 
        duracao_meses = st.number_input("Duração (Meses)", min_value=1, value=60)
    with col3:
        bandeira = st.selectbox("Bandeira", options = ["Verde","Amarela", "Vermelha 1", "Vermelha 2"] ,index = 0)
    with col4:
        modalidade_tarifaria = st.selectbox("Subgrupo Tarifário", options=["A4", "A3", "AS", "A2", "A1", "A3a", "B"], index=0)
    with col5:
        modalidade_tarifaria_verde = st.selectbox("Modalidade Tarifária", options=["Verde", "Azul"], index=0)


    Res_Hom = df_tarifas[df_tarifas["SigAgente"] == distribuidora]["DscREH"].sort_values(ascending=False).unique().tolist()

    col1, col2, col3, col4 = st.columns([3,1,1,1])
    with col1:
        resolucao = st.selectbox("Resolução Homologatória", options = Res_Hom, index = 0)
    with col2:
        pasep = st.number_input("PASEP (%)", min_value=0.0, value=0.83, format="%.2f")
    with col3:
        cofins = st.number_input("Cofins (%)", min_value=0.0, value=3.82, format="%.2f")
    with col4:
        icms = st.number_input("ICMS (%)", min_value=0.0, value=18.0, format="%.2f")
        

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

    from dateutil.relativedelta import relativedelta

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
    start_date = inicio_operacional
    end_date = start_date + relativedelta(months=+duracao_meses)
    years = list(range(start_date.year, end_date.year + 1))

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
            st.write("Proposta gerada! (Placeholder for now—add logic later.)")

        # Optional: Display collected grid data for debugging
        if st.checkbox("Mostrar dados da grade"):
            st.write("Dados da grade coletados:")
            st.write(grid_data)
            st.write("Dados de preços anuais coletados:")
            st.write(yearly_data)
    # Right section (1/4 width) for yearly prices
    with col2:
        #st.markdown("### Preços Anuais")
        if produto == "Desconto Garantido":
            desconto = st.number_input("Desconto (%)", min_value=0.0, value=0.0, format="%.2f", key="desconto")
            yearly_data["Desconto"] = {"Valor": desconto}
        else:
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
                yearly_data[year] = {"Preço": preco}

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





if __name__ == "__main__":
    main()
