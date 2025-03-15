"""Configuration settings for the application."""

# Default values
DEFAULT_DURATION_MONTHS = 60
DEFAULT_PASEP = 0.83
DEFAULT_COFINS = 3.82
DEFAULT_ICMS = 18.0
DEFAULT_START_DATE = "2026-01-01"

# Product options
PRODUCT_OPTIONS = ["Desconto Garantido", "Curva de Preço", "PMT"]

# Bandeira options
BANDEIRA_OPTIONS = ["Verde", "Amarela", "Vermelha 1", "Vermelha 2"]

# Modalidade Tarifária options
MODALIDADE_TARIFARIA_OPTIONS = ["A4", "A3", "AS", "A2", "A1", "A3a", "B"]
MODALIDADE_TARIFARIA_VERDE_OPTIONS = ["Verde", "Azul"]

# Grid structure for energy inputs
ENERGY_GRID_ROWS = [
    ["Demanda - Ponta", "Demanda - Fora Ponta", "Demanda - Horário Reservado"],
    ["Demanda s/ ICMS - Ponta", "Demanda s/ ICMS - Fora Ponta", "Demanda s/ ICMS - Horário Reservado"],
    ["Energia Ativa - Ponta", "Energia Ativa - Fora Ponta", "Energia Ativa - Horário Reservado"]
]

ENERGIA_COMPENSADA_ROW = [
    ["Energia Compensada - Ponta", "Energia Compensada - Fora Ponta", "Energia Compensada - Horário Reservado"]
]

# CSS for layout
LAYOUT_CSS = """
    <style>
        div[data-testid="stVerticalBlock"] > div {
            margin-bottom: 0px !important;
            padding-bottom: 0px !important;
        }
        div[data-testid="column"] {
            margin-bottom: 0px !important;
            padding-bottom: 0px !important;
        }
    </style>
""" 