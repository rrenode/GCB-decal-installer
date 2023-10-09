import subprocess
import zipfile
import winreg
import sys
import os

def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())

def get_program_path(registry_key):
    try:
        # Split the registry key into the hive and subkey
        hive_str, subkey = registry_key.split("\\", 1)
        
        # Map the hive string to the appropriate winreg constant
        hive_map = {
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
            "HKEY_USERS": winreg.HKEY_USERS,
            "HKEY_PERFORMANCE_DATA": winreg.HKEY_PERFORMANCE_DATA,
            "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
            "HKEY_DYN_DATA": winreg.HKEY_DYN_DATA
        }
        hive = hive_map.get(hive_str.upper())
        
        # Open the registry key and read the value
        with winreg.OpenKey(hive, subkey) as key:
            program_path, _ = winreg.QueryValueEx(key, "BakkesModPath")
            return program_path
    except FileNotFoundError:
        print(f"The registry key '{registry_key}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def file_exists(directory, filename):
    # Construct the full path to the file
    file_path = os.path.join(directory, filename)
    
    # Check if the file exists
    return os.path.isfile(file_path)

def get_resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def extract_files_from_zip(zip_name, folder_name, output_dir, num_files=10):
    if not os.path.exists(output_dir):
        print("It appears the AlphaConsole plugin has not been initalized. Please run Rocket League with Bakkes Mod at least once after installing Alpha Console.")

    zip_path = get_resource_path(zip_name)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Filter out the files from the specified folder
        files_to_extract = [f for f in zip_ref.namelist() if f.startswith(folder_name) and not f.endswith('/')]
        
        # Extract the first 'num_files' files from the list
        for file in files_to_extract[:num_files]:
            # Extract the file to the output directory
            zip_ref.extract(file, output_dir)
            # Move the file from the 'decals' subdirectory to the main output directory
            extracted_file_path = os.path.join(output_dir, file)
            new_file_path = os.path.join(output_dir, os.path.basename(file))
            
            # Check if the destination file already exists and delete it if it does
            if os.path.exists(new_file_path):
                os.remove(new_file_path)
            
            os.rename(extracted_file_path, new_file_path)
            
            # Remove the 'decals' subdirectory if it's empty
            try:
                os.rmdir(os.path.join(output_dir, folder_name))
            except OSError:
                pass  # Directory not empty or not present, do nothing

class DualOutput:
    def __init__(self, file_name):
        self.terminal = sys.stdout
        self.log = open(file_name, 'w')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # Flush method so that it can be used with print's flush argument
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()