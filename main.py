from config_reader import ConfigReader
from utils import DualOutput, extract_files_from_zip, file_exists, get_program_path, process_exists
import traceback
import logging
import sys

def setup_logging():
    logging.basicConfig(filename='output.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger().addHandler(console)

#."C:\Users\rober\Documents\Programming\GCB Decal Installer\venv\Scripts\Activate.ps1"
# pyinstaller --onefile --add-data="decals-20231006T184738Z-001.zip;." main.py

# Redirect stdout to our custom class
sys.stdout = DualOutput('output.log')

class DecalInstaller:
    def __init__(self):
        self.path = ""

    def check_bakkesmod(self):
        # Check if BakkesMod is running
        bakkes_status = process_exists("BakkesMod.exe")

        if bakkes_status:
            raise Exception("Bakkes mod is open. Please close Bakkes Mod before running the program.")

        # Ensure BakkesMod is installed
        registry_key = r"HKEY_CURRENT_USER\Software\BakkesMod\AppPath"
        path = get_program_path(registry_key)
        if path:
            logging.info(f"Bakkes Mod installation found. \nInstall is located at: {path}\n")
            self.path = path
        else:
            logging.warning("The program couldn't find Bakkes Mod installation or Bakkes mod is not installed.")
            raise Exception("Can't find Bakkes mod")

    def check_alphaconsole_plugin(self):
        # Make sure the AlphaConsole Plugin is installed and initialized
        directory = f"{self.path}\\plugins"
        filename = "ACPlugin.dll"

        if file_exists(directory, filename):
            logging.info(f"The file '{filename}' exists in the directory '{directory}'.\n Alpha Console is installed and initialized.\n")
        else:
            logging.warning(f"The file '{filename}' does not exist in the directory '{directory}'.")
            raise Exception("Error with AlphaConsole Bakkes Mod Plugin.")

    def install_decals(self):
        # Unzip and install decals
        logging.info("Extracting decal files and placing in DecalTextures...")
        zip_path = "decals-20231006T184738Z-001.zip"
        folder_name = "decals"
        output_dir = f"{self.path}\\data\\acplugin\\DecalTextures"

        extract_files_from_zip(zip_path, folder_name, output_dir)
        logging.info("Successfully extracted and placed in directory.")

    def update_config(self):
        # Set config key and values
        logging.info("Setting config...")
        config = ConfigReader(f"{self.path}\\cfg\\config.cfg")
        config.read()

        config.set("acplugin_decaltexture_selectedtexture_blue", "GCBOctaneHome")
        config.set("acplugin_decaltexture_selectedtexture_orange", "GCBOctaneHome")
        config.set("cl_itemmod_enabled", "1")
        config.set("cl_itemmod_code", "hAPCB1wABMIriAECAAA=", "Current loadout code")
        config.save()
        logging.info("Config set and saved.")

if __name__ == "__main__":
    setup_logging()
    logging.info("[Made by Discord User im_rob for the GCB Server <3]")

    try:
        installer = DecalInstaller()
        installer.check_bakkesmod()
        installer.check_alphaconsole_plugin()
        installer.install_decals()
        installer.update_config()
    except Exception as e:
        logging.error(f"An error occurred: {e}\n{traceback.format_exc()}")
    finally:
        input("Press any key to exit...")
