import json
import sys
import ast

def fix_json_attributes(input_file_path, output_file_path):
    try:
        with open(input_file_path, 'r') as file:
            data = json.load(file)

        # Attempt to manually parse and fix the 'attributes' field
        if 'attributes' in data:
            try:
                # Using ast.literal_eval to safely evaluate the string
                attributes = ast.literal_eval(data['attributes'])
                if isinstance(attributes, dict):
                    data['attributes'] = attributes
                else:
                    raise ValueError("Parsed 'attributes' is not a dictionary.")
            except (SyntaxError, ValueError) as e:
                print(f"Error: Unable to parse 'attributes' as JSON. {e}")
                return

        with open(output_file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"File successfully fixed and saved to '{output_file_path}'.")

    except FileNotFoundError:
        print(f"Error: File '{input_file_path}' not found.")
    except json.JSONDecodeError:
        print(f"Error: File '{input_file_path}' contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_json_file_path> <output_json_file_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    fix_json_attributes(input_file_path, output_file_path)

