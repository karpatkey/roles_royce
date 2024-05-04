import base64
import hashlib
import hmac
import os
import pickle


def priv_key():
    return os.urandom(64)


class CodeTransporter:
    PRIV_KEY = priv_key()

    def safe_serialize(self, obj: object):
        bts = pickle.dumps(obj)
        sig = self.__sign(bts)
        o = self.__encode64(bts)
        return f"{sig}:{o}"

    def safe_deserialize(self, data: str):
        [sig, msg] = data.split(":")
        bts = self.__decode64(msg)
        if not self.__is_signed(bts, sig):
            raise ValueError("CodeTransporter: Invalid signature")

        return pickle.loads(bts)

    def __sign(self, message: bytes) -> str:
        return hmac.new(key=self.PRIV_KEY, msg=message, digestmod=hashlib.sha1).hexdigest()

    def __encode64(self, o: bytes) -> str:
        return base64.b64encode(o).decode("utf-8")

    def __decode64(self, o: str) -> bytes:
        return base64.b64decode(o.encode("utf-8"))

    def __is_signed(self, message: bytes, sig: str):
        hmac_digest = hmac.new(key=self.PRIV_KEY, msg=message, digestmod=hashlib.sha1).hexdigest()
        return hmac.compare_digest(sig, hmac_digest)
