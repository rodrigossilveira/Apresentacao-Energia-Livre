
from modules.calculations import (
    prepare_quantidade, prepare_impostos_bandeira, calcular_fatura_cativa,
    calcular_fatura_uso, calcular_fatura_livre, gerar_graficos
)
from modules.pdf_builder import process_page1, process_page4, process_page5, process_page6, process_page7, process_page10, generate_pdf, open_pdf
from modules.data_utils import get_tariffs
import os
import streamlit as st
import logging

logger = logging.getLogger("Proposal_Generator")

def generate_proposal(IN, produto, years, grid_data, gd, irrigante, icms, paseb, cofins,                    
                     bandeira, icms_hr, desc_irrig, distribuidora, subgrupo, modalidade, 
                     resolucao, desconto, Razao_Social, Instalacao, fat_ref, agente, duracao_meses):
    
    """
    Generates a proposal document in PDF format based on the provided input parameters.
    Args:
        IN (str): Input data or identifier for the proposal.
        produto (str): The product type (e.g., "Desconto Garantido").
        years (list): List of years for which the proposal is generated.
        grid_data (dict): Data related to grid consumption and usage.
        gd (bool): Indicates whether distributed generation (GD) is applicable.
        irrigante (bool): Indicates whether the client is an irrigator.
        icms (float): ICMS tax rate.
        paseb (float): PASEB tax rate.
        cofins (float): COFINS tax rate.
        bandeira (float): Tariff flag adjustment.
        icms_hr (float): ICMS rate for specific hours.
        desc_irrig (float): Discount for irrigation.
        distribuidora (str): Name of the energy distributor.
        subgrupo (str): Subgroup classification of the client.
        modalidade (str): Tariff modality.
        resolucao (str): Regulatory resolution applicable.
        desconto (float): Discount percentage.
        Razao_Social (str): Client's corporate name.
        Instalacao (str): Installation identifier.
        fat_ref (str): Reference billing period.
        agente (str): Agent responsible for the proposal.
        duracao_meses (int): Duration of the contract in months.
    Returns:
        None: The function generates a PDF file and opens it, but does not return any value.
    Side Effects:
        - Generates and saves a PDF file in the user's Downloads folder.
        - Opens the generated PDF file.
        - Prints debug information to the console.
    Notes:
        - The function calculates various invoices (captive, usage, and free market) and savings.
        - It processes different pages of the proposal based on the product type and client classification.
        - The generated PDF includes graphical representations and client-specific details.
    """

    logger.info("Generating proposal...")
    logging.debug(f"produto: {produto}")
    #print(f"years: {years}", flush=True)
    #print(f"st.session_state.yearly_data: {st.session_state.yearly_data}", flush=True)
    
    quantidade = prepare_quantidade(grid_data)
    logging.debug(f"quantidade: {quantidade}")

    impostos_bandeira = prepare_impostos_bandeira(icms, paseb, cofins, bandeira, icms_hr, desc_irrig)
    logging.debug(f"impostos_bandeira: {impostos_bandeira}")

    tarifa = get_tariffs(distribuidora, subgrupo, modalidade, resolucao)
    logging.debug(f"tarifa: {tarifa}")
    
    preco = {
        "preco": [st.session_state.yearly_data[year]["Preço"] for year in years],
        "produto": produto,
        "anos": years,
        "duracao_meses": duracao_meses,
        "desconto": desconto/100
    }
    logging.debug(f"preco: {preco}")

    # Calculate various invoices
    fatura_cativa_dict = calcular_fatura_cativa(quantidade, tarifa, impostos_bandeira)
    fatura_cativa = fatura_cativa_dict["Fatura Cativa s Compensação"]

    fatura_uso_dict = calcular_fatura_uso(quantidade, tarifa, impostos_bandeira)
    fatura_uso = fatura_uso_dict["Fatura de Uso"]

    fatura_livre_dict = calcular_fatura_livre(quantidade, preco, impostos_bandeira, fatura_uso, fatura_cativa)
    fatura_livre = fatura_livre_dict["Fatura Livre"]
    

    # Calculate savings
    economia_mensal = fatura_cativa - fatura_uso - fatura_livre[0]
    economia_anual = economia_mensal * 12
    
    total_contrato = economia_mensal * duracao_meses

    # Debug logs
    logger.debug(f"fatura_cativa: {fatura_cativa}")
    logger.debug(f"fatura_uso: {fatura_uso}")
    logger.debug(f"fatura_livre: {fatura_livre}")
    logger.debug(f"economia_mensal: {economia_mensal}")
    logger.debug(f"economia_anual: {economia_anual}")
    
    desconto = preco["desconto"] if produto == "Desconto Garantido" else economia_mensal/fatura_cativa
    
    

    # Create PDF from SVGs
    svg_list = [
        'Temp_ppt/page 1.svg',
        'Proposta PPT/page 2.svg', 
        'Proposta PPT/page 3.svg', 
        'Placeholder',
        'Proposta PPT/page 8.svg', 
        'Proposta PPT/page 9.svg', 
        'Temp_ppt/page 10.svg'
    ]

    # Generate graphics and process pages
    gerar_graficos(preco, quantidade, tarifa, impostos_bandeira, fatura_uso, fatura_cativa, fatura_livre)
    process_page1(Razao_Social, Instalacao, fat_ref)
    process_page10(agente)
    
    if(produto == "Desconto Garantido"):
        logger.debug("Desconto Garantido pdf")
        if(gd):
            logger.debug("GD variant")
            #desconto_efetivo = 0.12 #placeholder
            fatura_cativa_c_compensacao = fatura_cativa_dict["Fatura Cativa"]
            desconto_efetivo = (fatura_cativa_c_compensacao - fatura_uso - fatura_livre[0]) / fatura_cativa_c_compensacao

            process_page5(IN, economia_mensal, total_contrato, desconto, desconto_efetivo)
            svg_list[3] = 'Temp_PPT/page 5.svg'
        else:
            logger.debug("No GD variant")
            process_page4(IN, economia_mensal, total_contrato, desconto)
            svg_list[3] = 'Temp_PPT/page 4.svg'

    elif(irrigante):
            logger.debug("Irrigante variant")         
            process_page7(IN, economia_mensal, total_contrato, desconto, economia_anual)
            svg_list[3] = 'Tem_PPT/page 7.svg'

    else:
        logger.debug("Preco fixo Normal variant")
        process_page6(IN, economia_mensal, total_contrato, desconto)
        svg_list[3] = 'Temp_PPT/page 6.svg'
  


    download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    pdf_path = os.path.join(download_folder, 'Proposta_' + Razao_Social + '_' + Instalacao + '_' + produto.replace(" ","_").replace("ç","c") + '.pdf')
    generate_pdf(svg_list, pdf_path, dpi=300)

    open_pdf(pdf_path)