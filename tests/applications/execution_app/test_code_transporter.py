import base64
import pickle

import pytest

from roles_royce.applications.execution_app.code_transporter import CodeTransporter


def test_transporter():
    t = CodeTransporter()
    serialized = t.safe_serialize({})

    assert serialized != ""
    obj = t.safe_deserialize(serialized)

    assert obj == {}


def test_transporter_obj():
    t = CodeTransporter()
    serialized = t.safe_serialize({"a": 1, "b": 2})
    obj = t.safe_deserialize(serialized)

    assert obj == {"a": 1, "b": 2}


class ExampleObjInner:
    i = 100


class ExampleObj:
    a = "ok"
    b = 1
    c = [ExampleObjInner(), ExampleObjInner()]


def test_transporter_nested():
    t = CodeTransporter()
    serialized = t.safe_serialize(ExampleObj())
    obj = t.safe_deserialize(serialized)

    assert obj.a == "ok"
    assert obj.b == 1
    assert len(obj.c) == 2
    assert obj.c[0].i == 100


def test_transporter_tampered_msg():
    t = CodeTransporter()
    serialized = t.safe_serialize({})

    [sig, _] = serialized.split(":")
    bts = pickle.dumps({"hackerman": True})
    tampered_msg = base64.b64encode(bts).decode("utf-8")
    tampered = f"{sig}:{tampered_msg}"
    with pytest.raises(ValueError, match=r"Invalid signature"):
        t.safe_deserialize(tampered)
