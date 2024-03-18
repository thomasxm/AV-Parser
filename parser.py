## Description: This script automates the process of scanning, formatting, and labeling files.
## It takes an input directory containing .exe files, a VirusTotal API key, and an output directory for JSON results.
## It also takes an optional labeler path to run the labeler on the output directory.
## The script calculates the SHA1 checksum of each file in the input directory and stores it in a dictionary.
## It then runs the VirusTotal client on the input directory and saves the results in the output directory.
## After processing the JSON files, it runs the formatter on the output directory to generate a voted label for each file.
## Finally, it runs the labeler on the output directory if a labeler path is provided.
## The script is executed from the command line with the input directory, output directory, VirusTotal API key, and optional labeler path as arguments.
## The main function of the script takes the command-line arguments, processes the JSON files, and runs the labeler on the output directory.
## The execute_vt_client function runs the VirusTotal client on the input directory and saves the results in the output directory.
## Author: Thomas XM
import os
import hashlib
import subprocess
import argparse
import shutil
import tempfile

def calculate_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(65536)  # Read in 64k chunks
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def run_labeler(labeler_path, output_directory):
    if labeler_path:
        abs_labeler_path = os.path.abspath(labeler_path)

        if os.path.isfile(abs_labeler_path):
            labeler_directory = os.path.dirname(abs_labeler_path)
            with tempfile.TemporaryDirectory() as temp_dir:
                for filename in os.listdir(output_directory):
                    if filename.startswith("avclassLbformat_") and filename.endswith(".json"):
                        shutil.copy(os.path.join(output_directory, filename), temp_dir)

                labeler_command = ["python3", abs_labeler_path, "-d", temp_dir, "-t", "-o", "output.txt"]
                subprocess.run(labeler_command, check=True)

                # Assuming output.txt is correctly located in the current working directory
                output_file_path = "output.txt"
                if os.path.isfile(output_file_path):
                    with open(output_file_path, "r") as file:
                        for line in file:
                            print(line, end='')  # Print each line directly
                else:
                    print("No output.txt file found.")


        else:
            print(f"Labeler script not found at {abs_labeler_path}. Skipping labeling step.")
    else:
        print("Labeler path not provided. Skipping labeling step.")



def execute_vt_client(input_directory, output_directory, vt_api_key):
    subprocess.run(["python3", "5_vt_client.py", input_directory, output_directory, vt_api_key], check=True)

# run formater.py to get the AV class result
def run_formatter(output_directory, hashes):
    for filename in os.listdir(output_directory):
        if filename.endswith(".json"):
            json_file_path = os.path.join(output_directory, filename)
            exe_name = os.path.splitext(filename)[0]
            sha1_checksum = hashes.get(exe_name, "")
            if sha1_checksum:
                subprocess.run(["python3", "formater.py", json_file_path, sha1_checksum, output_directory], check=True)


def main():

    parser = argparse.ArgumentParser(description="Automate the process of scanning, formatting, and labeling files")
    parser.add_argument('input_directory', help='Path to the input directory containing .exe files')
    parser.add_argument('output_directory', help='Path to the output directory for JSON results')
    parser.add_argument('vt_api_key', help='VirusTotal API key')
    parser.add_argument('-l', '--labeler', type=str, help='Absolute path to the labeler.py script', default="")

    args = parser.parse_args()

    hashes = {}
    for filename in os.listdir(args.input_directory):
        file_path = os.path.join(args.input_directory, filename)
        if os.path.isfile(file_path) and file_path.endswith(".exe"):
            hashes[filename] = calculate_sha1(file_path)

    execute_vt_client(args.input_directory, args.output_directory, args.vt_api_key)

    # After processing the JSON files
    run_formatter(args.output_directory, hashes)

    # Run the labeler on the output directory
    run_labeler(args.labeler, args.output_directory)

if __name__ == "__main__":
    main()
