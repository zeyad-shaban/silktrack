import ctypes
from ctypes import wintypes

from win32more.Windows.Win32.UI.Input.KeyboardAndMouse import INPUT, MOUSEINPUT
from constants import *
from structures import *
from utils import log_last_err


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


def register_rid():
    user32.GetRawInputData.restype = ctypes.c_uint
    user32.CreateWindowExW.restype = wintypes.HWND

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
    log_last_err("Creating HandleWindow err: ")

    rid = RAWINPUTDEVICE(
        usUsagePage=0x0001,
        usUsage=0x0002,
        dwFlags=RIDEV_INPUTSINK,
        hwndTarget=hwnd,
    )

    rid_call_res = user32.RegisterRawInputDevices(ctypes.byref(rid), 1, ctypes.sizeof(rid))
    if rid_call_res != 1:
        log_last_err("Register Raw Input Device err: ")
        raise Exception("Registering RawInputDevices failed, check err code above")

    return hwnd
