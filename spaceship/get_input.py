import sys
import threading
sys.path.insert(0, "..")
import basic

TEST_COUNT = 25

def main():
    for i in range(1, TEST_COUNT + 1):
        with open(f"input/input{i}.txt", "w") as f:
            f.write(basic.send_plaintext(f"get spaceship{i}"))

if __name__ == "__main__":
    sys.setrecursionlimit(10 ** 6)
    threading.stack_size(2 ** 27)
    thread = threading.Thread(target = main)
    thread.start()
