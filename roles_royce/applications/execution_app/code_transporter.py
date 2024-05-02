import base64
import pickle

from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


def priv_key():
    random_generator = Random.new().read
    prv = RSA.generate(1024, random_generator)
    return prv


class CodeTransporter:
    PRIV_KEY = priv_key()

    def safe_serialize(self, obj: object):
        bts = pickle.dumps(obj)
        sig = self.__sign(bts)
        sig = self.__encode64(sig)
        o = self.__encode64(bts)
        return f"{sig}:{o}"

    def safe_deserialize(self, data: str):
        [sig, msg] = data.split(":")
        sig = self.__decode64(sig)
        bts = self.__decode64(msg)
        if not self.__is_signed(bts, sig):
            raise ValueError("CodeTransporter: Invalid signature")

        return pickle.loads(bts)

    def __signer(self):
        return PKCS1_v1_5.new(self.PRIV_KEY)

    def __sign(self, message: bytes) -> bytes:
        h = SHA256.new(message)
        sig = self.__signer().sign(h)
        return sig

    def __encode64(self, o: bytes) -> str:
        return base64.b64encode(o).decode("utf-8")

    def __decode64(self, o: str) -> bytes:
        return base64.b64decode(o.encode("utf-8"))

    def __is_signed(self, message: bytes, sig: bytes):
        digest = SHA256.new(message)
        return self.__signer().verify(digest, sig)
