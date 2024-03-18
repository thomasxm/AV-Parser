import json
import sys

def convert_json_format(input_file_path, output_file_path, sha1_checksum):
    # Read the original JSON data from the input file
    with open(input_file_path, 'r') as file:
        original_json = json.load(file)

    # The new structure to be filled with data from the original JSON
    new_json = {
        "sha1": sha1_checksum,
        "av_labels": []
    }

    # Extracting engine_name and result from each entry within the original JSON's results
    for engine, details in original_json["attributes"]["results"].items():
        if details["result"] is not None:
            new_json["av_labels"].append([details["engine_name"], details["result"]])

    # Write the new JSON structure to the output file
    with open(output_file_path, 'w') as file:
        json.dump(new_json, file, indent=4)

# Check if the correct number of arguments are provided
if len(sys.argv) == 4:
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    sha1_checksum = sys.argv[3]
    convert_json_format(input_file, output_file, sha1_checksum)
else:
    print("Usage: python script.py input.json output.json sha1_checksum")
    sys.exit(1)
