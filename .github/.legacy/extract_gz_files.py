import os
import gzip
import shutil
from pathlib import Path

def extract_gz_files_and_find_smiley():
    temp_dir = Path("temp")
    if not temp_dir.exists():
        os.makedirs(temp_dir)
        print("temp directory does not exist!")
        return
    smiley_lines = []
    gz_files = list(temp_dir.glob("*.gz"))
    
    if not gz_files:
        print("No .gz files found in temp directory!")
        return
    
    print(f"Found {len(gz_files)} .gz files to extract...")
  
    for gz_file in gz_files:
        print(f"Extracting {gz_file.name}...")
        
        try:
            output_file = temp_dir / gz_file.stem
            
            # Extract the .gz file
            with gzip.open(gz_file, 'rb') as f_in:
                with open(output_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            print(f"Successfully extracted to {output_file.name}")
            try:
                with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if ":))" in line:
                            smiley_lines.append(f"{line.strip()}")
            except Exception as e:
                print(f"Error reading {output_file}: {e}")
                
        except Exception as e:
            print(f"Error extracting {gz_file}: {e}")
    
    output_txt = temp_dir / "smiley_lines.txt"
    
    if smiley_lines:
        with open(output_txt, 'w', encoding='utf-8') as f:
            for line in smiley_lines:
                f.write(line + '\n')
        
        print(f"\nFound {len(smiley_lines)} lines containing ':))' ")
        print(f"Results saved to {output_txt}")
    else:
        print("\nNo lines containing ':))' were found in any of the extracted files.")

if __name__ == "__main__":
    extract_gz_files_and_find_smiley()
