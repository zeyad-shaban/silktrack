import ctypes
from ctypes import wintypes

from win32more.Windows.Win32.UI.Input import RAWINPUT, RAWINPUTHEADER
from win32more.Windows.Win32.UI.Input.KeyboardAndMouse import INPUT, MOUSEINPUT
from register_rid import register_rid
from mouse_blocking_hook import MouseBlockingHook
from kalman_filter_1d import KalmanFilter1D
from constants import *
from utils import log_last_err


kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

if __name__ == "__main__":
    # intall mouse blocking hook
    mouse_hook = MouseBlockingHook()
    mouse_hook.install()

    # register RawDataInput
    hwnd = register_rid()

    # loop and filter mouse data
    filter_x = KalmanFilter1D(Q_scale=100, R=1000, mouse_hz=1000)
    filter_y = KalmanFilter1D(Q_scale=100, R=1000, mouse_hz=1000)
    prev_filtered_x = 0
    prev_filtered_y = 0

    pcbSize = ctypes.c_uint(0)
    cbSizeHeader = ctypes.sizeof(RAWINPUTHEADER)
    pDataBuff: ctypes.Array[ctypes.c_byte] = (ctypes.c_byte * 1)()

    msg = wintypes.MSG()
    try:
        while True:
            user32.GetMessageW(
                ctypes.byref(msg),
                hwnd,
                WP_INPUT,
                WP_INPUT,
            )

            if pcbSize.value == 0:
                ret = user32.GetRawInputData(
                    msg.lParam,  # hRawInput
                    RID_INPUT,  # uiCommand
                    0,  # pData
                    ctypes.byref(pcbSize),  # pcbSize
                    cbSizeHeader,  # cbSizeHeader
                )
                pDataBuff = (ctypes.c_byte * pcbSize.value)()

                if ret != 0:
                    log_last_err(status_text="Getting PCB Size err: ")
                    raise Exception("Getting PCB Size failed, check error code above")

            user32.GetRawInputData(
                msg.lParam,  # hRawInput
                RID_INPUT,  # uiCommand
                ctypes.byref(pDataBuff),  # pData
                ctypes.byref(pcbSize),  # pcbSize
                cbSizeHeader,  # cbSizeHeader
            )

            raw = ctypes.cast(pDataBuff, ctypes.POINTER(RAWINPUT)).contents
            if raw.data.mouse.ulExtraInformation == WM_SILKTRACK:
                continue

            raw_x, raw_y = raw.data.mouse.lLastX, raw.data.mouse.lLastY  # type: ignore
            filtered_x = filter_x.update(raw_x)
            filtered_y = filter_y.update(raw_y)
            dx = filtered_x
            dy = filtered_y

            prev_filtered_x = filtered_x
            prev_filtered_y = filtered_y

            mouse_input = MOUSEINPUT(
                dx=ctypes.c_long(round(dx)),  # LONG
                dy=ctypes.c_long(round(dy)),  # LONG
                mouseData=0,  # DWORD
                dwFlags=MOUSEEVENTF_MOVE,  # DWORD
                time=0,  # DWORD
                dwExtraInfo=WM_SILKTRACK,  # ULONG_PTR
            )

            if (
                user32.SendInput(
                    1,  # cInputs
                    INPUT(type=0, mi=mouse_input),  # pInputs, 0 for mouse
                    ctypes.sizeof(INPUT),  # cbSize
                )
                != 1
            ):
                log_last_err()
                raise Exception("SendInput failed, check above err code")

    except KeyboardInterrupt:
        pass
    finally:
        mouse_hook.uninstall()
