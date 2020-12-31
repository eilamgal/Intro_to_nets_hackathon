import msvcrt
import time


def _is_data():
    return msvcrt.kbhit()

if __name__ == "__main__":
    start = time.time()
    while time.time() - start <=10:
        if _is_data():
            print(msvcrt.getch().decode('utf-8'))
