import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import os

def flags_plot(categories, values, output_path = 'images/', filename = 'flags_plot.svg'):
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
        ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width}%', 
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
    plt.savefig(save_path, bbox_inches='tight', dpi=300)

# Example usage
"""categories = ['VERDE', 'AMARELA', 'VERMELHA I', 'VERMELHA II']
values = [22, 24, 27, 30]"""

def generate_yearly_economy_plot(years, values, percentages, output_folder = 'images/', output_filename = 'yearly_economy_plot.svg'):
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
        ax.text(label_x_pos_outside, label_y_pos_inside, f'{percentages[i]}%', 
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
    plt.savefig(output_path, bbox_inches='tight')  # No need for dpi in vector formats
    plt.close()  # Close the figure to free memory

# Example usage
"""years = ['2030', '2029', '2028', '2027', '2026']
values = [35849.07, 42256.63, 36916.99, 31577.36, 4879]
 percentages = [23.8, 28.1, 24.5, 21.0, 3.2]"""

def generate_price_curve_plot(years, values, output_folder = 'images', output_filename = 'price_curve_plot.svg'):
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
    ax.set_title('Preço Praticado por Período ¹', fontsize=24, fontweight='bold', color = '#0F766E')
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
    plt.savefig(output_path, bbox_inches='tight')  # No need for dpi in vector formats
    plt.close()  # Close the figure to free memory

# Example usage
"""years = ['2026', '2027', '2028', '2029', '2030', '2031']
values = [395.00, 270.00, 245.00, 220.00, 250.00, 260.00]"""

def generate_historico_irrigante_plot(months, custo_cativo_values, energia_livre_values, economia_values, output_folder = 'images/', output_filename = 'historico_irigante_plot.svg'):
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
    plt.savefig(output_path, bbox_inches='tight')  # No need for dpi in vector formats
    plt.close()  # Close the figure to free memory

# Example usage
"""# Data for the bar chart
months = ['Feb-24', 'Mar-24', 'Apr-24', 'May-24', 'Jun-24', 'Jul-24', 'Aug-24', 'Sep-24', 'Oct-24', 'Nov-24', 'Dec-24', 'Jan-25']
custo_cativo_values = [14422, 19304, 16189, 18403, 19098, 56123, 51053, 59629, 24614, 13128, 11260, 10386]
energia_livre_values = [17166, 20817, 19298, 11360, 20417, 50495, 48801, 53867, 20914, 11642, 9597, 8304]"""


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


def flags_pie_plot(categories, values, output_path='images/', filename='flags_pie_plot.png'):

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
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    crop_bottom(save_path, save_path, 0.3)


# Example usage
"""categories = ['Verde', 'Amarela', 'Vermelha 1', 'Vermelha 2']
values = [10.4, 11.36, 12.49, 16.92]"""