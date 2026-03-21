import ctypes

kernel32 = ctypes.windll.kernel32


def log_last_err(status_text="err code: "):
    err_code = kernel32.GetLastError()
    if err_code == 0:
        return
    print(f"{status_text}{err_code} - {ctypes.FormatError(err_code)}")
