import pandas as pd
import sqlite3
import streamlit as st
from modules.plot_generator import yearly_economy_plot, price_curve_plot, flags_plot, energy_cost_plot

@st.cache_data
def calcular_fatura_cativa(quantidade, tarifa, impostos_bandeira):
    """
    Calcula o valor a pagar por algum item/linha da fatura.
    :param quantidade: dict
    :param tarifa: dict
    :param impostos_bandeira: dict containing icms, paseb, cofins, and bandeira
    :return: dict

    result_dict = {
        "Demanda HFP": kW,
        "Demanda HFP sICMS": kW,
        "Demanda HP": None,  
        "Demanda HP sICMS": kW,
        "Demanda HR": kW,
        "Demanda HR sICMS": kW,
        "Energia HFP": MWh,
        "Energia HP": MWh,
        "Energia HR": MWh,
        "Energia Compensada HFP": MWh,
        "Energia Compensada HP": MWh,        
        "Desconto Irrigante Noturno": MWh,
        "Bandeira": MWh,
        }
    """
    # Create a dictionary to store the values during function execution
    result_dict = {
        "Demanda HFP": None,
        "Demanda HFP sICMS": None,
        "Demanda HP": None,
        "Demanda HP sICMS": None,
        "Energia HFP": None,
        "Energia HP": None,
        "Energia HR": None,
        "Energia Compensada HFP": None,
        "Energia Compensada HP": None,
        "Desconto Irrigante Noturno": None,
        "Custo da Bandeira": None,
        "Fatura Cativa": None
    }
    
    paseb_cofins = (1 / (1 - impostos_bandeira["paseb"] - impostos_bandeira["cofins"]))
    icms = 1/(1- impostos_bandeira["icms"])
    icms_hr = 1/(1- impostos_bandeira["icms_hr"])

    conn = sqlite3.connect("DataBase.db")
    flag = impostos_bandeira['bandeira']
    query = f'SELECT "{flag}" FROM tariff_flags'
    try:
        bandeira = pd.read_sql_query(query, conn).iloc[0,0]
    finally:
        conn.close()
        
    result_dict["Demanda HFP"] = quantidade["Demanda HFP"] * tarifa["Demanda_HFP"] * icms * paseb_cofins
    result_dict["Demanda HFP sICMS"] = quantidade["Demanda HFP sICMS"] * tarifa["Demanda_HFP"] * paseb_cofins
    result_dict["Demanda HP"] = quantidade["Demanda HP"] * tarifa["Demanda_HP"] * icms * paseb_cofins
    result_dict["Demanda HP sICMS"] = quantidade["Demanda HP sICMS"] * tarifa["Demanda_HP"] * paseb_cofins
    #result_dict["Demanda HR"] = quantidade["Demanda HR"] * tarifa["Demanda_HFP"] * icms_hr * paseb_cofins
    #result_dict["Demanda HR sICMS"] = quantidade["Demanda HR sICMS"] * tarifa["Demanda_HFP"] * paseb_cofins
    result_dict["Energia HFP"] = quantidade["Energia HFP"] * (tarifa["Consumo_HFP"] + bandeira) * icms * paseb_cofins
    result_dict["Energia HP"] = quantidade["Energia HP"] * (tarifa["Consumo_HP"] + bandeira) * icms * paseb_cofins
    result_dict["Energia HR"] = quantidade["Energia HR"] * tarifa["Consumo_HFP"] * icms_hr * paseb_cofins
    result_dict["Energia Compensada HP"] = quantidade["Energia Compensada HP"] * tarifa["Consumo_HP"] * icms * paseb_cofins
    result_dict["Energia Compensada HFP"] = quantidade["Energia Compensada HFP"] * tarifa["Consumo_HFP"] * icms * paseb_cofins

    result_dict["Desconto Irrigante Noturno"] = quantidade["Energia HR"] * (tarifa["Consumo_HFP"] + bandeira) * impostos_bandeira["desc_irr"]
    result_dict["Custo da Bandeira"] = ((quantidade["Energia HP"] + 
                                        quantidade['Energia HFP']) * bandeira * icms * paseb_cofins + 
                                        quantidade["Energia HR"] * bandeira * (icms_hr*paseb_cofins - impostos_bandeira["desc_irr"])
                                        )

    result_dict["Fatura Cativa"] = (
        result_dict["Demanda HFP"] + result_dict["Demanda HFP sICMS"] + result_dict["Demanda HP"] + 
        result_dict["Demanda HP sICMS"] + result_dict["Energia HFP"] + result_dict["Energia HP"] + 
        result_dict["Energia HR"] - result_dict["Energia Compensada HP"] - result_dict["Energia Compensada HFP"] -
        result_dict["Desconto Irrigante Noturno"]
    )
    return result_dict

@st.cache_data
def calcular_fatura_uso(quantidade, tarifa, impostos_bandeira):
    """
    Calcula os valores relacionados à fatura de uso de energia elétrica com base nas quantidades, tarifas e impostos fornecidos.
    Args:
        quantidade (dict): Um dicionário contendo as quantidades de energia e demanda utilizadas. 
            As chaves esperadas incluem:
                - "Demanda HFP": Quantidade de demanda em horário fora de ponta.
                - "Demanda HFP sICMS": Quantidade de demanda em horário fora de ponta sem ICMS.
                - "Demanda HP": Quantidade de demanda em horário de ponta.
                - "Demanda HP sICMS": Quantidade de demanda em horário de ponta sem ICMS.
                - "Energia HFP": Quantidade de energia consumida em horário fora de ponta.
                - "Energia HP": Quantidade de energia consumida em horário de ponta.
                - "Energia HR": Quantidade de energia consumida em horário reservado.
        tarifa (dict): Um dicionário contendo as tarifas aplicáveis. 
            As chaves esperadas incluem:
                - "Demanda_HFP": Tarifa para demanda em horário fora de ponta.
                - "Demanda_HP": Tarifa para demanda em horário de ponta.
                - "Consumo_HFP_TUSD": Tarifa de uso do sistema de distribuição para consumo em horário fora de ponta.
                - "Consumo_HP_TUSD": Tarifa de uso do sistema de distribuição para consumo em horário de ponta.
        impostos_bandeira (dict): Um dicionário contendo os valores de impostos e descontos aplicáveis. 
            As chaves esperadas incluem:
                - "paseb": Percentual do PASEB.
                - "cofins": Percentual do COFINS.
                - "icms": Percentual do ICMS.
                - "icms_hr": Percentual do ICMS para horário reservado.
                - "desc_irr": Percentual de desconto para irrigação noturna.
    Returns:
        dict: Um dicionário contendo os valores calculados para cada componente da fatura, incluindo:
            - "Demanda HFP": Valor da demanda em horário fora de ponta.
            - "Demanda HFP sICMS": Valor da demanda em horário fora de ponta sem ICMS.
            - "Demanda HP": Valor da demanda em horário de ponta.
            - "Demanda HP sICMS": Valor da demanda em horário de ponta sem ICMS.
            - "Energia HFP": Valor da energia consumida em horário fora de ponta.
            - "Energia HP": Valor da energia consumida em horário de ponta.
            - "Energia HR": Valor da energia consumida em horário reservado.
            - "Energia Compensada HFP": Valor da energia compensada em horário fora de ponta (não calculado explicitamente).
            - "Energia Compensada HP": Valor da energia compensada em horário de ponta (não calculado explicitamente).
            - "Desconto Irrigante Noturno": Valor do desconto para irrigação noturna.
            - "Desconto Demanda HFP": Valor do desconto na demanda em horário fora de ponta.
            - "Desconto Demanda HP": Valor do desconto na demanda em horário de ponta.
            - "Desconto TUSD HP": Valor do desconto na tarifa de uso do sistema de distribuição em horário de ponta.
            - "Fatura de Uso": Valor total da fatura de uso, considerando os descontos aplicáveis.
    """

    # Create a dictionary to store the values during function execution
    result_dict = {
        "Demanda HFP": None,
        "Demanda HFP sICMS": None,
        "Demanda HP": None,
        "Demanda HP sICMS": None,
        "Energia HFP": None,
        "Energia HP": None,
        "Energia HR": None,
        "Energia Compensada HFP": None,
        "Energia Compensada HP": None,
        "Desconto Irrigante Noturno": None,
        "Desconto Demanda HFP": None,
        "Desconto Demanda HP": None,
        "Desconto TUSD HP": None,
        "Fatura de Uso": None
    }

    paseb_cofins = (1 / (1 - impostos_bandeira["paseb"] - impostos_bandeira["cofins"]))
    icms = 1/(1- impostos_bandeira["icms"])
    icms_hr = 1/(1- impostos_bandeira["icms_hr"])
        
    result_dict["Demanda HFP"] = quantidade["Demanda HFP"] * tarifa["Demanda_HFP"] * icms * paseb_cofins
    result_dict["Demanda HFP sICMS"] = quantidade["Demanda HFP sICMS"] * tarifa["Demanda_HFP"] * paseb_cofins
    result_dict["Demanda HP"] = quantidade["Demanda HP"] * tarifa["Demanda_HP"] * icms * paseb_cofins
    result_dict["Demanda HP sICMS"] = quantidade["Demanda HP sICMS"] * tarifa["Demanda_HP"] * paseb_cofins
    result_dict["Energia HFP"] = quantidade["Energia HFP"] * tarifa["Consumo_HFP_TUSD"] * icms * paseb_cofins
    result_dict["Energia HP"] = quantidade["Energia HP"] * tarifa["Consumo_HP_TUSD"] * icms * paseb_cofins
    result_dict["Energia HR"] = quantidade["Energia HR"] * tarifa["Consumo_HFP_TUSD"] * icms_hr * paseb_cofins
    

    result_dict["Desconto Irrigante Noturno"] = quantidade["Energia HR"] * tarifa["Consumo_HFP_TUSD"] * impostos_bandeira["desc_irr"]
    result_dict["Desconto Demanda HFP"] = quantidade["Demanda HFP"] * tarifa["Demanda_HFP"] * 0.5
    result_dict["Desconto Demanda HP"] = quantidade["Demanda HP"] * tarifa["Demanda_HP"] * 0.5
    result_dict["Desconto TUSD HP"] = quantidade["Energia HP"] * (tarifa["Consumo_HP_TUSD"]-tarifa["Consumo_HFP_TUSD"]) * 0.5

    result_dict["Fatura de Uso"] = (
        result_dict["Demanda HFP"] + result_dict["Demanda HFP sICMS"] + result_dict["Demanda HP"] + 
        result_dict["Demanda HP sICMS"] + result_dict["Energia HFP"] + result_dict["Energia HP"] + 
        result_dict["Energia HR"]  -  result_dict["Desconto Irrigante Noturno"] - result_dict["Desconto Demanda HFP"] 
        - result_dict["Desconto Demanda HP"] - result_dict["Desconto TUSD HP"]
    )
    return result_dict

@st.cache_data
def calcular_fatura_livre(quantidade, preco, impostos_bandeira, fatura_uso, fatura_cativa):
    """
    Calculates the "Fatura Livre" (Free Invoice) based on the provided parameters.
    This function computes the free invoice values for different years based on the 
    pricing model and other parameters such as energy quantities, taxes, and usage fees.
    Args:
        quantidade (dict): A dictionary containing energy quantities for different periods:
            - "Energia HP": Energy during peak hours.
            - "Energia HFP": Energy during partial peak hours.
            - "Energia HR": Energy during off-peak hours.
        preco (dict): A dictionary containing pricing information:
            - "produto" (str): The pricing model, which can be "Desconto Garantido", "Curva de Preço", or "PMT".
            - "desconto" (float): Discount percentage (used for "Desconto Garantido").
            - "preco" (list): List of prices for each year (used for "Curva de Preço" and "PMT").
            - "anos" (list): List of years corresponding to the prices.
        impostos_bandeira (dict): A dictionary containing tax rates:
            - "icms" (float): ICMS tax rate.
            - "icms_hr" (float): ICMS tax rate for off-peak hours.
        fatura_uso (float): The usage fee for the free invoice.
        fatura_cativa (float): The captive invoice value.
    Returns:
        dict: A dictionary containing:
            - "Fatura Livre" (list): Calculated free invoice values for each year.
            - "anos" (list): List of years corresponding to the calculated values.
    Notes:
        - The function uses the `@st.cache_data` decorator to cache the results for optimization.
        - The calculation varies based on the pricing model specified in `preco["produto"]`:
            - "Desconto Garantido": Applies a discount to the captive invoice and subtracts the usage fee.
            - "Curva de Preço" and "PMT": Calculates based on energy quantities, tax rates, and prices.
    Debugging:
        The function includes debug print statements to log intermediate values such as:
        - Captive invoice (`fatura_cativa`).
        - Usage fee (`fatura_uso`).
        - Length of years and prices lists.
        - Energy quantities and calculated free invoice values.
    """
    result_dict = {
        "Fatura Livre": [],
        "anos": preco["anos"]
    }

    icms = 1/(1- impostos_bandeira["icms"])
    icms_hr = 1/(1- impostos_bandeira["icms_hr"])

    match preco["produto"]:

        case "Desconto Garantido": 
                result_dict["Fatura Livre"]  = [(1- preco["desconto"])*fatura_cativa - fatura_uso for i,_ in enumerate(preco["anos"])] 
        case "Curva de Preço":
                result_dict["Fatura Livre"] = [preco["preco"][i]*(quantidade["Energia HP"] * icms + quantidade["Energia HFP"] * icms + quantidade["Energia HR"] * icms_hr)/1000 for i,_ in enumerate(preco["anos"])]
        case "PMT":
                result_dict["Fatura Livre"] = [preco["preco"][i]*(quantidade["Energia HP"] * icms + quantidade["Energia HFP"] * icms + quantidade["Energia HR"] * icms_hr)/1000 for i,_ in enumerate(preco["anos"])]
    
    print(f"calcular_fatura_livre - fatura_cativa: {fatura_cativa}", flush=True)
    print(f"calcular_fatura_livre - fatura_uso: {fatura_uso}", flush=True)
    print(f"calcular_fatura_livre - len(preco['anos']): {len(preco['anos'])}", flush=True)
    print(f"calcular_fatura_livre - len(preco['preco']): {len(preco['preco'])}", flush=True)
    print(f"calcular_fatura_livre - quantidade: {quantidade}", flush=True)
    print(f"calcular_fatura_livre - fatura_livre: {result_dict['Fatura Livre']}", flush=True)
    return result_dict

@st.cache_data
def gerar_graficos(preco, quantidade, tarifa, impostos_bandeira,  fatura_uso, fatura_cativa, fatura_livre):
    months = [min(12, max(0, preco["duracao_meses"] - 12*i)) for i in range(len(preco["anos"]))]

    #price curve plot
    price_curve_plot(preco["anos"], preco["preco"])
    
    # Debugging output
    print(f"len(preco['anos']): {len(preco['anos'])}")
    print(f"len(months): {len(months)}")
    print(f"len(fatura_livre): {len(fatura_livre)}")
    print(f"fatura_livre: {fatura_livre}")
    print(f"preco['preco']: {preco['preco']}")


  

    #yearly economy plot
    economy = [(fatura_cativa - fatura_uso - fatura_livre[i])*months[i] for i in range(len(months))]
    percentual_economy = [(fatura_cativa - fatura_uso - fatura_livre[i])/fatura_cativa for i in range(len(fatura_livre))]
    yearly_economy_plot(preco["anos"], economy, percentual_economy )
    #print(percentual_economy)
    
    #flags plot
    descontos_bandeiras = []
    for bandeira in ['verde', 'amarela', 'vermelha I', 'vermelha II']:
        new_dict = impostos_bandeira
        new_dict[bandeira] = bandeira
        fatura_cativa_bandeira = calcular_fatura_cativa(quantidade, tarifa, new_dict)["Fatura Cativa"]
        #descontos_bandeiras.append((fatura_cativa - fatura_uso - fatura_livre))
        mean_economy = sum((fatura_cativa_bandeira - fatura_uso - fatura_livre[i])*months[i] for i in range(len(months)))/preco["duracao_meses"]
        descontos_bandeiras.append(100*mean_economy/fatura_cativa_bandeira)

    #energy cost plot
    #energy_cost_plot(total_cost, energia_livre, servicos_distribuicao,economia, output_path='images/', filename='energy_cost_plot.svg')
    energy_cost_plot(fatura_cativa,fatura_livre[0], fatura_uso, economy[0]/12)
    print(descontos_bandeiras)
    flags_plot(descontos_bandeiras)