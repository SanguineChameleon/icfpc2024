import sys
import threading
sys.path.insert(0, "..")
import basic

def main():
    while True:
        print(basic.Parser(input()).parse())

if __name__ == "__main__":
    sys.setrecursionlimit(10 ** 6)
    threading.stack_size(2 ** 27)
    thread = threading.Thread(target = main)
    thread.start()