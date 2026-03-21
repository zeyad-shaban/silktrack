import ctypes
from ctypes import wintypes
from win32more.Windows.Win32.UI.WindowsAndMessaging import MSLLHOOKSTRUCT

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

LLMHF_INJECTED = 0x00000001
WH_MOUSE_LL = 14


def log_last_err(status_text="err code"):
    err_code = kernel32.GetLastError()
    print(f"{status_text}: {err_code} - {ctypes.FormatError(err_code)}")


def LowLevelMouseProc(nCode, wParam, lParam):
    if nCode < 0 or ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents.flags & LLMHF_INJECTED: # type: ignore
        return user32.CallNextHookEx(0, nCode, wParam, ctypes.c_long(lParam))

    return 1

HOOKPROC = ctypes.WINFUNCTYPE(wintypes.LONG, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM)
mouse_cb = HOOKPROC(LowLevelMouseProc)


user32.SetWindowsHookExW(
    WH_MOUSE_LL,  # idHook
    mouse_cb,  # lpfn
    None,  # hmod
    0,  # dwThreadId
)
log_last_err()

msg = wintypes.MSG()
while True:
    user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
    user32.TranslateMessage(ctypes.byref(msg))
    user32.DispatchMessageW(ctypes.byref(msg))
