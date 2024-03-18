
## This function takes a JSON file as input and processes it to extract data. It also corrects the JSON format and writes the corrected JSON to a new file.
## The output json file can be further parsed by AVClass to generate a voted label for the file.
## Author: Thomas XM
import json
import sys
import ast
import argparse
import os

def correct_json_format(data):
    try:
        if isinstance(data['attributes'], str):
            data['attributes'] = ast.literal_eval(data['attributes'])
        return data
    except (ValueError, SyntaxError) as e:
        print(f"Error evaluating string as Python literal: {e}")
        return None

def process_json_file(input_file_path):
    try:
        with open(input_file_path, 'r') as file:
            data = json.load(file)
        
        corrected_data = correct_json_format(data)
        if corrected_data is None:
            print("No corrected data to write.")
            return None

        output_file_path = "pretty_" + os.path.basename(input_file_path)
        with open(output_file_path, 'w') as file:
            json.dump(corrected_data, file, indent=4)
        print(f"Corrected JSON has been written to {output_file_path}")

        return corrected_data, output_file_path
    except FileNotFoundError:
        print(f"The file {input_file_path} does not exist.")
        return None, None
    except json.JSONDecodeError as e:
        print(f"Error reading JSON data from {input_file_path}: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, None

def calculate_rates(json_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)

        stats = data['attributes']['stats']
        total = sum(value for key, value in stats.items())
        malicious = stats['malicious']
        evasion_sum = total - malicious

        detection_rate = malicious / total if total != 0 else 0
        evasion_rate = evasion_sum / total if total != 0 else 0

        return detection_rate, evasion_rate
    except Exception as e:
        print(f"An error occurred while calculating the rates: {e}")
        return None, None

def extract_unique_values(json_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)

        results = data['attributes']['results']
        unique_methods = set()
        unique_results = set()

        for engine, details in results.items():
            if 'method' in details and details['method']:
                unique_methods.add(details['method'])
            if 'result' in details and details['result']:
                unique_results.add(details['result'])

        return unique_methods, unique_results
    except Exception as e:
        print(f"An error occurred while extracting unique values: {e}")
        return None, None

def convert_json_format(original_json, output_file_path, sha1_checksum):
    new_json = {
        "sha1": sha1_checksum,
        "av_labels": []
    }

    for engine_data in original_json["attributes"]["results"].values():
        if engine_data["result"] is not None:
            new_json["av_labels"].append([engine_data["engine_name"], engine_data["result"]])

    with open(output_file_path, 'w') as file:
        json.dump(new_json, file, separators=(',', ':'))
    print(f"New file structure for AVClass has been written to {output_file_path}")

def format_and_print_list(title, items):
    print(f"{title}:")
    for item in sorted(items):
        print(f" - {item}")

def main():
    parser = argparse.ArgumentParser(description='Process JSON file and extract data')
    parser.add_argument('json_file', type=str, help='Path to the JSON file')
    parser.add_argument('sha1_checksum', type=str, help='SHA1 checksum for the output file')
    parser.add_argument('output_directory', type=str, help='Output directory to save formatted files')
    args = parser.parse_args()

    corrected_data, corrected_file_path = process_json_file(args.json_file)
    if corrected_data:
        detection_rate, evasion_rate = calculate_rates(corrected_file_path)
        unique_methods, unique_results = extract_unique_values(corrected_file_path)

        print(f"Detection Rate: {detection_rate}")
        print(f"Evasion Rate: {evasion_rate}\n")

        if unique_methods is not None and unique_results is not None:
            format_and_print_list("Unique Methods", unique_methods)
            print()  # Add a blank line for better separation
            format_and_print_list("Unique Results", unique_results)

        new_format_file_name = "avclassLbformat_" + os.path.basename(args.json_file)
        new_format_file_path = os.path.join(args.output_directory, new_format_file_name)
        convert_json_format(corrected_data, new_format_file_path, args.sha1_checksum)

if __name__ == "__main__":
    main()
