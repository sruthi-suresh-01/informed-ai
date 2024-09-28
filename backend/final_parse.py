import json


def load_json(json_path: str) -> dict:
    with open(json_path) as json_file:
        try:
            json_data = json.load(json_file)
            if not isinstance(json_data, dict):
                raise ValueError("Loaded JSON is not a dictionary")
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            raise


def process_zip_data(zip_data: dict) -> dict:
    processed_data = {}
    for zip_code, entries in zip_data.items():
        if entries:
            first_entry = entries[0]
            combined_value = f"{first_entry['state']}Z{first_entry['zone_number']}"
            processed_data[zip_code] = combined_value
    return processed_data


def save_to_json(data: dict, output_path: str) -> None:
    with open(output_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


def main() -> None:
    # Paths to the input and output files
    input_json_path = "output_final_output.json"
    output_json_path = "zip_zone.json"

    # Load the input JSON file
    zip_data = load_json(input_json_path)

    # Process the ZIP data to create the desired format
    processed_data = process_zip_data(zip_data)

    # Save the processed data to a new JSON file
    save_to_json(processed_data, output_json_path)
    print(f"Output saved to {output_json_path}")


if __name__ == "__main__":
    main()
