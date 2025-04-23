from lxml import etree
import base64
import sqlite3
import pandas as pd
import cairosvg
from PyPDF2 import PdfMerger
from datetime import datetime, timedelta
from io import BytesIO
import os
from modules.data_utils import fetch_agent_contact_info
import logging

logger = logging.getLogger("Proposal_Generator")

# Define namespaces
NSMAP = {
    None: "http://www.w3.org/2000/svg",
    "xlink": "http://www.w3.org/1999/xlink",
    "inkscape": "http://www.inkscape.org/namespaces/inkscape",
    "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
}

def load_svg(input_svg_path: str) -> tuple:
    """
    Load and parse an SVG file.

    Args:
        input_svg_path (str): Path to the input SVG file.

    Returns:
        tuple: A tuple containing the parsed tree and root element, or (None, None) if an error occurs.
    """
    logger = logging.getLogger("Proposal_Generator")
    try:
        tree = etree.parse(input_svg_path)
        root = tree.getroot()
        return tree, root
    except FileNotFoundError:
        logger.error(f"Error: SVG file not found at '{input_svg_path}'")
    except etree.XMLSyntaxError as e:
        logger.error(f"Error parsing SVG file: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    return None, None

def replace_text(root, element_id: str, old_text: str, new_text: str, namespaces: dict) -> None:
    """
    Replaces text within an SVG element identified by its ID, while preserving
    its position attributes (`x` and `y`) and ensuring parent elements do not
    override these attributes.

    Args:
        root (xml.etree.ElementTree.Element): The root element of the SVG document.
        element_id (str): The ID of the SVG element whose text is to be replaced.
        old_text (str): The text to be replaced within the element.
        new_text (str): The new text to replace the old text.
        namespaces (dict): A dictionary of namespace mappings for the SVG document.

    Returns:
        None
    """

    text_element = root.find(f".//*[@id='{element_id}']", namespaces=namespaces)
    if text_element is not None:
        tspan_x = text_element.get("x")
        tspan_y = text_element.get("y")
        updated_text = text_element.text.replace(old_text, str(new_text))
        text_element.text = updated_text
        if tspan_x is not None:
            text_element.set("x", tspan_x)
        if tspan_y is not None:
            text_element.set("y", tspan_y)
        # Ensure parent <tspan> or <text> doesn’t override
        parent = text_element.getparent()
        if parent.tag == "{http://www.w3.org/2000/svg}tspan":
            parent_x = parent.get("x")
            parent_y = parent.get("y")
            if parent_x is not None:
                parent.set("x", parent_x)
            if parent_y is not None:
                parent.set("y", parent_y)
        #logger.debug(f"Stabilized <tspan> at x={tspan_x}, y={tspan_y}")
        logger.debug(f"{element_id} text replaced: '{old_text}' -> '{new_text}'")


def embed_svg(root, base_svg_path, embed_svg_path: str, x: int = 0, y: int = 0, scale: int = 1.0) -> None:
    """
    Embed an SVG file into another SVG file at a specified position and scale, modifying the base SVG in-place.
    
    Args:
        root: The root element of the base SVG tree to modify
        base_svg_path: Path to the base SVG file
        embed_svg_path: Path to the SVG file to embed
        x: X-coordinate for the embedded SVG's top-left corner (default: 0)
        y: Y-coordinate for the embedded SVG's top-left corner (default: 0)
        scale: Scaling factor for the embedded SVG (default: 1.0)
    
    Returns:
        The modified SVG tree
    """
    logger = logging.getLogger("Proposal_Generator")
    logging.info(f"Embedding SVG '{embed_svg_path}' into '{base_svg_path}' at ({x}, {y}) with scale {scale}")
    try:
        # Parse the base SVG
        base_tree = root.getroottree()

        # Parse the SVG to embed
        embed_tree = etree.parse(embed_svg_path)
        embed_root = embed_tree.getroot()

        # Create a <g> element to group the embedded SVG content
        group = etree.Element("g", nsmap=NSMAP)
        transform = f"translate({x}, {y}) scale({scale})"
        group.set("transform", transform)

        # Move all children from the embed SVG's root to the group
        for child in embed_root:
            group.append(child)

        # Append the group to the base SVG's root
        root.append(group)

        # Save the modified SVG
        logger.debug(f"SVG {base_svg_path} embedded successfully")
        return base_tree

    except etree.XMLSyntaxError as e:
        logger.error(f"Error parsing embedded SVG: {e}")
    except FileNotFoundError as e:
        logger.error(f"Error: Embedded SVG file not found - {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

def process_page1(cliente, instalacao, fat_ref,  input_svg_path="Proposta PPT/page 1.svg", output_svg_path="Temp_ppt/page 1.svg", db_path="DataBase.db"):
    """
    Process an SVG file by replacing text fields with data from a database.
    
    Args:
        agente: The agent's name to query in the database
        input_svg_path: Path to the input SVG file
        output_svg_path: Path where the modified SVG will be saved
        db_path: Path to the SQLite database
    """
    logger.debug("Processing page 1")
    # Load the SVG file
    tree, root = load_svg(input_svg_path)
    if not tree or not root:
        return
    
    # Format fat_ref to "dd/mm/yyyy"
    if isinstance(fat_ref, datetime):
        formatted_fat_ref = fat_ref.strftime("%d/%m/%Y")
    else:
        # If fat_ref is a string, parse it into a datetime object first
        formatted_fat_ref = datetime.strptime(str(fat_ref), "%Y-%m-%d").strftime("%d/%m/%Y")

    # Replace text in the SVG file
    replace_text(root, "tspan5",":", ": " + instalacao, NSMAP)  # Agent name
    replace_text(root, "tspan4",":",  ": " + cliente, NSMAP)       # Email
    replace_text(root, "tspan6",":", ": " + str(formatted_fat_ref), NSMAP)     # Phone
            
    # Save the modified SVG file
    try:
        tree.write(output_svg_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
        logger.info(f"Modified SVG saved to '{output_svg_path}'")

    except IOError as e:
        logger.error(f"Error saving modified SVG: {e}")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def process_page4(IN: str, media_mensal: float, total_contrato: float, economia_contratual: float, input_svg_path="Proposta PPT/page 4.svg", output_svg_path="Temp_ppt/page 4.svg", db_path="DataBase.db"):
    """
    Processes and modifies an SVG file for page 4 of a presentation by replacing text elements 
    and embedding an image. The function also calculates a validity date and formats numerical 
    values for insertion into the SVG.
    Args:
        IN (str): Instalation number as a string
        media_mensal (float): Monthly average value to be formatted and inserted into the SVG.
        total_contrato (float): Total contract value to be formatted and inserted into the SVG.
        economia_contratual (float): Contractual savings percentage to be formatted and inserted into the SVG.
        economia_efetiva (float): Effective savings value (not directly used in the function).
        input_svg_path (str, optional): Path to the input SVG file. Defaults to "Proposta PPT/page 4.svg".
        output_svg_path (str, optional): Path to save the modified SVG file. Defaults to "Temp_ppt/page 4.svg".
        db_path (str, optional): Path to the database file (not directly used in the function). Defaults to "DataBase.db".
    Returns:
        None
    Notes:
        - The function uses helper functions `load_svg`, `replace_text`, and `embed_svg` to manipulate the SVG.
        - The `validade` date is calculated as 5 days from the current date.
        - Numerical values are formatted with a comma as the decimal separator and a space as the thousands separator.
        - The function handles exceptions during the SVG saving process and logs errors if they occur.
    """
    logger.debug("Processing page 4")
    validade = datetime.today() + timedelta(days=5)

    # Load the SVG file
    tree, root = load_svg(input_svg_path)
    if not tree or not root:
        return
    
    # Replace text in the SVG file
    
    replace_text(root, "tspan520-74-4-0-6", "XXXXXXXXXX", IN, NSMAP) 
    replace_text(root, "tspan520-7", "xx xxx,xx", f"{media_mensal:.2f}".replace(",", " ").replace(".",","), NSMAP) 
    replace_text(root, "tspan520-7-1", "xx xxx,xx", f"{total_contrato:.2f}".replace(",", " ").replace(".",","), NSMAP)
    replace_text(root, "tspan12", "25%",  f"{economia_contratual:.0%}" , NSMAP)    
    replace_text(root, "tspan6","20/02/2025", f"{validade.day:02d}/{validade.month:02d}/{validade.year}", NSMAP)  
    embed_svg(root, input_svg_path,"images/energy_cost_plot.svg" ,x=80,y=95, scale= 0.25)
    # Save the modified SVG file
    try:
        tree.write(output_svg_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
        logger.info(f"Modified SVG saved to '{output_svg_path}'")


    except IOError as e:
        logger.error(f"Error saving modified SVG: {e}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def process_page5(IN: str, media_mensal: float, total_contrato: float, economia_contratual: float, economia_efetiva: float, input_svg_path="Proposta PPT/page 5.svg", output_svg_path="Temp_ppt/page 5.svg", db_path="DataBase.db"):
    """
    Processes and modifies an SVG file to update specific text elements and embed an image.
    Args:
        IN (str): Instalacao number as a string.
        media_mensal (float): Monthly average value to be displayed in the SVG.
        total_contrato (float): Total contract value to be displayed in the SVG.
        economia_contratual (float): Contractual savings percentage to be displayed in the SVG.
        economia_efetiva (float): Effective savings percentage to be displayed in the SVG.
        input_svg_path (str, optional): Path to the input SVG file. Defaults to "Proposta PPT/page 5.svg".
        output_svg_path (str, optional): Path to save the modified SVG file. Defaults to "Temp_ppt/page 5.svg".
        db_path (str, optional): Path to the database file (not used in the current implementation). Defaults to "DataBase.db".
    Returns:
        None
    Notes:
        - The function loads an SVG file, replaces specific text elements with provided values,
        embeds an image, and saves the modified SVG to the specified output path.
        - The `validade` date is calculated as 5 days from the current date and formatted as DD/MM/YYYY.
        - The function handles exceptions during the saving process and prints error messages if any issues occur.
    """
   
    validade = datetime.today() + timedelta(days=5)

    logger.debug("Processing page 5")

    # Load the SVG file
    tree, root = load_svg(input_svg_path)
    if not tree or not root:
        return
    
    # Replace text in the SVG file
    replace_text(root, "tspan520-74-4-0-6", "3014435811", IN, NSMAP) 
    replace_text(root, "tspan520-7", "xx xxx,xx", f"{media_mensal:,.2f}".replace(",", " ").replace(".",","), NSMAP) 
    replace_text(root, "tspan520-7-1", "xx xxx,xx", f"{total_contrato:,.2f}".replace(",", " ").replace(".",","), NSMAP)
    replace_text(root, "tspan1", "25%",  f"{economia_contratual:.0%}" , NSMAP)    
    replace_text(root, "tspan2","14%", f"{economia_efetiva:.0%}" , NSMAP)
    replace_text(root, "tspan6","20/02/2025", f"{validade.day:02d}/{validade.month:02d}/{validade.year}", NSMAP)  
    embed_svg(root, input_svg_path,"images/energy_cost_plot.svg" ,x=95,y=120, scale= 0.2)
    # Save the modified SVG file
    try:
        tree.write(output_svg_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
        logger.info(f"Modified SVG saved to '{output_svg_path}'")

    except IOError as e:
        logger.error(f"Error saving modified SVG: {e}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def process_page6(IN, media_mensal, total_contrato, economia_contratual, input_svg_path="Proposta PPT/page 6.svg", output_svg_path="Temp_ppt/page 6.svg", db_path="DataBase.db"):
    """
    Processes and modifies an SVG file for page 6 of a presentation by replacing text elements 
    and embedding additional SVG images.
    Args:
        IN (str): Instalacao number as a string.
        media_mensal (float): Monthly average value to be formatted and replaced in the SVG.
        total_contrato (float): Total contract value to be formatted and replaced in the SVG.
        economia_contratual (float): Contractual savings percentage to be formatted and replaced in the SVG.
        economia_efetiva (float): Effective savings percentage (currently unused in the function).
        input_svg_path (str, optional): Path to the input SVG file. Defaults to "Proposta PPT/page 6.svg".
        output_svg_path (str, optional): Path to save the modified SVG file. Defaults to "Temp_ppt/page 6.svg".
        db_path (str, optional): Path to the database file (currently unused in the function). Defaults to "DataBase.db".
    Returns:
        None
    Notes:
        - The function calculates a validity date (5 days from today) and replaces it in the SVG.
        - Text elements in the SVG are replaced using the `replace_text` function.
        - Additional SVG images are embedded into the main SVG using the `embed_svg` function.
        - The modified SVG is saved to the specified output path.
        - Error handling is implemented for file saving and unexpected exceptions.
    """
    
    logger.debug("Processing page 6")

    validade = datetime.today() + timedelta(days=5)

    # Load the SVG file
    tree, root = load_svg(input_svg_path)
    if not tree or not root:
        return
    
    # Replace text in the SVG file
    replace_text(root, "tspan520-74-4-0-6", "3014435811", IN, NSMAP) 
    replace_text(root, "tspan520-7", "xx xxx,xx", f"{media_mensal:,.2f}".replace(",", " ").replace(".",","), NSMAP) 
    replace_text(root, "tspan520-7-1", "xx xxx,xx", f"{total_contrato:,.2f}".replace(",", " ").replace(".",","), NSMAP)
    replace_text(root, "tspan1", "25%",  f"{economia_contratual:.0%}" , NSMAP)    
    #replace_text(root, "tspan2","14%", f"{economia_efetiva:.0%}" , NSMAP)
    replace_text(root, "tspan12","20/02/2025", f"{validade.day:02d}/{validade.month:02d}/{validade.year}", NSMAP)  
    embed_svg(root, input_svg_path,"images/energy_cost_plot.svg" ,x=80,y=75, scale= 0.25)
    embed_svg(root, input_svg_path,"images/flags_plot.svg" ,x=135,y=190, scale= 0.15)
    embed_svg(root, input_svg_path,"images/price_curve_plot.svg" ,x=-35,y=190, scale= 0.1)
    # Save the modified SVG file
    try:
        tree.write(output_svg_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
        logger.info(f"Modified SVG saved to '{output_svg_path}'")

    except IOError as e:
        logger.error(f"Error saving modified SVG: {e}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def process_page7(IN, media_mensal, total_contrato, economia_contratual, economia_anual, input_svg_path="Proposta PPT/page 7.svg", output_svg_path="Temp_ppt/page 7.svg", db_path="DataBase.db"):
    """
    Processes and modifies an SVG file for page 7 of a presentation by embedding data and replacing placeholders.
    Args:
        IN (str): Instalacao number as a string.
        media_mensal (float): Monthly average value to be formatted and embedded in the SVG.
        total_contrato (float): Total contract value to be formatted and embedded in the SVG.
        economia_contratual (float): Contractual savings percentage to be formatted and embedded in the SVG.
        economia_anual (float): Annual savings value (currently unused in the function).
        input_svg_path (str, optional): Path to the input SVG file. Defaults to "Proposta PPT/page 7.svg".
        output_svg_path (str, optional): Path to save the modified SVG file. Defaults to "Temp_ppt/page 7.svg".
        db_path (str, optional): Path to the database file (currently unused in the function). Defaults to "DataBase.db".
    Returns:
        None
    Notes:
        - The function loads an SVG file, replaces specific text placeholders with formatted values, and embeds additional SVG images.
        - The modified SVG is saved to the specified output path.
        - The function calculates a validity date (5 days from the current date) and embeds it in the SVG.
        - Error handling is included for saving the modified SVG file.
    """
    logger.debug("Processing page 7")

    validade = datetime.today() + timedelta(days=5)

    # Load the SVG file
    tree, root = load_svg(input_svg_path)
    if not tree or not root:
        return
    
    # Replace text in the SVG file
    replace_text(root, "tspan520-74-4-0-6", "XXXXXXXXXX", IN, NSMAP) 
    replace_text(root, "tspan520-7", "xx xxx,xx", f"{media_mensal:,.2f}".replace(",", " ").replace(".",","), NSMAP) 
    replace_text(root, "tspan520-7-1", "xx xxx,xx", f"{total_contrato:,.2f}".replace(",", " ").replace(".",","), NSMAP)
    replace_text(root, "tspan5", "XXX XXX", f"{total_contrato:,.0f}".replace(",", " ").replace(".",","), NSMAP)
    replace_text(root, "tspan1", "25%",  f"{economia_contratual:.0%}" , NSMAP)    
    #replace_text(root, "tspan2","14%", f"{economia_efetiva:.0%}" , NSMAP)
    replace_text(root, "tspan12","20/02/2025", f"{validade.day:02d}/{validade.month:02d}/{validade.year}", NSMAP)  
    embed_svg(root, input_svg_path,"images/energy_cost_plot.svg" ,x=125,y=75, scale= 0.18)
    embed_svg(root, input_svg_path,"images/historic_graph.svg" ,x=80,y=170, scale= 0.165)

    # Save the modified SVG file
    try:
        tree.write(output_svg_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
        logger.info(f"Modified SVG saved to '{output_svg_path}'")

    except IOError as e:
        logger.error(f"Error saving modified SVG: {e}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def process_page10(agente, input_svg_path="Proposta PPT/page 10.svg", output_svg_path="Temp_ppt/page 10.svg", db_path="DataBase.db"):
    """
    Process an SVG file by replacing text fields with data from a database.
    
    Args:
        agente: The agent's name to query in the database
        input_svg_path: Path to the input SVG file
        output_svg_path: Path where the modified SVG will be saved
        db_path: Path to the SQLite database
    """
    logger.debug("Processing page 10")

    # Load the SVG file
    tree, root = load_svg(input_svg_path)
    if not tree or not root:
        return

    # Define namespaces for Inkscape SVG compatibility
    NSMAP = {
        None: "http://www.w3.org/2000/svg",  # Default SVG namespace
        "xlink": "http://www.w3.org/1999/xlink",
        "inkscape": "http://www.inkscape.org/namespaces/inkscape",
        "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
    }

    # Fetch agent contact info from the database
    contact_info = fetch_agent_contact_info(agente, db_path)
    if not contact_info:
        return

    # Replace text in the SVG file
    replace_text(root, "tspan520-7", "Agente/Analista Comercial", agente, NSMAP)  # Agent name
    replace_text(root, "tspan524", "(00) 0000-0000", contact_info["phone"], NSMAP)  # Email
    replace_text(root, "tspan2", "XXXXXXXXXX@cemig.com.br", contact_info["email"], NSMAP)  # Phone

    # Save the modified SVG file
    try:
        tree.write(output_svg_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
        logger.info(f"Modified SVG saved to '{output_svg_path}'")
    except IOError as e:
        logger.error(f"Error saving modified SVG: {e}")

def svg_to_pdf_stream(svg_path: str, dpi: int = 500) -> None:
    """
    Convert an SVG file to a PDF stream in memory.
    
    Args:
        svg_path: Path to the input SVG file
        dpi: Resolution in dots per inch (default: 500)
    
    Returns:
        BytesIO object containing PDF data
    """
    try:
        pdf_stream = BytesIO()
        cairosvg.svg2pdf(url=svg_path, write_to=pdf_stream, dpi=dpi)
        pdf_stream.seek(0)
        logger.info(f"Converted {svg_path} to PDF stream")
        return pdf_stream
    except Exception as e:
        logger.error(f"Error converting {svg_path} to PDF: {e}")
        return None

def generate_pdf(svg_files: list, output_pdf: str, dpi: int = 500) -> None:
    """
    Merge multiple SVG files into a single PDF without saving temporary files.
    
    Args:
        svg_files: List of paths to SVG files
        output_pdf: Path where the final merged PDF will be saved
        dpi: Resolution in dots per inch (default: 500)
    """
    merger = PdfMerger()

    # Convert each SVG to PDF stream and append to merger
    for svg_file in svg_files:
        if not os.path.exists(svg_file):
            logger.error(f"Error: {svg_file} does not exist")
            continue
        pdf_stream = svg_to_pdf_stream(svg_file, dpi)
        if pdf_stream:
            merger.append(pdf_stream)

    # Write the merged PDF to disk
    try:
        with open(output_pdf, 'wb') as f:
            merger.write(f)
        logger.info(f"Merged PDF saved as {output_pdf}")
    except Exception as e:
        logger.error(f"Error merging PDFs: {e}")
    finally:
        merger.close()

def open_pdf(pdf_path: str) -> None:
    """
    Opens a PDF file using the default PDF viewer on the operating system.

    Parameters:
        pdf_path (str): The file path to the PDF document to be opened.

    Behavior:
        - On macOS, it uses the "open" command to open the PDF.
        - On Linux, the "xdg-open" command can be used (commented out in the code).
        - On Windows, it uses the "start" command to open the PDF.

    Note:
        Ensure that the `pdf_path` is a valid file path and that the operating system
        has a default application configured to open PDF files.
    """
    if os.name == "posix":  # macOS/Linux
        os.system(f"open {pdf_path}")  # macOS
        # Use "xdg-open" for Linux: os.system(f"xdg-open {pdf_path}")
    elif os.name == "nt":  # Windows
        os.system(f"start {pdf_path}")



