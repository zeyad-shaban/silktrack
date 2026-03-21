import ctypes
from ctypes import wintypes

# custom
WM_SILKTRACK = 0x8001

# win defined
WP_INPUT = 0x00FF
RIDEV_INPUTSINK = 0x00000100
HWND_MESSAGE = ctypes.cast(ctypes.c_void_p(-3), wintypes.HWND)
RID_INPUT = 0x10000003
MOUSEEVENTF_MOVE = 0x0001
RIDEV_NOLEGACY = 0x00000030
LLMHF_INJECTED = 0x00000001
WH_MOUSE_LL = 14