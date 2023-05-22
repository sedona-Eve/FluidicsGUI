plate_width = 10  # Width of each well in millimeters
plate_height = 10  # Height of each well in millimeters
plate_spacing = 10  # Spacing between each well in millimeters
start_x = 10  # X-coordinate of the first well
start_y = 10  # Y-coordinate of the first well
start_z = 0  # Z-coordinate of the first well

coords = []
well_name_template = "Hybridize {}"

for i in range(1, 97):
    well_name = well_name_template.format(i)
    x = start_x + (i - 1) % 12 * (plate_width + plate_spacing)
    y = start_y + (i - 1) // 12 * (plate_height + plate_spacing)
    z = start_z
    coords.append('<well name="{}" x="{}" y="{}" z="{}" />'.format(well_name, x, y, z))

# Print the generated coordinates
for coord in coords:
    print(coord)
    
'''

automate generation of coordinates for 96-well plate for cnc router coords 
make sure you determine where the 0,0 (origin) of the cnc router is and where you want 
to place your plate before calculating the wells, adjust code based on the starting
point of your 96 well plate

Sedona Murphy
2023-05-22
''' 
