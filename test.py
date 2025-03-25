from modules.pdf_builder import process_page1, process_page5, process_page10, merge_svgs_to_pdf

#process_page1()
process_page5(50000.00,1000000.00, 0.27, 0.12)
process_page10("Fernando Madeira")

svg_list = ['Temp_ppt/page 1.svg','Proposta PPT/page 2.svg', 'Proposta PPT/page 3.svg', '' ,
            'Proposta PPT/page 8.svg', 'Proposta PPT/page 9.svg', 'Temp_ppt/page 10.svg']

svg_list[3] = 'Temp_ppt/page5.svg'

merge_svgs_to_pdf(svg_list, 'output.pdf', dpi= 300)