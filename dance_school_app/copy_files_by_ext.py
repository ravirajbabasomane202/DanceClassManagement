import os

# Root folder where you want to search
root_dir = "."

# Output file
output_file = "all_files_combined.txt"

# File extensions to include
extensions = {".py", ".js", ".css", ".html"}

with open(output_file, "w", encoding="utf-8") as outfile:
    for folder, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(folder, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                        outfile.write(f"File: {file_path}\n")
                        outfile.write(infile.read())
                        outfile.write("\n" + "="*50 + "\n\n")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

print(f"✅ All files combined into {output_file}")
