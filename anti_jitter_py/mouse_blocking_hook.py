import ctypes
from ctypes import wintypes

from structures import *
from win32more.Windows.Win32.UI.WindowsAndMessaging import MSLLHOOKSTRUCT
from constants import *
from utils import log_last_err

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

HOOKPROC = ctypes.WINFUNCTYPE(wintypes.LONG, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM)


class MouseBlockingHook:
    def __init__(self):
        self.mouse_cb = HOOKPROC(self._callback)
        self.hook_handle = None

    def install(self):
        self.hook_handle = user32.SetWindowsHookExW(
            WH_MOUSE_LL,  # idHook
            self.mouse_cb,  # lpfn
            None,  # hmod
            0,  # dwThreadId
        )
        log_last_err("Mouse hook attaching err: ")

    def uninstall(self):
        user32.UnhookWindowsHookEx(self.hook_handle)
        print("okay done uninstalling")

    def _callback(self, nCode, wParam, lParam):
        if nCode < 0 or ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents.dwExtraInfo == WM_SILKTRACK: # flags & LLMHF_INJECTED:
            return user32.CallNextHookEx(0, nCode, wParam, ctypes.c_long(lParam))

        return 1


if __name__ == "__main__":
    mouse_hook = MouseBlockingHook()
    mouse_hook.install()
