
from modules.calculations import (
    prepare_quantidade, prepare_impostos_bandeira, calcular_fatura_cativa,
    calcular_fatura_uso, calcular_fatura_livre, gerar_graficos
)
from modules.pdf_builder import process_page1, process_page5, process_page10, generate_pdf, open_pdf
from modules.data_utils import get_tariffs
import os
import streamlit as st


def generate_proposal(produto, years, grid_data, irrigante, icms, paseb, cofins, 
                     bandeira, icms_hr, desc_irrig, distribuidora, subgrupo, modalidade, 
                     resolucao, desconto, Razao_Social, Instalacao, fat_ref, agente, duracao_meses):
    print(f"produto: {produto}", flush=True)
    print(f"years: {years}", flush=True)
    print(f"st.session_state.yearly_data: {st.session_state.yearly_data}", flush=True)
    
    quantidade = prepare_quantidade(grid_data)

    impostos_bandeira = prepare_impostos_bandeira(icms, paseb, cofins, bandeira, icms_hr, desc_irrig)

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
    generate_pdf(svg_list, pdf_path, dpi=300)

    open_pdf(pdf_path)