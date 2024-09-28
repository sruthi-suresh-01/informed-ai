import json


def load_zip_to_location(json_path: str) -> dict:
    with open(json_path) as json_file:
        try:
            json_data = json.load(json_file)
            if not isinstance(json_data, dict):
                raise ValueError("Loaded JSON is not a dictionary")
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            raise


def process_line(line: str, zip_to_location: dict, final_output: dict) -> None:
    parts = line.strip().split("|")
    state = parts[0]
    zone_number = parts[1]
    county = parts[5]  # COUNTY is the 6th field in the line

    for zip_code, (zip_state, zip_county) in zip_to_location.items():
        if zip_state == state and zip_county == county:
            if zip_code not in final_output:
                final_output[zip_code] = []
            final_output[zip_code].append({"state": state, "zone_number": zone_number})


def process_data_file(data_file_path: str, zip_to_location: dict) -> dict:
    final_output: dict = {}
    with open(data_file_path) as data_file:
        for line in data_file:
            process_line(line, zip_to_location, final_output)
    return final_output


def save_to_json(data: dict, output_path: str) -> None:
    with open(output_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


def main() -> None:
    # Paths to the input files
    json_path = "zip_to_county.json"
    data_file_path = "zonedata.txt"
    output_file_path = "output_final_output.json"

    # Load the ZIP to location mapping
    zip_to_location = load_zip_to_location(json_path)

    # Process the data file to extract relevant information
    final_output = process_data_file(data_file_path, zip_to_location)

    # Save the final output to a JSON file
    save_to_json(final_output, output_file_path)
    print(f"Output saved to {output_file_path}")


if __name__ == "__main__":
    main()
