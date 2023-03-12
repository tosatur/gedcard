from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser
from datetime import datetime
import argparse

parser = argparse.ArgumentParser(description="Create barcodes.")
parser.add_argument("-i", "--input", help="GEDCOM file to input.")
parser.add_argument("-o", "--output", help="Path to output VCard to.")
parser.add_argument("-f", "--filename", help="Filename to save as.")
parser.add_argument("-d", "--includedesceased", help="Create contacts for deceased people.", action="store_true")
parser.add_argument("-g", "--includegender", help="Include gender in contacts.", action="store_true")
args = parser.parse_args()

def make_vcard (first_name, last_name, birth_date, death_date_line, gender_line):
    return (f"""
BEGIN:VCARD
VERSION:4.0
N:{last_name};{first_name}
FN:{first_name} {last_name}
BDAY:{birth_date}{death_date_line}{gender_line}
REV:1
END:VCARD
"""
    )

def parse_date(date_string):
    date_string = date_string.strip().replace('-', '')
    if not date_string or len(date_string) < 4:
        # Return None if input is empty or invalid
        return None
    date_format = "%Y" if len(date_string) == 4 else "%b %Y" if len(date_string) <= 7 else "%d %b %Y"
    try:
        date_object = datetime.strptime(date_string, date_format)
        return date_object.strftime("%Y%m%d")
    except ValueError:
        # Return None if input cannot be converted to a date object
        return None


# Path to `.ged` file
input_path = args.input

#parse output path
if args.output[-1] != "\\" or "/":
    args.output += "\\"

#parse filename
if args.filename[-4:] != ".vcf":
    args.filename += ".vcf"

#write to path/filename
output_path = args.output + args.filename

# Initialize parser
gedcom_parser = Parser()

# Parse file
gedcom_parser.parse_file(input_path)

root_child_elements = gedcom_parser.get_root_child_elements()

#open output file
f = open(output_path, "w", encoding="utf-8")

# Iterate through all root child elements
for element in root_child_elements:

    # Is the `element` an actual `IndividualElement`? (Allows usage of extra functions such as `surname_match` and `get_name`.)
    if isinstance(element, IndividualElement):
        if element.is_deceased() == False or args.includedesceased == True:
            #get name
            name = element.get_name()
            first_name = name[0]
            last_name = name[1]

            #get birth date
            birth_info = element.get_birth_data()
            birth_date = parse_date(birth_info[0])

            #get death date
            if element.is_deceased() == True:
                death_info = element.get_death_data()
                death_date = parse_date(death_info[0])
                death_date_line = f"\nDEATHDATE:{death_date}"
            elif element.is_deceased() == False:
                death_date_line = ""
            
            #get gender
            if args.includegender == True:
                gender = element.get_gender()
                gender_line = f"\nGENDER:{gender}"
            elif args.includegender == False:
                gender_line = ""

            #write to file
            f.write(make_vcard(first_name, last_name, birth_date, death_date_line, gender_line))