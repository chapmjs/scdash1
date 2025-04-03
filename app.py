import pandas as pd
from shiny import App, ui, render
from shinywidgets import output_widget, render_widget
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Define the data
data = {
    'Part Number': ['E2081-66555', 'E2081-66556', 'E2084-66501', 'E2084-66508', 'E2084-66522', 
                    'E2084-66523', 'E2081-61116', 'E2081-61120', 'E2084-67600', 'E2084-61101', 
                    'E2084-64701', 'E2084-64401', 'E2084-00102', 'E2084-64400', 'E2084-66203', 
                    'E2084-66200', 'E2084-67907', 'E2084-67920', 'E3065-66504', 'E3065-66505', 
                    'E3065-66519', 'E3065-66517', 'E2084-67960', 'E3065-64701', 'E3065-67901', 
                    'E2084-04107', 'E2084-04108', 'E3065-66513', 'E2085-66520', 'E3066-66514', 
                    'E2084-67927'],
    'Description': ['HV Driver', 'Waveplate 1"', 'Motorized Flipper', 'Mounting pedistal', 'Holding Fork', 
                    '90 degree prisms', 'Prism Coating', 'Prism Mount', 'Translation stage', 'Picomotor actuator', 
                    'Picomotor driver', 'Window (FS coated)', 'Bare Vacuum Flange', 'Vacuum Pump', 'Vacuum Pump Valve', 
                    'Mirror', 'Mount claw', 'Mounting pedistal', 'Holding Fork', 'Picomotor Servo', 
                    'Tilting Mirror', 'Mirror Driver crate', 'Mirror Driver card', 'Mirror Readback Card', 'Lens', 
                    'Optical Table', 'Laser Diode', 'Hyphenator Duphenator', 'LH Smokeshifter', 'Bracket', 
                    'Injection Pump'],
    'Supplier': ['McDonalds', 'McDonalds', 'McDonalds', 'McDonalds', 'Wendys', 
                'Wendys', 'Quiznos', 'Quiznos', 'Quiznos', 'Quiznos', 
                'Taco Time', 'KFC', 'KFC', 'Subway', 'IHOP', 
                'IHOP', 'Sizzler', 'Quiznos', 'Wendys', 'Wendys', 
                'McDonalds', 'Wendys', 'Sizzler', 'Taco Time', 'Panda Express', 
                'BYU-I Food Services', 'BYU-I Food Services', 'Wendys', 'McDonalds', 'McDonalds', 
                'Sizzler'],
    'Yield': [99.0, 99.0, 99.7, 99.0, 99.0, 
             99.0, 99.0, 99.0, 99.0, 98.0, 
             100.0, 99.0, 99.0, 100.0, 100.0, 
             100.0, 100.0, 100.0, 99.0, 99.0, 
             100.0, 99.0, 95.0, 100.0, 100.0, 
             100.0, 100.0, 95.0, 100.0, 100.0, 
             100.0],
    'CM #1 Inventory': [107, 158, 1379, 168, 95, 
                       66, 161, 279, 34, 1187, 
                       13, 30, 16, 30, 123, 
                       36, 8, 283, 711, 467, 
                       102, 520, 375, 5, 659, 
                       1355, 622, 438, 0, 0, 
                       9],
    'CM #2 Inventory': [65, 55, 1694, 88, 51, 
                       12, 40, 73, 11, 320, 
                       4, 23, 10, 8, 34, 
                       11, 8, 372, 440, 81, 
                       16, 241, 72, 0, 196, 
                       233, 100, 183, 0, 0, 
                       0],
    'OEM Inventory': [14, 14, 252, None, 7, 
                     8, 7, 14, 2, 63, 
                     2, 2, 2, 2, 7, 
                     2, 1, None, 36, 27, 
                     7, 63, None, None, 36, 
                     None, None, 63, None, None, 
                     1]
}

# Create the DataFrame
df = pd.DataFrame(data)

# Replace None with 0 for the inventory columns
df['OEM Inventory'] = df['OEM Inventory'].fillna(0).astype(int)

# Calculate total inventory
df['Total Inventory'] = df['CM #1 Inventory'] + df['CM #2 Inventory'] + df['OEM Inventory']

# Sort the parts by Part Number for the dropdown
sorted_parts = sorted(zip(df['Part Number'], df['Description']), key=lambda x: x[0])
part_options = {part: f"{part} - {desc}" for part, desc in sorted_parts}

# Create the Shiny app
app = App(ui=ui.page_fluid(
    ui.h1("Part Inventory Dashboard"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_select("part", "Select Part Number", part_options),
            ui.hr(),
            ui.output_ui("part_details"),
        ),
        ui.panel_main(
            ui.h3(ui.output_text("part_title")),
            ui.layout_column_wrap(
                ui.value_box(
                    "Yield",
                    ui.output_text("yield_value"),
                    showcase=ui.output_text("yield_icon"),
                    theme="bg-gradient-info-dark"
                ),
                ui.value_box(
                    "Total Inventory",
                    ui.output_text("total_inventory"),
                    showcase=ui.output_text("inventory_icon"),
                    theme="bg-gradient-success-dark"
                ),
                width=1/2
            ),
            ui.card(
                ui.card_header("Inventory Breakdown"),
                output_widget("inventory_chart")
            ),
            ui.card(
                ui.card_header("Supplier Information"),
                ui.output_ui("supplier_info")
            )
        )
    )
))

def server(input, output, session):
    
    @output
    @render.text
    def part_title():
        selected_part = input.part()
        part_data = df[df['Part Number'] == selected_part].iloc[0]
        return f"{selected_part} - {part_data['Description']}"
    
    @output
    @render.ui
    def part_details():
        selected_part = input.part()
        part_data = df[df['Part Number'] == selected_part].iloc[0]
        
        return ui.TagList(
            ui.h4("Part Details"),
            ui.p(f"Part Number: {selected_part}"),
            ui.p(f"Description: {part_data['Description']}"),
            ui.p(f"Supplier: {part_data['Supplier']}"),
        )
    
    @output
    @render.text
    def yield_value():
        selected_part = input.part()
        part_data = df[df['Part Number'] == selected_part].iloc[0]
        return f"{part_data['Yield']}%"
    
    @output
    @render.text
    def yield_icon():
        selected_part = input.part()
        part_data = df[df['Part Number'] == selected_part].iloc[0]
        if part_data['Yield'] >= 99.5:
            return ui.HTML('<i class="fa fa-check-circle" style="color: green; font-size: 24px;"></i>')
        elif part_data['Yield'] >= 98:
            return ui.HTML('<i class="fa fa-check" style="color: orange; font-size: 24px;"></i>')
        else:
            return ui.HTML('<i class="fa fa-exclamation-triangle" style="color: red; font-size: 24px;"></i>')
    
    @output
    @render.text
    def total_inventory():
        selected_part = input.part()
        part_data = df[df['Part Number'] == selected_part].iloc[0]
        return f"{int(part_data['Total Inventory'])}"
    
    @output
    @render.text
    def inventory_icon():
        selected_part = input.part()
        part_data = df[df['Part Number'] == selected_part].iloc[0]
        if part_data['Total Inventory'] > 100:
            return ui.HTML('<i class="fa fa-boxes" style="color: green; font-size: 24px;"></i>')
        elif part_data['Total Inventory'] > 20:
            return ui.HTML('<i class="fa fa-box" style="color: orange; font-size: 24px;"></i>')
        else:
            return ui.HTML('<i class="fa fa-exclamation-circle" style="color: red; font-size: 24px;"></i>')
    
    @output
    @render_widget
    def inventory_chart():
        selected_part = input.part()
        part_data = df[df['Part Number'] == selected_part].iloc[0]
        
        # Create data for the chart
        locations = ['CM #1', 'CM #2', 'OEM']
        values = [part_data['CM #1 Inventory'], part_data['CM #2 Inventory'], part_data['OEM Inventory']]
        
        # Create a pie chart
        fig = px.pie(
            names=locations,
            values=values,
            title="Inventory Distribution",
            color_discrete_sequence=px.colors.sequential.Blues_r,
            hole=0.4,
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        
        return fig
    
    @output
    @render.ui
    def supplier_info():
        selected_part = input.part()
        part_data = df[df['Part Number'] == selected_part].iloc[0]
        supplier = part_data['Supplier']
        
        # Count how many parts are from this supplier
        supplier_parts = df[df['Supplier'] == supplier]
        
        return ui.TagList(
            ui.p(f"Supplier: {supplier}"),
            ui.p(f"Total Parts from this Supplier: {len(supplier_parts)}"),
            ui.p("Other Parts from this Supplier:"),
            ui.tags.ul([
                ui.tags.li(f"{row['Part Number']} - {row['Description']}") 
                for _, row in supplier_parts.iterrows() 
                if row['Part Number'] != selected_part
            ])
        )

app.ui.head_content = ui.tags.link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css")

# Run the app
app