import pandas as pd
import sqlite3

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
    query = f"SELECT {impostos_bandeira['bandeira']} FROM tariff_flags"
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

def calcular_fatura_uso(quantidade, tarifa, impostos_bandeira):

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

    conn = sqlite3.connect("DataBase.db")
    query = f"SELECT {impostos_bandeira['bandeira']} FROM tariff_flags"
    try:
        bandeira = pd.read_sql_query(query, conn).iloc[0,0]
    finally:
        conn.close()
        
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

def calcular_fatura_livre(quantidade, preco, impostos_bandeira):