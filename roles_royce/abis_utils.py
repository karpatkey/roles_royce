import json
import os
import inspect

def load_abi(abi_filename):
    caller_frame = inspect.stack()[1]
    caller_filename = caller_frame[1]
    caller_file_directory = os.path.dirname(caller_filename)
    file_path = os.path.join(caller_file_directory, './abis', abi_filename)
    with open(file_path) as f:
        return json.load(f)