import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

WH_MOUSE_LL = 14
WM_MOUSEMOVE = 0x0200

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

hook_handle = None

def mouse_proc(nCode, wParam, lParam):
    if nCode >= 0 and wParam == WM_MOUSEMOVE:
        return 1  # block movement
    return user32.CallNextHookEx(hook_handle, nCode, wParam, lParam)

mouse_cb = HOOKPROC(mouse_proc)
hook_handle = user32.SetWindowsHookExW(WH_MOUSE_LL, mouse_cb, None, 0)
print(f"hook installed: {hook_handle}")

msg = wintypes.MSG()
while True:
    user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
    user32.TranslateMessage(ctypes.byref(msg))
    user32.DispatchMessageW(ctypes.byref(msg))