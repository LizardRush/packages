import re
import json

def parse_rush_file(file_name):
    data = {}
    output = ""  # Variable to store combined output

    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()

            is_notation_section = False
            current_notation = {}  # Store variables in a notation section

            for line in lines:
                line = line.strip()

                if line.startswith("<RTYPE"):
                    if is_notation_section:
                        data.update(current_notation)  # Update data with notation variables
                        current_notation = {}

                    is_notation_section = True
                    continue

                if is_notation_section:
                    key_value = line.split(':', 1)
                    if len(key_value) == 2:
                        key = key_value[0].strip()
                        value = key_value[1].strip()
                        current_notation[key] = value
                        output += line + "\n"  # Add notation content to output

            # Update data with the last notation section
            if is_notation_section:
                data.update(current_notation)

    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return data if data else output
def parse_rconfig(filename):
    config = {}
    current_section = None
    content_section = None

    with open(filename, 'r') as file:
        lines = file.readlines()

        for line in lines:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('//'):
                continue

            # Check for section headers [section_name]
            section_match = re.match(r'\[(\w+)\]', line)
            if section_match:
                current_section = section_match.group(1)
                if current_section == 'content':
                    content_section = {}
                    config[current_section] = content_section
                else:
                    config[current_section] = {}
                continue

            # Check for key-value pairs
            if current_section and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Attempt to parse value as JSON if enclosed in quotes
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass

                # Add key-value pair to the section
                if current_section != 'content':
                    config[current_section][key] = value
                else:
                    content_section[key] = value

    return config
