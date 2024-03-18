# ####
# Client application to scan files in a directory with VirusTotal and save the results in JSON format.
# The application uses the vt Python package to interact with the VirusTotal API. The vt package provides a high-level interface to the VirusTotal API, allowing for easy scanning of files and retrieving analysis results.  
# The application takes three command-line arguments: the input directory containing the files to scan, the output directory to save the results, and the VirusTotal API key. 
# The main function of the application is scan_directory_and_save_results, which creates a VirusTotal client and scans each file in the input directory. The results are then saved in JSON format in the output directory.   
# The application uses asyncio to perform the scanning of multiple files concurrently, improving the overall performance of the scanning process. 
## Author: Thomas XM
import os
import vt
import json
import argparse
import asyncio

def convert_to_serializable(obj):
    if isinstance(obj, vt.Object):
        return {k: convert_to_serializable(v) for k, v in obj.to_dict().items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(v) for v in obj]
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif obj is None:
        return None
    return str(obj)  # Fallback for unknown types

async def scan_file(client, file_path, output_file_path):
    try:
        print(f"Scanning file: {file_path}")
        with open(file_path, "rb") as file:
            analysis = await client.scan_file_async(file)
        
        print(f"Waiting for analysis completion for file: {file_path}")
        await client.wait_for_analysis_completion(analysis)
        
        print(f"Retrieving analysis results for file: {file_path}")
        analysis_result = await client.get_object_async(f"/analyses/{analysis.id}")

        serializable_result = convert_to_serializable(analysis_result)

        # Save the results to the output directory in compact format
        with open(output_file_path, "w") as output_file:
            json.dump(serializable_result, output_file)

        # Save the results in pretty format
        pretty_output_file_path = os.path.splitext(output_file_path)[0] + "_pretty.json"
        with open(pretty_output_file_path, "w") as pretty_output_file:
            pretty_output_file.write(json.dumps(serializable_result, indent=4))

        print(f"Results saved for file: {file_path}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

async def scan_directory_and_save_results(input_directory, output_directory, api_key):
    async with vt.Client(api_key) as client:
        tasks = []
        for filename in os.listdir(input_directory):
            file_path = os.path.join(input_directory, filename)
            if os.path.isfile(file_path):
                output_file_path = os.path.join(output_directory, filename + ".json")
                tasks.append(scan_file(client, file_path, output_file_path))

        print(f"Starting analysis of {len(tasks)} files.")
        await asyncio.gather(*tasks)
        print("All files processed.")

def main():
    parser = argparse.ArgumentParser(description='Scan files in a directory with VirusTotal')
    parser.add_argument('input_directory', help='Path to the input directory containing files to scan')
    parser.add_argument('output_directory', help='Path to the output directory to save results')
    parser.add_argument('api_key', help='VirusTotal API key')

    args = parser.parse_args()

    if not os.path.exists(args.output_directory):
        os.makedirs(args.output_directory)

    print("Starting VirusTotal scanning process.")
    asyncio.run(scan_directory_and_save_results(args.input_directory, args.output_directory, args.api_key))
    print("Scanning process completed.")

if __name__ == "__main__":
    main()
