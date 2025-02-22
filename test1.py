import os

# Specify the folder you want to scan
root_dir = "./"  # Change this to your project's path

# List of folders or files to ignore
exclude_list = ["node_modules", "__pycache__", ".git", ".vscode",".venv",".idea","py-gpt"]  # Add any files or folders you want to ignore

def list_directory(directory, prefix=""):
    """Recursively lists a directory structure while ignoring specific files/folders."""
    try:
        items = sorted(os.listdir(directory))
    except PermissionError:
        return  # Skip folders with restricted access

    items = [item for item in items if item not in exclude_list]  # Exclude unwanted files/folders

    for index, item in enumerate(items):
        path = os.path.join(directory, item)
        connector = "└── " if index == len(items) - 1 else "├── "
        print(prefix + connector + item)

        if os.path.isdir(path):
            new_prefix = prefix + ("    " if index == len(items) - 1 else "│   ")
            list_directory(path, new_prefix)

print(root_dir)
list_directory(root_dir)








# import os
# import difflib  # noqa
# import PIL

# import os

# def list_directory(directory, prefix=""):
#     """Recursively lists a directory structure and prints file contents"""
#     try:
#         items = os.listdir(directory)
#         items.sort()
#     except PermissionError:
#         print(prefix + "└── [Permission Denied]")
#         return
    
#     for index, item in enumerate(items):
#         path = os.path.join(directory, item)
#         connector = "└── " if index == len(items) - 1 else "├── "
#         print(prefix + connector + item)
        
#         if os.path.isdir(path):
#             new_prefix = prefix + ("    " if index == len(items) - 1 else "│   ")
#             list_directory(path, new_prefix)
#         else:
#             # Try reading the file
#             try:
#                 print(prefix + "    " + "▼ File Content ▼")
#                 with open(path, "r", encoding="utf-8") as file:
#                     for line in file:
#                         print(prefix + "    " + line.rstrip())  # Preserve formatting
#                 print(prefix + "    " + "▲ End of File ▲\n")
#             except Exception as e:
#                 print(f"[Could not read file: ]\n")

# # Change the path to the folder you want to scan
# root_dir = "./"  # Replace with your project path
# print(root_dir)
# list_directory(root_dir)
