from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent.parent
import sys
sys.path.append(str(ROOT_DIR))

import json

from src.rcs660s import RCS660S
from src.ccid_command.get_firmware_version import GetFirmwareVersion
from src.utils import print_hex, extract_bytes

def test_get_firmware_version():

    port = "/dev/ttyAMA0"
    baudrate = 115200
    timeout_fps = 16

    rcs660s = RCS660S(port=port, baudrate=baudrate, timeout_fps=timeout_fps)
    rcs660s.create_command_frame(ccid_command=GetFirmwareVersion(), is_debug=True)
    rcs660s.send_command_frame()

    response = rcs660s.read_response()
    print("status: ", response["status"], "message: ", response["message"])
    print_hex("apdu_response: ", response["apdu_response"])


if __name__ == "__main__":
    test_get_firmware_version()