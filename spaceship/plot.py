import sys
import matplotlib.pyplot as plt

if __name__ == "__main__":
    #test_num = int(sys.argv[1])
    for test_num in range(24, 26):
        file_path = f"input/input{test_num}.txt"
        with open(file_path, "r") as f:
            points = [line.split() for line in f.read().strip().split("\n")]
            x = [int(p[0]) for p in points]
            y = [int(p[1]) for p in points]
            plt.scatter(x, y)
            plt.show()