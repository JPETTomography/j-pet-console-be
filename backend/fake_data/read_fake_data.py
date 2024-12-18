import json
import csv


def parse_section(lines):
    header = lines[0]
    records = []
    for row in csv.DictReader(lines[1:], delimiter='\t'):
        if "" in row.keys():
            del row[""]
        records.append(row)
    return header.strip(), records

def fake_json(file_path: str) -> dict:
    result = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        section_lines = []

        for line in lines:
            if line.strip():  # Non-empty line
                section_lines.append(line)
            elif section_lines:  # Empty line indicates section boundary
                header, records = parse_section(section_lines)
                result[header] = records
                section_lines = []
        if section_lines:
            header, records = parse_section(section_lines)
            result[header] = records
    return result


if __name__=="__main__":
    file_path = "Believable fake J-PET database - Sheet1.tsv"
    print(fake_json(file_path))
