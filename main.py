def main():
    print("Hello from apresentacao-energia-livre!")

import streamlit as st


col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    agente = st.text_input("Agente", value="Ferando Madeira")
with col2:
    produto = st.selectbox("Produto", options = ["Desconto Garantido", "Curva de Preço","PMT"], index = 2)
with col3:
    gd = st.checkbox("G.D.", value=False)
with col4:
    irrigante = st.checkbox("Irrigante", value=False)
with col5:
    inicio_operacional = st.date_input("Início Operacional", value="2026-01-01")


distribuidora = st.text_input("Distribuidora", value="CEMIG-D")
resolucao = st.text_input("Resolução Homologatória", value="RESOLUÇÃO HOMOLOGATORIA Nº 3.528, DE 21 DE MAIO DE 2024")


col1, col2, col3, col4 = st.columns(4)
with col1:
    modalidade_tarifaria = st.selectbox("Modalidade Tarifária", options=["A4", "A3", "AS", "A2", "A1", "A3a", "B"], index=0)
with col2:
    modalidade_tarifaria_verde = st.selectbox("Modalidade Tarifária", options=["Verde", "Azul"], index=0)
with col3:
    duracao_meses = st.number_input("Duração (Meses)", min_value=1, value=60)
with col4:
    bandeira = st.selectbox("Bandeira", options = ["Verde","Amarela", "Vermelha 1", "Vermelha 2"] ,index = 0)


col1, col2, col3 = st.columns(3)
with col1:
    demanda_ativa = st.number_input("Demanda Ativa – kW", min_value=0.0, value=317.0)
with col2:
    demanda_ativa_sem_icms = st.number_input("Demanda Ativa (Sem ICMS) – kW", min_value=0.0, value=140.0)
with col3:
    energia_ativa = st.number_input("Energia Ativa – kWh", min_value=0.0, value=14278.0)


col1, col2, col3 = st.columns(3)
with col1:
    pasep = st.number_input("PASEP (%)", min_value=0.0, value=0.83, format="%.2f")
with col2:
    cofins = st.number_input("Cofins (%)", min_value=0.0, value=3.82, format="%.2f")
with col3:
    icms = st.number_input("ICMS (%)", min_value=0.0, value=18.74, format="%.2f")


years = [2026, 2027, 2028, 2029, 2030, 2031]
yearly_data = {}
for year in years:
    col1, col2 = st.columns(2)
    with col1:
        preco = st.number_input(f"Preço R$ ({year})", min_value=0.0, value=263.38, format="%.2f")
    
    yearly_data[year] = {"Preço": preco}

# Generate Proposal Button
if st.button("Gerar Proposta"):
    st.write("Proposta gerada! (Placeholder for now—add logic later.)")

# Display collected data (for debugging)
if st.checkbox("Mostrar dados coletados"):
    st.write("Dados coletados:")
    st.write({
        "Agente": agente,
        "Produto": produto,
        "G.D.": gd,
        "Irrigante": irrigante,
        "Início Operacional": inicio_operacional,
        "Distribuidora": distribuidora,
        "Resolução": resolucao,
        "Modalidade Tarifária": modalidade_tarifaria,
        "Modalidade Tarifária Verde": modalidade_tarifaria_verde,
        "Duração (Meses)": duracao_meses,
        "Bandeira": bandeira,
        "Demanda Ativa (kW)": demanda_ativa,
        "Demanda Ativa Sem ICMS (kW)": demanda_ativa_sem_icms,
        "Energia Ativa (kWh)": energia_ativa,
        "PASEP (%)": pasep,
        "Cofins (%)": cofins,
        "ICMS (%)": icms,
        "Custos Anuais": yearly_data
    })


if __name__ == "__main__":
    main()
