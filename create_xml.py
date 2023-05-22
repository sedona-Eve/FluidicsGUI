'''
quick code to generate different hybridization protocols for 96 rounds 

Sedona Murphy
2023-05-22
'''

def generate_xml_string():
    return '<protocol>\n' + ''.join([
        f'  <step name="Hybridization {i}">\n'
        f'    <move well="Well {i}" />\n'
        f'    <pause time="3" />\n'
        f'    <pump name="Pump 1" speed="5" time="30" />\n'
        f'    <pause time="900" />\n'
        f'    <move buffer="Wash" />\n'
        f'    <pump name="Pump 1" speed="5" time="120" />\n'
        f'    <pause time="3" />\n'
        f'    <move buffer="Bleach" />\n'
        f'    <pump name="Pump 1" speed="5" time="120" />\n'
        f'    <pause time="3" />\n'
        f'    <move buffer="Imaging" />\n'
        f'    <pump name="Pump 1" speed="5" time="30" />\n'
        f'    <pause time="20" />\n'
        f'  </step>\n'
        for i in range(1, 97)
    ]) + '</protocol>'

def create_xml():
    xml_string = generate_xml_string()
    with open("hybridizations.xml", "w") as f:
        f.write(xml_string)

create_xml()
