import os

TEST_COUNT = 25

if __name__ == "__main__":
    for i in range(1, TEST_COUNT + 1):
        os.mkdir(f"files/test{i}")
