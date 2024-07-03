import sys
import threading
sys.path.insert(0, "..")
import basic

def main():
    while True:
        file_name = input() + ".txt"
        with open(file_name, "r") as file:
            text = file.read()
            print(text)
            print(basic.Parser(basic.send_plaintext(text)).parse())

if __name__ == "__main__":
    sys.setrecursionlimit(10 ** 6)
    threading.stack_size(2 ** 27)
    thread = threading.Thread(target = main)
    thread.start()