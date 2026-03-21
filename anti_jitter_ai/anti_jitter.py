import ctypes
from ctypes import wintypes

from win32more.Windows.Win32.UI.Input import RAWINPUT, RAWINPUTHEADER
from win32more.Windows.Win32.UI.Input.KeyboardAndMouse import INPUT, MOUSEINPUT
from register_rid import register_rid
from mouse_blocking_hook import MouseBlockingHook
from kalman_filter_1d import KalmanFilter1D
from constants import *
from utils import log_last_err

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32


class AntiJitter:
    def __init__(self, Q_scale, R, mouse_hz):
        self.mouse_hook = MouseBlockingHook()
        self.mouse_hook.install()

        self.hwnd = register_rid()
        self.filter_x = KalmanFilter1D(Q_scale=Q_scale, R=R, mouse_hz=mouse_hz)
        self.filter_y = KalmanFilter1D(Q_scale=Q_scale, R=R, mouse_hz=mouse_hz)

        self.pcbSize = ctypes.c_uint(0)
        self.cbSizeHeader = ctypes.sizeof(RAWINPUTHEADER)
        self.pDataBuff: ctypes.Array[ctypes.c_byte] = (ctypes.c_byte * 1)()

        self.msg = wintypes.MSG()

        self._set_pcb_size()

    def run(self):
        try:
            while True:
                user32.GetMessageW(
                    ctypes.byref(self.msg),
                    self.hwnd,
                    WP_INPUT,
                    WP_INPUT,
                )

                user32.GetRawInputData(
                    self.msg.lParam,  # hRawInput
                    RID_INPUT,  # uiCommand
                    ctypes.byref(self.pDataBuff),  # pData
                    ctypes.byref(self.pcbSize),  # pcbSize
                    self.cbSizeHeader,  # cbSizeHeader
                )

                raw = ctypes.cast(self.pDataBuff, ctypes.POINTER(RAWINPUT)).contents
                if raw.data.mouse.ulExtraInformation == WM_SILKTRACK:
                    continue

                filtered_x = self.filter_x.update(raw.data.mouse.lLastX)
                filtered_y = self.filter_y.update(raw.data.mouse.lLastY)

                mouse_input = MOUSEINPUT(
                    dx=ctypes.c_long(round(filtered_x)),  # LONG
                    dy=ctypes.c_long(round(filtered_y)),  # LONG
                    mouseData=0,  # DWORD
                    dwFlags=MOUSEEVENTF_MOVE,  # DWORD
                    time=0,  # DWORD
                    dwExtraInfo=WM_SILKTRACK,  # ULONG_PTR
                )

                send_inp_res = user32.SendInput(
                    1,  # cInputs
                    INPUT(type=0, mi=mouse_input),  # pInputs, 0 for mouse
                    ctypes.sizeof(INPUT),  # cbSize
                )

                if send_inp_res != 1:
                    log_last_err()
                    raise Exception("SendInput failed, check above err code")

        except KeyboardInterrupt:
            pass
        finally:
            self.mouse_hook.uninstall()

    def _set_pcb_size(self):
        user32.GetMessageW(
            ctypes.byref(self.msg),
            self.hwnd,
            WP_INPUT,
            WP_INPUT,
        )

        ret = user32.GetRawInputData(
            self.msg.lParam,  # hRawInput
            RID_INPUT,  # uiCommand
            0,  # pData
            ctypes.byref(self.pcbSize),  # pcbSize
            self.cbSizeHeader,  # cbSizeHeader
        )
        self.pDataBuff = (ctypes.c_byte * self.pcbSize.value)()

        if ret != 0:
            log_last_err(status_text="Getting PCB Size err: ")
            raise Exception("Getting PCB Size failed, check error code above")
