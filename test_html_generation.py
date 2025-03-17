from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

def generate_pdf_from_html(template_path, output_pdf_path, context):
    """
    Generates a PDF from an HTML template by replacing placeholders with provided context.

       :param output_pdf_path: Path where the generated PDF will be saved.
    :param context: A dictionary containing placeholder-value pairs for replacement.
    """
    try:
        # Step 1: Load the HTML template
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template(template_path)

        # Step 2: Render the template with the provided context
        rendered_html = template.render(context)


        # Step 3: Save the rendered HTML to a temporary file (optional)
        temp_html_path = "temp_rendered.html"
        with open(temp_html_path, 'w', encoding='utf-8') as file:
            file.write(rendered_html)

        # Step 4: Convert the rendered HTML to PDF
        HTML(string=rendered_html).write_pdf(output_pdf_path)

        print(f"PDF successfully generated at: {output_pdf_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Define paths
    template_path = r"Layout_CEMIG copy.html"  # Path to your HTML template
    output_pdf_path = r"output.pdf"  # Path where the PDF will be saved

    # Get user input for placeholders
    #title = input("Enter the title of the document: ")

    #website_name = input("Enter the name of the website: ")
    #custom_text = input("Enter custom text for the paragraph: ")

    # Create a context dictionary for Jinja2
    context = {
        "title": "hello",
        "website_name": "Again",
        "custom_text": "friend o a friend"
    }
    # Generate the PDF
    generate_pdf_from_html(template_path, output_pdf_path, context)