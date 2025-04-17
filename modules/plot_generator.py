import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.ticker as ticker
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.legend_handler import HandlerPatch
import matplotlib.patches as mpatches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
import os
from PIL import Image
from pathlib import Path
from typing import Optional

def flags_plot(values, categories = ['VERDE', 'AMARELA', 'VERMELHA I', 'VERMELHA II'], output_path = 'images/', filename = 'flags_plot.svg', transparent_background: bool = True):
    # Reverse the order of the data
    categories = categories[::-1]
    values = values[::-1]
    colors = ['#1EFF8C', '#FFCB2A', '#EC3137', '#AE3333']

    # Create the figure and axis objects
    fig, ax = plt.subplots(figsize=(10, 4))

    # Create the horizontal bar chart
    bars = ax.barh(categories, values, color=colors)

    # Add data labels on the bars
    for bar in bars:
        width = bar.get_width()
        label_x_pos = width + 4 
        ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width:.2f}%', 
                va='center', ha='right', color='#0F7661', fontweight='bold', fontsize = 20)

    # Set the title and labels
    ax.set_title('DESCONTO MÉDIO EM CADA \nBANDEIRA TARIFÁRIA\n', fontsize=24, x=-0.00
                , ha = 'left', color='#0F7661')
    #ax.set_xlabel('Desconto (%)', fontsize=12)
    #ax.set_ylabel('Bandeira Tarifária', fontsize=12)

    ax.set_xlim(left=-1)

    #Remove lines surrounding the plot
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Bring back the left spine and set its color
    ax.spines['left'].set_visible(True)
    ax.spines['left'].set_color('#0F7661')
    ax.spines['left'].set_linewidth(2)

    #bars = ax.barh(categories, values, color=colors, height=0.0001)  # Adjust height (e.g., 0.6)

    #Remove ticks from the y-axis
    ax.tick_params(left=False)

    ax.yaxis.set_tick_params(pad=15)  # Adds 15px padding between labels and spine
    ax.set_yticklabels(categories, fontsize=20, color='#0F7661')  # Adjust fontsize as needed
    # Remove the x-axis ticks and labels
    ax.xaxis.set_visible(False)

    # Show the plot
    plt.tight_layout()
    save_path = os.path.join(output_path, filename)
    plt.savefig(save_path, transparent= transparent_background, bbox_inches='tight', dpi=300)

# Example usage
"""
values = [22, 24, 27, 30]
"""

def yearly_economy_plot(years, values, percentages, output_folder = 'images/', output_filename = 'yearly_economy_plot.svg', transparent_background: bool = True):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    x_offset = 0
    y_offset = 0

    colors = ['#0F766E'] * len(years)

    # Create the figure and axis objects
    fig, ax = plt.subplots(figsize=(18, 6.5))

    # Create the horizontal bar chart
    bars = ax.barh(years, values, color=colors)


     # Determine the threshold (e.g., 10% of the maximum bar width)
    max_width = max(values)
    threshold = 0.10 * max_width  # Adjust the percentage as needed

     # Add two data labels for each bar
    for i, bar in enumerate(bars):
        width = bar.get_width()
        
        # Label 1: Monetary value (inside or outside based on threshold)
        if width < threshold:
            # Outside label (black font)
            label_x_pos_inside = width + 1000 # Adjust offset for outside positioning
            label_y_pos_inside = bar.get_y() + bar.get_height() / 2 + 0.2 
            label_color = 'black'
            x_offset = 6000
            y_offset = -0.2
        else:
            # Inside label (white font)
            label_x_pos_inside = 1000  # Adjust multiplier for inside positioning
            label_y_pos_inside = bar.get_y() + bar.get_height() / 2
            label_color = 'white'
        
        ax.text(label_x_pos_inside, label_y_pos_inside, f'R$ {values[i]:,.2f}', 
                va='center', ha='left', color=label_color, fontweight='bold', fontsize=12)
        
        # Label 2: Percentage (outside end of the bar)
        label_x_pos_outside = width + 1000  # Adjust offset for percentage positioning
        label_y_pos_inside = bar.get_y() + bar.get_height() / 2 + y_offset
        ax.text(label_x_pos_outside, label_y_pos_inside, f'{percentages[i]:.2%}', 
                va='center', ha='left', color='black', fontweight='bold', fontsize=12)
    # Customize the title and add icon
    ax.set_title('Economia Anual²', fontsize=16, fontweight='bold', loc='center', color = '#0F766E')
    img_path = 'images/money_icon.png'  # Path to your money icon image
    arr_img = plt.imread(img_path, format='png')
    imagebox = OffsetImage(arr_img, zoom=0.4)  # Adjust zoom as needed
    ab = AnnotationBbox(imagebox, xy = (0.4, 1.04), xycoords= 'axes fraction', frameon=False)
    ax.add_artist(ab)

    # Remove ticks and spines
    ax.tick_params(left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Remove x-axis and add padding to y-axis labels
    ax.xaxis.set_visible(False)
    ax.yaxis.set_tick_params(pad=15)

    # Save the plot as a vectorized image
    output_path = os.path.join(output_folder, output_filename)
    plt.savefig(output_path,transparent= transparent_background, bbox_inches='tight')  # No need for dpi in vector formats
    plt.close()  # Close the figure to free memory

# Example usage
"""years = ['2030', '2029', '2028', '2027', '2026']
values = [35849.07, 42256.63, 36916.99, 31577.36, 4879]
 percentages = [23.8, 28.1, 24.5, 21.0, 3.2]"""

def price_curve_plot(years, values, output_folder = 'images', output_filename = 'price_curve_plot.svg', transparent_background: bool = True):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Data for the bar chart
    
    colors = ['#0F766E'] * len(years)

    # Create the figure and axis objects
    fig, ax = plt.subplots(figsize=(18, 4))

    # Create the vertical bar chart
    bars = ax.bar(years, values, color=colors, width= 0.3)

    # Add data labels on top of the bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 20, f'R$ {height:,.2f}', 
                ha='center', va='bottom', color='black', fontweight='bold', fontsize=18)

    # Customize the title and remove unnecessary elements
    ax.set_title('Preço Praticado por Período ¹\n\n', fontsize=24, fontweight='bold', color = '#0F766E')
    ax.yaxis.set_visible(False)


    # Remove ticks and spines
    ax.tick_params(axis='x', labelsize=14, color = '#D3D3D3')  # Adjust fontsize
    for label in ax.get_xticklabels():
        label.set_fontweight('bold')
        label.set_color('#6a6a6a')       # Make labels bold
    ax.tick_params(left=False, bottom=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.xaxis.set_tick_params(pad=15)  # Adds 15px padding between labels and spine


    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_color('#D3D3D3')
    
    # Save the plot as a vectorized image
    output_path = os.path.join(output_folder, output_filename)
    plt.savefig(output_path, transparent= transparent_background, bbox_inches='tight')  # No need for dpi in vector formats
    plt.close()  # Close the figure to free memory

# Example usage
"""years = ['2026', '2027', '2028', '2029', '2030', '2031']
values = [395.00, 270.00, 245.00, 220.00, 250.00, 260.00]"""

def historico_irrigante_plot(months, custo_cativo_values, energia_livre_values, economia_values, output_folder = 'images/', output_filename = 'historico_irigante_plot.svg', transparent_background: bool = True):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)


    economia_values = [energia_livre_values[i] - custo_cativo_values[i] for i in range(0,len(energia_livre_values))]
    economia_percent = [-economia_values[i]/custo_cativo_values[i] for i in range(0,len(economia_values))]
    # Create the figure and axis objects
    fig, ax = plt.subplots(figsize=(14, 6))

    # Set bar width and positions
    bar_width = 0.35
    index = range(len(months))

    # Create the grouped bars
    bars1 = ax.bar(index, custo_cativo_values, bar_width, color='#FF6B6B', label='CUSTO CATIVO')
    bars2 = ax.bar([i + bar_width for i in index], energia_livre_values, bar_width, color='#0F766E', label='ENERGIA LIVRE')

    # Add percentage labels above the bars
    for i, value in enumerate(economia_percent):
        if value < 0:
            color = 'red'
        else:
            color = 'green'
        ax.text(i + bar_width / 2, max(custo_cativo_values[i], energia_livre_values[i]) + 1000, f'{value: .1%}', 
                ha='center', va='bottom', color=color, fontweight='bold', fontsize=12)

    # Customize the title and remove unnecessary elements
    ax.tick_params(axis='y', labelsize=10)
    ax.legend()

    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)
    # Remove ticks and spines
    ax.tick_params(left=False, bottom=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Add a data table below the chart
    cell_text = [
        [f'R$ {custo:,}' for custo in custo_cativo_values],
        [f'R$ {livre:,}' for livre in energia_livre_values],
        [f'R$ {eco:,}' for eco in economia_values]
    ]
    row_labels = ['CUSTO CATIVO', 'ENERGIA LIVRE', 'ECONOMIA']
    col_labels = months

    # Define row colors
    row_colors = ['#FF6B6B', '#0F766E', 'white']  # Match bar colors for the first two rows
    
    # Add the table
    table = ax.table(cellText=cell_text, rowLabels=row_labels, colLabels=col_labels,
                     loc='bottom', bbox=[0, -0.4, 1, 0.3])  # Adjust bbox for spacing
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)  # Adjust font size of the table
    table.scale(1, 1.5)  # Scale the table for better readability

    # Adjust layout to accommodate the table
    plt.subplots_adjust(left=0.2, bottom=0.4)  # Add space for the table

    # Save the plot as a vectorized image
    output_path = os.path.join(output_folder, output_filename)
    plt.savefig(output_path, transparent= transparent_background, bbox_inches='tight')  # No need for dpi in vector formats
    plt.close()  # Close the figure to free memory


def crop_bottom(image_path, output_path, crop_percentage=0.3):
    # Open the image
    img = Image.open(image_path)
    
    # Get the dimensions of the image
    width, height = img.size
    
    # Calculate the amount to crop from the bottom
    crop_height = int(height * crop_percentage)
    
    # Define the box to crop (left, upper, right, lower)
    box = (0, 0, width, height - crop_height)
    
    # Crop the image
    cropped_img = img.crop(box)
    
    # Save the cropped image
    cropped_img.save(output_path)


def flags_pie_plot(categories, values, output_path='images/', filename='flags_pie_plot.png', transparent_background: bool = True):

    categories = categories[::-1]
    values = values[::-1]
    colors = ['#6D1B1E', '#E53935', '#FFC107' , '#7AC24C', 'white']

    # Append an extra data point for the "invisible" half-circle
    values.append(sum(values))  # Add the sum of all values
    categories.append("")        # Add an empty category for the invisible slice

    # Create the figure and axis objects
    fig, ax = plt.subplots(figsize=(8, 8))

    # Create the pie chart with only the top half populated
    wedges, texts, autotexts = ax.pie(
        values, 
        labels=None, 
        colors=colors, 
        autopct=lambda pct: f'{pct:.2f}%' if pct > 0 else '',  # Show percentage only for visible slices
        startangle=0, 
        wedgeprops=dict(width=0.45, edgecolor='white'), 
        radius=1.2,  # Increase the radius to make the donut larger
        pctdistance=0.85
    )

    # Set the title
    ax.set_title('DESCONTO EM CADA BANDEIRA\n', fontsize=20)

    # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.axis('equal')  

    for i, autotext in enumerate(autotexts):
        if i < len(autotexts) - 1:  # Only customize visible slices
            autotext.set_color('white' if categories[i] in ['Vermelha 1', 'Vermelha 2'] else 'black')
            autotext.set_weight('bold')
            autotext.set_fontsize(14)
        else:
            autotext.set_visible(False)  # Hide the percentage for the invisible slice

    # Add horizontal legend at the bottom
    legend = ax.legend(
        wedges[:-1],  # Exclude the invisible slice from the legend
        categories[:-1],  # Exclude the empty category from the legend
        title="Bandeira", 
        loc='upper center', 
        bbox_to_anchor=(0.5, 0.5),  # Adjust vertical position of the legend
        ncol=len(categories) - 1,  # Exclude the invisible slice
        frameon=False
    )
    plt.setp(legend.get_texts(), fontsize='14', color='#0F7661')
    plt.setp(legend.get_title(), fontsize='16', color='#0F7661')

    # Remove the axes
    ax.axis('off')
    print(values)
    # Save the plot
    save_path = os.path.join(output_path, filename)
    plt.savefig(save_path, transparent= transparent_background, bbox_inches='tight', dpi=300)
    crop_bottom(save_path, save_path, 0.3)


def energy_cost_plot(total_cost, energia_livre, servicos_distribuicao,economia, output_path='images/', filename='energy_cost_plot.svg', transparent_background: bool = True):
    """
    Generates a bar plot comparing total energy cost with a breakdown of Energia Livre, 
    Serviços de Distribuição, and Economia. The plot includes annotations, icons, and 
    labels for better visualization.
    Args:
        total_cost (float): The total energy cost.
        energia_livre (float): The cost of Energia Livre.
        servicos_distribuicao (float): The cost of Serviços de Distribuição.
        economia (float): The amount of savings (economia).
        output_path (str, optional): The directory where the plot will be saved. Defaults to 'images/'.
        filename (str, optional): The name of the output file. Defaults to 'energy_cost_plot.svg'.
    Raises:
        Exception: If there is an error loading the icon images.
    Notes:
        - The plot includes two bars: one for the total cost and another stacked bar 
            for Energia Livre, Serviços de Distribuição, and Economia.
        - Icons and labels are added to enhance the visualization.
        - The plot is saved as an SVG file with a transparent background.
    Example:
        energy_cost_plot(
            total_cost=1000.0,
            energia_livre=400.0,
            servicos_distribuicao=300.0,
            economia=300.0,
            output_path='output/',
            filename='cost_comparison.svg'
        )
    """

    # Create the figure and axis objects
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='none')  # Increased figure width for more spacing
    ax.set_facecolor('none')  # Set axes background to transparent

    # Left bar (total cost)
    ax.bar(0, total_cost, color='#D3D3D3', width=0.8, edgecolor='black', linewidth=1.5, zorder=1)  # Increased width to 0.8

    # Right bar (stacked: Energia Livre + Serviços de Distribuição + Economia)
    ax.bar(2, energia_livre, color='#1EFF8C', width=0.8, edgecolor='black', linewidth=1.5, zorder=1)  # Increased width and moved to x=2 for spacing
    ax.bar(2, servicos_distribuicao, bottom=energia_livre, color='#0F7661', width=0.8, edgecolor='black', linewidth=1.5, zorder=1)
    ax.bar(2, economia, bottom=energia_livre + servicos_distribuicao, color='white', width=0.8, 
           edgecolor='black', linewidth=1.5, linestyle='--', zorder=1)

    # Add text labels for the values
    # Left bar (total cost)
    ax.text(0, total_cost / 2, f'R$ {total_cost:,.2f}'.replace(",",".").replace(".",","), ha='center', va='center', color='black', fontweight='bold', fontsize=12)

    # Right bar (Energia Livre)
    ax.text(2, energia_livre / 2, f'R$ {energia_livre:,.2f}'.replace(",",".").replace(".",","), ha='center', va='center', color='white', fontweight='bold', fontsize=12)
    # Right bar (Serviços de Distribuição)
    ax.text(2, energia_livre + servicos_distribuicao / 2, f'R$ {servicos_distribuicao:,.2f}'.replace(",",".").replace(".",","), ha='center', va='center', color='white', fontweight='bold', fontsize=12)
    # Right bar (Economia) with "ECONOMIA" label above
    economia_y_pos = energia_livre + servicos_distribuicao + economia / 2
    ax.text(2, economia_y_pos + 500, 'ECONOMIA', ha='center', va='center', color='black', fontweight='bold', fontsize=14)
    ax.text(2, economia_y_pos, f'R$ {economia:,.2f}'.replace(",",".").replace(".",","), ha='center', va='center', color='black', fontweight='bold', fontsize=12)

    # Load the icon images with error handling
    try:
        light_bulb_img = mpimg.imread('images/light_bulb.jpg')
        print("Light bulb image loaded successfully:", light_bulb_img.shape)
    except Exception as e:
        print(f"Error loading light bulb image: {e}")
        light_bulb_img = None

    try:
        power_line_img = mpimg.imread('images/power_line.jpg')
        print("Power line image loaded successfully:", power_line_img.shape)
    except Exception as e:
        print(f"Error loading power line image: {e}")
        power_line_img = None

    # Define the positions for the icons
    x_icon = 2.8  # Adjusted for the new bar position and spacing
    y_energia = energia_livre / 2
    y_servicos = energia_livre + servicos_distribuicao / 2

    # Add the icons using OffsetImage and AnnotationBbox
    if light_bulb_img is not None:
        light_bulb_offset = OffsetImage(light_bulb_img, zoom=0.35, zorder=10)
        ab_light_bulb = AnnotationBbox(light_bulb_offset, (x_icon, y_energia), frameon=False, zorder=10)
        ax.add_artist(ab_light_bulb)
        # Add the text label next to the icon
        ax.text(x_icon + 0.3, y_energia, 'Energia Livre', ha='left', va='center', color='#0F7661', fontsize=12)

    if power_line_img is not None:
        power_line_offset = OffsetImage(power_line_img, zoom=0.3, zorder=10)
        ab_power_line = AnnotationBbox(power_line_offset, (x_icon, y_servicos), frameon=False, zorder=10)
        ax.add_artist(ab_power_line)
        # Add the text label next to the icon
        ax.text(x_icon + 0.3, y_servicos, 'Serviços de Distribuição', ha='left', va='center', color='#0F7661', fontsize=12)

    # Remove spines and ticks
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(left=False, bottom=False)
    ax.set_xticks([])
    ax.set_yticks([])

    # Set the limits after all elements are added
    ax.set_ylim(0, max(total_cost, energia_livre + servicos_distribuicao + economia) * 1.2)
    ax.set_xlim(-0.5, 4)  # Increased x-axis limit to accommodate wider spacing

    # Save the plot
    plt.tight_layout()
    save_path = os.path.join(output_path, filename)
    plt.savefig(save_path, transparent= transparent_background, bbox_inches='tight', dpi=300)
    plt.show()

def create_historic_graph(months, actual_values, new_values, reference_values, 
                       show_quota=True, figsize=(12,6), output_path="images/historic_graph.svg",
                       transparent_background = True):
    """
    Create a custom graph with rounded rectangles and circles.
    
    Parameters:
    months (list): List of month labels
    actual_values (list): List of actual values
    new_values (list): List of new values
    reference_values (list): List of reference values
    show_quota (bool): Whether to show quota lines and labels
    figsize (tuple): Figure size (width, height)
    """
    
    percentage_diff = [((-1)*(actual - new - ref) / actual * 100) 
                  for actual, new, ref in zip(actual_values, new_values, reference_values)]

    # Calculate spacing based on y-range and figure width, adjusted for equal aspect
    y_range = max(actual_values) * 1.1  # Max y-limit
    total_x_units = y_range * (figsize[0] / figsize[1])
    spacing = total_x_units / (len(months) + 1)
    #spacing = 2*y_range / (len(months))  # Scale spacing to y-range, 1.5 is a tuning factor
    width = spacing*0.3

    # Function definitions
    def flying_rectangle_graph(x_ax, y_ax, y0_ax, width, offset=0, face_color='gold', edge_color=None):
        
        """
        Draws rectangles with rounded ends (circles) for a bar-like plot.
        Skips drawing circles if y_ax is null (NaN/None) or zero.
        
        Parameters:
        - x_ax: List of x-axis labels (e.g., months)
        - y_ax: List of heights for rectangles
        - y0_ax: List of base y-values for rectangles
        - width: Width of each rectangle
        - offset: Horizontal offset for positioning
        - face_color: Color of the rectangles and circles
        - edge_color: Color of the rectangle edges (None for default)
        
        Returns:
        - None
        """

        rectprops = dict(facecolor=face_color, edgecolor='black', linewidth=0)
        x = spacing * np.arange(len(x_ax))
        heights = y_ax
        basis = y0_ax
        circle_radius = 0.95 * width / 2

        for i, month in enumerate(x_ax):
            # Only draw circles if height is non-zero and not NaN
            if not (np.isnan(heights[i]) or heights[i] == 0): 
                rect = FancyBboxPatch((x[i] - width + offset, basis[i]), width, 
                                    heights[i], boxstyle="round", **rectprops)
                ax.add_patch(rect)

                circle_top = Circle((x[i] - width/2 + offset, basis[i] + heights[i]), 
                                    radius=circle_radius, color=face_color)
                circle_bottom = Circle((x[i] - width/2 + offset, basis[i]), 
                                    radius=circle_radius, color=face_color)
                ax.add_patch(circle_top)
                ax.add_patch(circle_bottom)

            # Add percentage difference labels
            #label_x = x[i] - width/2 + offset
            #label_y = (actual_values[i] + basis[i] + heights[i])/2 - 4
            #label = Text(label_x, label_y, f'{percentage_diff[i]:.1f}%', 
            #            ha='center', va='bottom', rotation=90, 
            #            color='#0D5F4E', fontsize=11)  # Darker green than #117761
            #ax.add_artist(label)
        return None

    def add_quota(x_ax, actual_values, new_values, reference_values, width=width, circle_radius=width/2):
        x = spacing * np.arange(len(x_ax))  # Use the same spacing as the main plot
        offset = spacing * 0.35  # Match the offset used in flying_rectangle_graph
        for i, month in enumerate(x_ax):
            # Start at top of new_values circle (basis + height + radius)
            y_start = reference_values[i] + new_values[i] + circle_radius
            # End at top of actual_values circle (height + radius)
            y_end = actual_values[i] + circle_radius
            # X-position centered on the new_values series
            x_pos = x[i] + width/2
            # Define text height (approximate, in data units; adjust if needed)
            # Calculate midpoint and text height before drawing lines
            mid_y = (y_start + y_end) / 2
            mid_x = x_pos
            text_height = (y_end - y_start) * 0.25  # 10% of the total height as buffer
            # Lower segment: from y_start to just below text
            quota_line_lower = Line2D([x_pos, x_pos], [y_start + 0.1*width, mid_y - text_height],
                                    color='lightgrey', linestyle='-')
            ax.add_line(quota_line_lower)
            # Upper segment: from just above text to y_end
            quota_line_upper = Line2D([x_pos, x_pos], [mid_y + text_height, y_end - 0.1*width],
                                    color='lightgrey', linestyle='-')
            ax.add_line(quota_line_upper)
            
            mid_x = x_pos
            mid_y = (y_start + y_end) / 2
            quota_text = Text(mid_x, mid_y, f'{percentage_diff[i]:.1f}%', ha='center', va='center', rotation=90, color='#0D5F4E', fontsize=11)
            ax.add_artist(quota_text)

            # Horizontal line at bottom (y_start)
            hline_bottom = Line2D([x_pos - 0.4 * width, x_pos + 0.4 * width], [y_start + 0.1*width, y_start + 0.1*width],
                                  color='lightgrey', linestyle='-')
            ax.add_line(hline_bottom)
            # Horizontal line at top (y_end)
            hline_top = Line2D([x_pos - 0.4 * width, x_pos + 0.4 * width], [y_end - 0.1*width, y_end- 0.1*width],
                              color='lightgrey', linestyle='-')
            ax.add_line(hline_top)


    # Plot setup
    fig, ax = plt.subplots(figsize=figsize)
    #ax.set_aspect('auto')
    plt.axis('equal')
    # Replace your format_func with:
    def format_func(value, pos):
        if value >= 1000000:
            return f'R$ {value / 1000000:.1f}M'
        elif value >= 1000:
            return f'R$ {value / 1000:.1f}k'
        return f'R$ {value:.0f}'

    # Axis configuration
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_func))
    ax.set_xticks(spacing * np.arange(len(months)))    
    ax.set_xticklabels(months, rotation=0, ha='center')
    ax.tick_params(axis='x', pad=15)  # Increase spacing between labels and plot
    ax.set_xlim(-0.5 * spacing, spacing * len(months) + 0.5)
    ax.set_ylim(0, max(actual_values) * 1.1)
    #ax.set_title('Desempenho Mensal\n', fontsize=16, fontweight='bold', color='#107762')
    # Remove x and y axis spines (black lines)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # Remove x and y axis ticks
    ax.tick_params(axis='x', which='both', length=0)  # Remove x-axis ticks
    ax.tick_params(axis='y', which='both', length=0)  # Remove y-axis ticks

    # Create graph elements
    flying_rectangle_graph(months, actual_values, [0]*len(months), width=width, offset=0, face_color='#fec107')
    flying_rectangle_graph(months, reference_values, [0]*len(months), width=width, offset=width, face_color='#117761')
    flying_rectangle_graph(months, new_values, reference_values, width=width, offset=width, face_color='#e7e9e8')
    if show_quota:
        add_quota(months, actual_values, new_values, reference_values, width=width)

    class HandlerCircle(HandlerPatch):
        def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
            center = xdescent + 0.5 * width, ydescent + 0.5 * height
            p = mpatches.Circle(xy=center, radius=4)
            self.update_prop(p, orig_handle, legend)
            p.set_transform(trans)
            return [p]
        
    # Create legend
    legend_elements = [
        plt.Circle((0, 0), 1, facecolor='#fec107', edgecolor='none', label='Simulação Mercado Cativo'),
        plt.Circle((0, 0), 1, facecolor='#117761', edgecolor='none', label='Fatura TUSD Distribuidora'),
        plt.Circle((0, 0), 1, facecolor='#e7e9e8', edgecolor='none', label='Fatura CEMIG (Mercado Livre de Energia)')
    ]
    plt.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(0.0, -0.15), ncol=3, frameon=False,
              handler_map={plt.Circle: HandlerCircle()})
    
    # Wrapping all out
    plt.tight_layout()
    
    fig.savefig(output_path, transparent= transparent_background, bbox_inches='tight')
    plt.close(fig)
