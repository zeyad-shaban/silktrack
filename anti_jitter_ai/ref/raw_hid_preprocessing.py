import ctypes
from ctypes import wintypes

from win32more.Windows.Win32.UI.Input.KeyboardAndMouse import INPUT, MOUSEINPUT
from kalman_filter_1d import KalmanFilter1D
from constants import *
from structures import *

import numpy as np
import matplotlib.pyplot as plt

OBSERVING_MODE = False

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

user32.GetRawInputData.restype = ctypes.c_uint
user32.CreateWindowExW.restype = wintypes.HWND


def log_last_err(status_text="err code"):
    err_code = kernel32.GetLastError()
    print(f"{status_text}: {err_code} - {ctypes.FormatError(err_code)}")


# Create the HWND (to have the message queue to receive the WP_INPUT at) Create as message only window https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-createwindowexw
hwnd = user32.CreateWindowExW(
    0,  # dwExStyle
    "Static",  # lpClassName
    0,  # lpWindowName
    0,  # dwStyle
    0,  # X
    0,  # Y
    0,  # nWidth
    0,  # nHeight
    HWND_MESSAGE,  # hWndParent
    0,  # hMenu
    0,  # hInstance
    0,  # lpParam
)

# In case of failure call GetLastError https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-getlasterror
# check for error code https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes
print(f"hwnd CraeteWindowExW response: {hwnd}")
log_last_err()

rid = RAWINPUTDEVICE(
    usUsagePage=0x0001,
    usUsage=0x0002,
    dwFlags=RIDEV_INPUTSINK,
    hwndTarget=hwnd,
)


# Registering: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerrawinputdevices
rid_call_res = user32.RegisterRawInputDevices(ctypes.byref(rid), 1, ctypes.sizeof(rid))

print(f"Call register raw input device result: {rid_call_res}")
log_last_err("RegisterRID call Err")

# Receive the message from message queue through GetMessage https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getmessage

out_msg = MSG()

# hunt for WM_INPUT https://learn.microsoft.com/en-us/windows/win32/inputdev/wm-input
get_msg_success = user32.GetMessageW(
    ctypes.byref(out_msg),  # [out]          LPMSG lpMsg
    hwnd,  # [in, optional] HWND  hWnd
    WP_INPUT,  # [in]           UINT  wMsgFilterMin
    WP_INPUT,  # [in]           UINT  wMsgFilterMax
)
print(f"GetMessage Success Response: {get_msg_success}")
log_last_err()

print(f"msg: {out_msg}")

pcbSize = ctypes.c_uint(0)
cbSizeHeader = ctypes.sizeof(RAWINPUTHEADER)
pDataBuff: ctypes.Array[ctypes.c_byte] = (ctypes.c_byte * 1)()

raw_data_x = []
raw_data_y = []
filtered_data_x = []
filtered_data_y = []

filter_x = KalmanFilter1D(Q_scale=130, R=1000, mouse_hz=1000)
filter_y = KalmanFilter1D(Q_scale=130, R=1000, mouse_hz=1000)

prev_filtered_x = 0
prev_filtered_y = 0
while True:
    get_msg_success = user32.GetMessageW(
        ctypes.byref(out_msg),  # [out]          LPMSG lpMsg
        hwnd,  # [in, optional] HWND  hWnd
        WP_INPUT,  # [in]           UINT  wMsgFilterMin
        WP_INPUT,  # [in]           UINT  wMsgFilterMax
    )

    if pcbSize.value == 0:
        ret = user32.GetRawInputData(
            out_msg.lParam,  # hRawInput
            RID_INPUT,  # uiCommand
            0,  # pData
            ctypes.byref(pcbSize),  # pcbSize
            cbSizeHeader,  # cbSizeHeader
        )
        pDataBuff = (ctypes.c_byte * pcbSize.value)()
        print(f"getrawinputdate - pcbSize setting: {ret}")
        log_last_err(status_text="Err for getting pcbSize")
        assert ret == 0, "GetRawInputData unsuccesfull, couldn't retreive pcbSize"

    # get raw (unprocessed raw HID data, exactly as sensor reports) https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getrawinputdata
    user32.GetRawInputData(
        out_msg.lParam,  # hRawInput
        RID_INPUT,  # uiCommand
        ctypes.byref(pDataBuff),  # pData
        ctypes.byref(pcbSize),  # pcbSize
        cbSizeHeader,  # cbSizeHeader
    )
    # log_last_err()

    processed_x, processed_y = out_msg.pt.x, out_msg.pt.y

    raw = ctypes.cast(pDataBuff, ctypes.POINTER(RAWINPUT)).contents

    # skip our own data
    if raw._DUMMYUNIONNAME.mouse.ulExtraInformation == 0x5E1D:
        continue

    raw_x, raw_y = raw._DUMMYUNIONNAME.mouse.lLastX, raw._DUMMYUNIONNAME.mouse.lLastY  # type: ignore
    filtered_x = filter_x.update(raw_x)
    filtered_y = filter_y.update(raw_y)

    if OBSERVING_MODE:
        raw_data_x.append(raw_x)
        raw_data_y.append(raw_y)
        filtered_data_x.append(filtered_x)
        filtered_data_y.append(filtered_y)

        print(f"{len(raw_data_x)} / 300")
        if len(raw_data_x) >= 300:
            break

    else:  # Send Input back to fix mouse https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput
        dx = filtered_x - prev_filtered_x
        dy = filtered_y - prev_filtered_y
        # dx = dy = 0
        print(f"dx: {dx:.2f}, dy: {dy:.2f}, filtered_x: {filtered_x:.2f}, filtered_y: {filtered_y:.2f}, prev_filtered_x: {prev_filtered_x:.2f}, prev_filtered_y: {prev_filtered_y:.2f}")

        prev_filtered_x = filtered_x
        prev_filtered_y = filtered_y

        mouse_input = MOUSEINPUT(
            dx=ctypes.c_long(round(dx)),  # LONG
            dy=ctypes.c_long(round(dy)),  # LONG
            mouseData=0,  # DWORD
            dwFlags=MOUSEEVENTF_MOVE,  # DWORD
            time=0,  # DWORD
            dwExtraInfo=0x5E1D,  # ULONG_PTR
        )

        res = user32.SendInput(
            1,  # cInputs
            INPUT(type=0, mi=mouse_input),  # pInputs, 0 for mouse
            ctypes.sizeof(INPUT),  # cbSize
        )

        # print(f"sending input res: {res}")
        # log_last_err("Sending input err")

    # print(f"processed: {out_msg.pt.x}, {out_msg.pt.y}, Raw: {raw_x} {raw_y}")

if OBSERVING_MODE:
    plt.subplot(211)
    plt.plot(raw_data_x, label="Raw")
    plt.plot(filtered_data_x, label="Filtered")
    plt.title("X")
    plt.legend()

    plt.subplot(212)
    plt.plot(raw_data_y, label="Raw")
    plt.plot(filtered_data_y, label="Filtered")
    plt.title("Y")
    plt.legend()

    plt.tight_layout()
    plt.show()
