#include <iostream>

int res[81];
int badCount[81][9];
int given[81];

void addBad(int cellNum, int val, int delta) {
    int row = cellNum / 9;
    int col = cellNum % 9;
    int boxRow = row / 3 * 3;
    int boxCol = col / 3 * 3;
    for (int i = 0; i < 9; i++) {
        int cellNum2 = row * 9 + i;
        badCount[cellNum2][val] += delta;
    }
    for (int i = 0; i < 9; i++) {
        int cellNum2 = i * 9 + col;
        badCount[cellNum2][val] += delta;
    }
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            int cellNum2 = (boxRow + i) * 9 + (boxCol + j);
            badCount[cellNum2][val] += delta;
        }
    }
}

void backtrack(int cellNum) {
    if (cellNum == 81) {
        for (int i = 0; i < 81; i++) {
            std::cout << res[i] + 1;
        }
        exit(0);
    }
    for (int val = 0; val < 9; val++) {
        if (given[cellNum] != -1 && val != given[cellNum]) {
            continue;
        }
        if (badCount[cellNum][val] == 0) {
            addBad(cellNum, val, 1);
            res[cellNum] = val;
            backtrack(cellNum + 1);
            addBad(cellNum, val, -1);
        }
    }
}

int main() {
    for (int i = 0; i < 81; i++) {
        given[i] = -1;
    }
    int givenCount;
    std::cin >> givenCount;
    for (int i = 0; i < givenCount; i++) {
        int cellNum, val;
        std::cin >> cellNum >> val;
        val--;
        given[cellNum] = val;
    }
    backtrack(0);
}