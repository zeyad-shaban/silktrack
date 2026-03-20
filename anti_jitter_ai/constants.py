import ctypes
from ctypes import wintypes


WP_INPUT = 0x00FF
RIDEV_INPUTSINK = 0x00000100
HWND_MESSAGE = ctypes.cast(ctypes.c_void_p(-3), wintypes.HWND)
RID_INPUT = 0x10000003
