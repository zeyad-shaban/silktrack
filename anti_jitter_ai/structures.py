import ctypes
from ctypes import wintypes
from win32more.Windows.Win32.UI.Input import RAWHID, RAWKEYBOARD
# i could have used win32more for all but.. where is the fun in that :P


# https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawinputdevice
class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [
        ("usUsagePage", wintypes.USHORT),
        ("usUsage", wintypes.USHORT),
        ("dwFlags", wintypes.DWORD),
        ("hwndTarget", wintypes.HWND),
    ]


# https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-msg
class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT),
        ("lPrivate", wintypes.DWORD),
    ]


# https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawinputheader
class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [
        ("dwType", wintypes.DWORD),
        ("dwSize", wintypes.DWORD),
        ("hDevice", wintypes.HANDLE),
        ("wParam", wintypes.WPARAM),
    ]

# https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawmouse
class RAWMOUSE(ctypes.Structure):
    class _DUMMYUNIONNAME(ctypes.Union):
        class _DUMMYSTRUCTNAME(ctypes.Structure):
            _fields_ = [
                ("usButtonFlags", wintypes.USHORT),
                ("usButtonData",  wintypes.USHORT),
            ]
        _fields_ = [
            ("ulButtons",      wintypes.ULONG),
            ("DUMMYSTRUCTNAME", _DUMMYSTRUCTNAME),
        ]
    _fields_ = [
        ("usFlags",            wintypes.USHORT),
        ("DUMMYUNIONNAME",     _DUMMYUNIONNAME),
        ("ulRawButtons",       wintypes.ULONG),
        ("lLastX",             wintypes.LONG),
        ("lLastY",             wintypes.LONG),
        ("ulExtraInformation", wintypes.ULONG),
    ]
    


# https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawinput
class RAWINPUT (ctypes.Structure):
    class _DUMMYUNIONNAME(ctypes.Union):
        _fields_ = [
            ('mouse', RAWMOUSE),
            ('keyboard', RAWKEYBOARD),
            ('hid', RAWHID),
        ]
    _fields_ = [
        ('header', RAWINPUTHEADER),
        ('_DUMMYUNIONNAME', _DUMMYUNIONNAME),
    ]