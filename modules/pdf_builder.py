from lxml import etree
import base64
import sqlite3
import pandas as pd
import cairosvg
from PyPDF2 import PdfMerger
from datetime import datetime, timedelta
import os

# Define namespaces
NSMAP = {
    None: "http://www.w3.org/2000/svg",
    "xlink": "http://www.w3.org/1999/xlink",
    "inkscape": "http://www.inkscape.org/namespaces/inkscape",
    "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
}

# Define the function to replace text in an SVG element
def replace_text1(root, element_id, new_text, namespaces):
    """
    Replace the text content of an SVG element with the given ID while stabilizing its position.
    
    Args:
        root: The root element of the SVG tree
        element_id: The ID of the element to modify
        new_text: The new text to insert (converted to string)
        namespaces: Dictionary of XML namespaces
    """
    
    try:
        text_element = root.find(f".//*[@id='{element_id}']", namespaces=namespaces)
        if text_element is not None:
            # Replace the text
            text_element.text = str(new_text)

            # Stabilize the parent <text> element if it exists
            parent = text_element.getparent()
            while parent is not None and parent.tag != "{http://www.w3.org/2000/svg}text":
                parent = parent.getparent()
            if parent is not None and parent.tag == "{http://www.w3.org/2000/svg}text":
                # Preserve parent's position and enforce text-anchor
                x = parent.get("x")
                y = parent.get("y")
                parent.set("text-anchor", "start")  # Force left-alignment
                if x is not None:
                    parent.set("x", x)
                if y is not None:
                    parent.set("y", y)
                print(f"Stabilized parent <text> at x={x}, y={y}")
        else:
            print(f"Warning: Element with ID '{element_id}' not found in SVG.")
    except Exception as e:
        print(f"Error replacing text for ID '{element_id}': {e}")


def replace_text(root, element_id, new_text, namespaces):
    text_element = root.find(f".//*[@id='{element_id}']", namespaces=namespaces)
    if text_element is not None:
        tspan_x = text_element.get("x")
        tspan_y = text_element.get("y")
        text_element.text = str(new_text)
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
        print(f"Stabilized <tspan> at x={tspan_x}, y={tspan_y}")

# Define the function to embed svg in anothe SVG element
def embed_svg(root, base_svg_path, embed_svg_path, output_svg_path, x=0, y=0, scale=1.0):
    """
    Embed an SVG file into another SVG file at a specified position and scale.
    
    Args:
        base_svg_path: Path to the base SVG file
        embed_svg_path: Path to the SVG file to embed
        output_svg_path: Path where the resulting SVG will be saved
        x: X-coordinate for the embedded SVG's top-left corner (default: 0)
        y: Y-coordinate for the embedded SVG's top-left corner (default: 0)
        scale: Scaling factor for the embedded SVG (default: 1.0)
    """
    try:
        # Parse the base SVG
        base_tree = etree.parse(base_svg_path)
        base_root = base_tree.getroot()

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
        base_tree.write(output_svg_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
        print(f"Embedded SVG saved as {output_svg_path}")

    except etree.XMLSyntaxError as e:
        print(f"Error parsing SVG: {e}")
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Define the main function to process the SVG file
def process_page10(agente, input_svg_path="Proposta PPT/page 10.svg", output_svg_path="Temp_ppt/page 10.svg", db_path="DataBase.db"):
    """
    Process an SVG file by replacing text fields with data from a database.
    
    Args:
        agente: The agent's name to query in the database
        input_svg_path: Path to the input SVG file
        output_svg_path: Path where the modified SVG will be saved
        db_path: Path to the SQLite database
    """
    # Load the SVG file
    try:
        tree = etree.parse(input_svg_path)
        root = tree.getroot()
    except FileNotFoundError:
        print(f"Error: SVG file not found at '{input_svg_path}'")
        return
    except etree.XMLSyntaxError as e:
        print(f"Error parsing SVG file: {e}")
        return

    # Define namespaces for Inkscape SVG compatibility
    NSMAP = {
        None: "http://www.w3.org/2000/svg",  # Default SVG namespace
        "xlink": "http://www.w3.org/1999/xlink",
        "inkscape": "http://www.inkscape.org/namespaces/inkscape",
        "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
    }

    # Connect to the SQLite database
    try:
        with sqlite3.connect(db_path) as conn:
            # Query the database for email and phone
            query = """
            SELECT "e-mail", telefone 
            FROM Contatos_Agentes 
            WHERE agente = ?
            """
            df = pd.read_sql_query(query, conn, params=(agente,))
            
            # Check if the query returned any rows
            if df.empty:
                print(f"No results found for agent '{agente}' in the database.")
                return
            
            # Extract email and phone from the first row
            email = df.iloc[0]["e-mail"]
            phone = df.iloc[0]["telefone"]
            
            # Replace text in the SVG file
            replace_text(root, "tspan520-7", agente, NSMAP)  # Agent name
            replace_text(root, "tspan2", email, NSMAP)       # Email
            replace_text(root, "tspan524", phone, NSMAP)     # Phone
            
            # Save the modified SVG file
            try:
                tree.write(output_svg_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
                print(f"Modified SVG saved to '{output_svg_path}'")
            except IOError as e:
                print(f"Error saving modified SVG: {e}")
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def process_page1(cliente, instalacao, fat_ref,  input_svg_path="Proposta PPT/page 1.svg", output_svg_path="Temp_ppt/page 1.svg", db_path="DataBase.db"):
    """
    Process an SVG file by replacing text fields with data from a database.
    
    Args:
        agente: The agent's name to query in the database
        input_svg_path: Path to the input SVG file
        output_svg_path: Path where the modified SVG will be saved
        db_path: Path to the SQLite database
    """
    # Load the SVG file
    try:
        tree = etree.parse(input_svg_path)
        root = tree.getroot()
    except FileNotFoundError:
        print(f"Error: SVG file not found at '{input_svg_path}'")
        return
    except etree.XMLSyntaxError as e:
        print(f"Error parsing SVG file: {e}")
        return
    
    # Replace text in the SVG file
    replace_text(root, "tspan5", "INSTALAÇÃO: " + instalacao, NSMAP)  # Agent name
    replace_text(root, "tspan4", "CLIENTE: " + cliente, NSMAP)       # Email
    replace_text(root, "tspan6", "FATURA DE REFERÊNCIA: " + str(fat_ref), NSMAP)     # Phone
            
    # Save the modified SVG file
    try:
        tree.write(output_svg_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
        print(f"Modified SVG saved to '{output_svg_path}'")
    except IOError as e:
        print(f"Error saving modified SVG: {e}")
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def process_page5(media_mensal, total_contrato, economia_contratual, economia_efetiva, input_svg_path="Proposta PPT/page 5.svg", output_svg_path="Temp_ppt/page 5.svg", db_path="DataBase.db"):
    """
    Process an SVG file by replacing text fields with data from a database.
    
    Args:
        agente: The agent's name to query in the database
        input_svg_path: Path to the input SVG file
        output_svg_path: Path where the modified SVG will be saved
        db_path: Path to the SQLite database
    """
    validade = datetime.today() + timedelta(days=5)

    # Load the SVG file
    try:
        tree = etree.parse(input_svg_path)
        root = tree.getroot()
    except FileNotFoundError:
        print(f"Error: SVG file not found at '{input_svg_path}'")
        return
    except etree.XMLSyntaxError as e:
        print(f"Error parsing SVG file: {e}")
        return
    
    # Replace text in the SVG file
    replace_text(root, "tspan520-7", f"R${media_mensal:,.2f}".replace(",", " "), NSMAP) 
    replace_text(root, "tspan520-7-1", f"R${total_contrato:,.2f}".replace(",", " "), NSMAP)
    replace_text(root, "tspan1", f"{economia_contratual:.0%}" , NSMAP)    
    replace_text(root, "tspan2", f"{economia_efetiva:.0%}" , NSMAP)
    replace_text(root, "tspan6", f"{validade.day:02d}/{validade.month:02d}/{validade.year}", NSMAP)  
    embed_svg(root, input_svg_path,"images/energy_cost_plot.svg", output_svg_path ,x=95,y=120, scale= 0.2)
    # Save the modified SVG file
    try:
        tree.write(output_svg_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
        print(f"Modified SVG saved to '{output_svg_path}'")

    except IOError as e:
        print(f"Error saving modified SVG: {e}")
    
    except Exception as e:
        print(f"Unexpected error: {e}")

def svg_to_pdf(svg_path, pdf_path, dpi=500):
    """
    Convert an SVG file to a PDF with specified DPI for high resolution.
    
    Args:
        svg_path: Path to the input SVG file
        pdf_path: Path where the temporary PDF will be saved
        dpi: Resolution in dots per inch (default: 300 for high quality)
    """
    try:
        cairosvg.svg2pdf(url=svg_path, write_to=pdf_path, dpi=dpi)
        print(f"Converted {svg_path} to {pdf_path}")
    except Exception as e:
        print(f"Error converting {svg_path} to PDF: {e}")

    """from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF
    drawing = svg2rlg(svg_path)
    renderPDF.drawToFile(drawing, pdf_path)"""

def merge_svgs_to_pdf(svg_files, output_pdf, dpi=500):
    """
    Merge multiple SVG files into a single PDF.
    
    Args:
        svg_files: List of paths to SVG files
        output_pdf: Path where the final merged PDF will be saved
        dpi: Resolution in dots per inch (default: 300)
    """
    # List to store temporary PDF paths
    temp_pdfs = []
    merger = PdfMerger()

    # Convert each SVG to a temporary PDF
    for svg_file in svg_files:
        if not os.path.exists(svg_file):
            print(f"Error: {svg_file} does not exist")
            continue
        temp_pdf = svg_file.replace(".svg", "_temp.pdf")
        svg_to_pdf(svg_file, temp_pdf, dpi)
        temp_pdfs.append(temp_pdf)

    # Merge all temporary PDFs
    try:
        with PdfMerger() as merger:
            for pdf in temp_pdfs:
                merger.append(pdf)
            merger.write(output_pdf)
        print(f"Merged PDF saved as {output_pdf}")
   
    except Exception as e:
        print(f"Error merging PDFs: {e}")
    finally:
        # Clean up temporary files
        for temp_pdf in temp_pdfs:
            if os.path.exists(temp_pdf):
                #os.remove(temp_pdf)
                print(f"Removed temporary file {temp_pdf}")

# Example usage
""" 
svg_files = [
    "Proposta PPT/output_page9.svg",
    "Proposta PPT/output_page10.svg"
]
output_pdf = "Proposta PPT/combined_pages_9_10.pdf"
merge_svgs_to_pdf(svg_files, output_pdf, dpi=300)"""