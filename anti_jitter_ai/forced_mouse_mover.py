import ctypes
from ctypes import wintypes
import time
import threading
from win32more.Windows.Win32.UI.Input.KeyboardAndMouse import INPUT, MOUSEINPUT

user32 = ctypes.windll.user32

WH_MOUSE_LL = 14
WM_MOUSEMOVE = 0x0200
MOUSEEVENTF_MOVE = 0x0001
LLMHF_INJECTED = 0x00000001  # flag set on synthetic input


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", wintypes.POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulong),
    ]


HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
hook_handle = None


def mouse_proc(nCode, wParam, lParam):
    if nCode >= 0 and wParam == WM_MOUSEMOVE:
        info = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
        if info.flags & LLMHF_INJECTED:
            return user32.CallNextHookEx(hook_handle, nCode, wParam, ctypes.c_long(lParam))
        return 1
    return user32.CallNextHookEx(hook_handle, nCode, wParam, ctypes.c_long(lParam))


def move_mouse():
    time.sleep(1)
    print("moving right...")
    for _ in range(300):
        mi = MOUSEINPUT(dx=ctypes.c_long(3), dy=0, mouseData=0, dwFlags=MOUSEEVENTF_MOVE, time=0, dwExtraInfo=0)
        user32.SendInput(1, INPUT(type=0, mi=mi), ctypes.sizeof(INPUT))
        time.sleep(0.01)
    print("moving left...")
    for _ in range(300):
        mi = MOUSEINPUT(dx=ctypes.c_long(-3), dy=0, mouseData=0, dwFlags=MOUSEEVENTF_MOVE, time=0, dwExtraInfo=0)
        user32.SendInput(1, INPUT(type=0, mi=mi), ctypes.sizeof(INPUT))
        time.sleep(0.01)
    print("done!")


mouse_cb = HOOKPROC(mouse_proc)
hook_handle = user32.SetWindowsHookExW(WH_MOUSE_LL, mouse_cb, None, 0)
print(f"hook installed: {hook_handle}")

threading.Thread(target=move_mouse, daemon=True).start()

msg = wintypes.MSG()
while True:
    user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
    user32.TranslateMessage(ctypes.byref(msg))
    user32.DispatchMessageW(ctypes.byref(msg))
