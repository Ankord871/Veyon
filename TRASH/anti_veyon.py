import time
import subprocess
import psutil
import sys
import os

try:
    import win32gui
    import win32process
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

BLOCK_KEYWORDS = ("veyon", "блокировка veyon", "veyon master")
LOCK_TIMEOUT = 5.0
CHECK_INTERVAL = 0.5

# --- ИСКЛЮЧАЕМ СЕБЯ ---
MY_PID = os.getpid()
MY_NAME = os.path.basename(sys.executable).lower()  # для exe
MY_SCRIPT = os.path.basename(sys.argv[0]).lower()   # для .py

def veyon_process_running():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Если это наш собственный процесс — пропускаем
            if proc.info['pid'] == MY_PID:
                continue
            
            n = proc.info['name'].lower()
            
            # Если имя процесса совпадает с нашим exe или скриптом — пропускаем
            if n == MY_NAME or n == MY_SCRIPT:
                continue
                
            if 'veyon' in n and 'anti' not in n:
                return True
        except Exception:
            pass
    return False

def veyon_window_present():
    if not HAS_WIN32:
        return False
    found = [False]
    def cb(hwnd, _):
        try:
            title = win32gui.GetWindowText(hwnd).lower()
            if not title:
                return True
            
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # Если окно принадлежит нам — пропускаем
            if pid == MY_PID:
                return True
                
            proc = psutil.Process(pid)
            name = proc.name().lower()
            
            # Если процесс окна — это наш exe — пропускаем
            if name == MY_NAME or name == MY_SCRIPT:
                return True

            if 'veyon' in name and 'anti' not in name:
                found[0] = True
                return False
            if 'veyon' in title:
                found[0] = True
                return False
        except Exception:
            pass
        return True
    try:
        win32gui.EnumWindows(cb, None)
    except Exception:
        pass
    return found[0]

def reboot():
    subprocess.run('shutdown /r /t 0 /f', shell=True)

def main():
    lock_start = None
    while True:
        try:
            win = veyon_window_present()
            proc = veyon_process_running()
            active = win or proc

            if active:
                if lock_start is None:
                    lock_start = time.time()
                elif time.time() - lock_start >= LOCK_TIMEOUT:
                    reboot()
                    break
            else:
                lock_start = None
        except Exception:
            pass
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()