import os
import difflib  # noqa
import PIL

import os

def list_directory(directory, prefix=""):
    """Recursively lists a directory structure and prints file contents"""
    try:
        items = os.listdir(directory)
        items.sort()
    except PermissionError:
        print(prefix + "└── [Permission Denied]")
        return
    
    for index, item in enumerate(items):
        path = os.path.join(directory, item)
        connector = "└── " if index == len(items) - 1 else "├── "
        print(prefix + connector + item)
        
        if os.path.isdir(path):
            new_prefix = prefix + ("    " if index == len(items) - 1 else "│   ")
            list_directory(path, new_prefix)
        else:
            # Try reading the file
            try:
                print(prefix + "    " + "▼ File Content ▼")
                with open(path, "r", encoding="utf-8") as file:
                    for line in file:
                        print(prefix + "    " + line.rstrip())  # Preserve formatting
                print(prefix + "    " + "▲ End of File ▲\n")
            except Exception as e:
                print(prefix + "    " + f"[Could not read file: {e}]\n")

# Change the path to the folder you want to scan
root_dir = "./www/"  # Replace with your project path
print(root_dir)
list_directory(root_dir)
