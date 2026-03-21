import ctypes
from ctypes import wintypes
import threading
import queue

from win32more.Windows.Win32.UI.Input.KeyboardAndMouse import MOUSEINPUT, INPUT
from kalman_filter_1d import KalmanFilter1D
from structures import *
from win32more.Windows.Win32.UI.WindowsAndMessaging import MSLLHOOKSTRUCT
from constants import *

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

HOOKPROC = ctypes.WINFUNCTYPE(wintypes.LONG, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM)


class MouseHook:
    def __init__(self, Q_scale: int, R: int, mouse_hz: int):
        self.filter_x = KalmanFilter1D(Q_scale, R, mouse_hz)
        self.filter_y = KalmanFilter1D(Q_scale, R, mouse_hz)
        self.mouse_cb = HOOKPROC(self._callback)
        self.prev_raw_x = self.prev_raw_y = None
        self.q = queue.Queue()

        self.hook_handle = None
        self.running = True

    def install(self):
        threading.Thread(target=self._worker, daemon=True).start()

        self.hook_handle = user32.SetWindowsHookExW(
            WH_MOUSE_LL,  # idHook
            self.mouse_cb,  # lpfn
            None,  # hmod
            0,  # dwThreadId
        )
        self._log_last_err()
        msg = wintypes.MSG()

        try:
            while self.running:
                user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        except KeyboardInterrupt:
            pass
        finally:
            self.uninstall()

    def uninstall(self):
        user32.UnhookWindowsHookEx(self.hook_handle)
        self.running = False
        print("okay done uninstalling")

    def _worker(self):
        while True:
            raw_x, raw_y = self.q.get()
            self._send_filtered_input(raw_x, raw_y)

    def _callback(self, nCode, wParam, lParam):
        info = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents

        if nCode < 0 or info.flags & LLMHF_INJECTED:  # type: ignore
            return user32.CallNextHookEx(0, nCode, wParam, ctypes.c_long(lParam))

        self.q.put((info.pt.x, info.pt.y))
        return 1

    def _log_last_err(self, status_text="err code: "):
        err_code = kernel32.GetLastError()
        print(f"{status_text}{err_code} - {ctypes.FormatError(err_code)}")

    def _send_filtered_input(self, raw_x, raw_y):
        if self.prev_raw_x is None:
            self.prev_raw_x = raw_x
            self.prev_raw_y = raw_y

        filtered_dx, filtered_dy = self.filter_x.update(raw_x - self.prev_raw_x), self.filter_y.update(raw_y - self.prev_raw_y)

        print(f"raw_x: {raw_x}, prev_raw_x: {self.prev_raw_x}")
        # print(f"raw_dx: {raw_x - self.prev_raw_x:+.0f} raw_dy: {raw_y - self.prev_raw_y:+.0f} | filtered_dx: {filtered_dx:+.2f} filtered_dy: {filtered_dy:+.2f}")

        self.prev_raw_x = raw_x
        self.prev_raw_y = raw_y

        mouse_input = MOUSEINPUT(
            dx=ctypes.c_long(round(filtered_dx)),  # LONG
            dy=ctypes.c_long(round(filtered_dy)),  # LONG
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

        return 1


if __name__ == "__main__":
    mouse_hook = MouseHook(Q_scale=1000, R=1, mouse_hz=100)
    mouse_hook.install()
