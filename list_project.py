import os
import pyperclip

def list_files(root_dir="."):
    result = []
    for folder, _, files in os.walk(root_dir):
        if "venv" in folder or "__pycache__" in folder:
            continue
        for file in files:
            if file.endswith((".py", ".ui")) or file == "__init__.py":
                rel_path = os.path.relpath(os.path.join(folder, file), root_dir)
                result.append(rel_path)
    return result

if __name__ == "__main__":
    try:
        import pyperclip
    except ImportError:
        print("Installing pyperclip...")
        os.system("pip install pyperclip")
        import pyperclip

    files = list_files()
    output = "\n".join(files)
    pyperclip.copy(output)
    print(f"📋 {len(files)} file disalin ke clipboard! Tinggal paste.")