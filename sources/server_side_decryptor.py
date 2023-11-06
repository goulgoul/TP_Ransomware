import logging
from operator import xor
from re import sub
from xorcrypt import xorfile
from pathlib import Path
import sys
 

class ServerSideDecryptor:
    def __init__(self, path) -> None:
        self._path = path
        self._log = logging.getLogger(self.__class__.__name__)
        return None

    def get_files(self, filter: str, dir_path: str) -> list[str]:
        # return all files matching the filter
        """files_list is a list containing the paths of every file found recursively by the rglob() function in the file system.
        The paths are stored as strings."""

        files_list = [str(p) for p in list(Path(dir_path).rglob(filter))]

        return files_list
    
    def get_subfolders(self, root_path: str) -> list[str]:
        subfolder_list = [str(sf) for sf in list(Path(root_path).glob("*"))]

        return subfolder_list

    def get_key(self, path):
        key_path = f"{path}/key.bin"
        if not Path(key_path).exists():
            raise Exception(f"{key_path}: no such file or directory")
        with open(key_path, "rb") as key_file:
            return key_file.read()

    def xorfiles(self, files: list[str], key: bytes) -> None:
        # xor a list for file
        self._log.debug("XORFILES FUNCTION")
        [xorfile(file, key) for file in files]
        return None
    
    def decrypt_all_files(self) -> None:
        for subfolder in self.get_subfolders(self._path):
            self._log.debug(subfolder)
            key = self.get_key(subfolder)
            self._log.debug(key)
            leaked_files_path = f"{subfolder}/leaked_files"
            file_list = self.get_files("*", leaked_files_path)
            self._log.debug(file_list)
            self.xorfiles(file_list, key)

        return None

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        raise Exception("Missing cnc_data path. Please enter it before running the decryptor.")
    if "--verbose" in sys.argv:
        logging.basicConfig(level=logging.DEBUG)
    decryptor = ServerSideDecryptor(sys.argv[1])
    decryptor.decrypt_all_files()
    
