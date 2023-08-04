#plate_width = 10  # Width of each well in millimeters
#plate_height = 10  # Height of each well in millimeters
#plate_spacing = 10  # Spacing between each well in millimeters
plate_spacing =9  # Spacing between well centers in mm (happens to be the same in x and y) !!! make sure that in GBRL settings (can open these through the $$ command on the Grbl Candle, $100 =$101, not sure if the number matters. I have 800)
start_x =248 # X-coordinate of the first well A1
start_y =54  # Y-coordinate of the first well A1
start_z =0  # Z-coordinate of the first well

coords = []
well_name_template = "Hybridize {}"

for i in range(1, 97):
    well_name = well_name_template.format(i)
    #x = start_x + (i - 1) % 12 * (plate_width + plate_spacing)
   # y = start_y + (i - 1) // 12 * (plate_height + plate_spacing)
    x = start_x - (i - 1) % 12 * plate_spacing
    y = start_y +(i - 1) //12 * plate_spacing 
    z = start_z
    coords.append('<well name="{}" x="{}" y="{}" z="{}" />'.format(well_name, x, y, z))
    
well_name="Bleach"
x_ssc=91
y_ssc=84
z_ssc=0
coords.append('<buffer name="{}" x="{}" y="{}" z="{}" />'.format(well_name, x_ssc, y_ssc, z_ssc))

well_name="Wash"
x_wash=21
y_wash=84
z_wash=0
coords.append('<buffer name="{}" x="{}" y="{}" z="{}" />'.format(well_name, x_wash, y_wash, z_wash))

well_name="Imaging"
x_im=152
y_im=24
z_im=0
coords.append('<buffer name="{}" x="{}" y="{}" z="{}" />'.format(well_name, x_im, y_im, z_im))



# Print the generated coordinates
for coord in coords:
    print(coord)

print(len(coords))

print(all(coords))





def generate_xml_string():
    return '<positions>\n \t' + '\n \t'.join(coords) +  '\n' + '</positions>'

#Print the generated coordinates to file
def create_xml():
    xml_string = generate_xml_string()
    with open("CncCoords.xml", "w") as f:
    # f.write('\n'.join(coords))
       f.write(xml_string)
       

create_xml()


'''
automate generation of coordinates for 96-well plate for cnc router coords 
make sure you determine where the 0,0 (origin) of the cnc router is and where you want 
to place your plate before calculating the wells, adjust code based on the starting
point of your 96 well plate

Sedona Murphy
2023-05-22
Tonia Hafner
2023-08-01
''' 
