import json

# ai generated this in 5 secs cuz im too lazy
def deduplicate_punishments(input_file, output_file):
    try:
        # Load the data from the file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        seen_uuids = set()
        deduplicated_data = []

        # Iterate and filter, keeping the first occurrence
        for entry in data:
            uuid = entry.get("uuid")
            if uuid not in seen_uuids:
                deduplicated_data.append(entry)
                seen_uuids.add(uuid)
        
        # Write the cleaned data to a new file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(deduplicated_data, f, indent=2)
            
        print(f"Success! Deduplication complete.")
        print(f"Original count: {len(data)}")
        print(f"Final count: {len(deduplicated_data)}")
        
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{input_file}'.")

# Change the last line of your script to this:
import os

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to the script's location
input_path = os.path.join(script_dir, 'punishments.json')
output_path = os.path.join(script_dir, 'deduplicated_punishments.json')

# Run the function
deduplicate_punishments(input_path, output_path)