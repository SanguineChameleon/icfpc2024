#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <algorithm>
#include <thread>
#include <numeric>
#include <random>

const int API_COOL_DOWN = 90;
const int TEST_COUNT = 25;

class Solver {
private:
    static const int MAX_MOVES = 10000000;
    static constexpr char digits[3][3] = {{'1', '4', '7'}, {'2', '5', '8'}, {'3', '6', '9'}};

    int testNum;
    std::vector<std::pair<int, int>> squares;
    std::vector<int> bestOrder;
    int n;
    
    bool hasFound = false;
    bool hasSubmitted = false;

    void readInput() {
        std::string filePath = "input/input" + std::to_string(testNum) + ".txt";
        std::ifstream inputFile(filePath);
        int x, y;
        while (inputFile >> x >> y) {
            squares.emplace_back(x, y);
        }
        n = squares.size();
    }

    std::string getFilePath(std::string fileName) {
        std::string filePath = "files/test" + std::to_string(testNum) + "/" + fileName + ".txt";
        return filePath;
    }

    void writeToFile(std::string fileName, std::string content) {
        std::string filePath = getFilePath(fileName);
        std::ofstream outputFile(filePath);
        outputFile << moves;
    }

    void writeToFile(std::string fileName, std::vector<int>& order) {
        std::string filePath = getFilePath(fileName);
        std::ofstream outputFile(filePath);
        for (int i = 0; i < n; i++) {
            outputFile << order[i] << '\n';
        }
    }

    void readOrder(std::string fileName, std::vector<int>& order) {
        order.resize(n);
        std::string filePath = getFilePath(fileName);
        std::ifstream inputFile(filePath);
        for (int i = 0; i < n; i++) {
            inputFile >> order[i];
        }
    }

    std::string moves;

    int eval(std::vector<int> &order, bool trace = false) {
        if (trace) {
            moves.clear();
        }
        int vx = 0;
        int vy = 0;
        int cx = 0;
        int cy = 0;
        int res = 0;
        for (int i = 0; i < n; i++) {
            int nx = squares[order[i]].first;
            int ny = squares[order[i]].second;
            int k = 0;
            while (true) {
                int dx = nx - cx - vx * k;
                int dy = ny - cy - vy * k;
                int sum = k * (k + 1) / 2;
                if (abs(dx) <= sum && abs(dy) <= sum) {
                    break;
                }
                k++;
            }
            int dx = nx - cx - vx * k;
            int dy = ny - cy - vy * k;
            for (int j = k; j >= 1; j--) {
                int ax = 0;
                int ay = 0;
                if (dx >= j) {
                    dx -= j;
                    ax = 1;
                }
                if (dx <= -j) {
                    dx += j;
                    ax = -1;
                }
                if (dy >= j) {
                    dy -= j;
                    ay = 1;
                }
                if (dy <= -j) {
                    dy += j;
                    ay = -1;
                }
                if (trace) {
                    moves += digits[ax + 1][ay + 1];
                }
                vx += ax;
                vy += ay;
            }
            cx = nx;
            cy = ny;
            res += k;
        }
        return res;
    }

    void greedyByMoves(std::vector<int> &order) {
        std::vector<bool> chosen(n);
        order.resize(n);
        int vx = 0;
        int vy = 0;
        int cx = 0;
        int cy = 0;
        int cnt = 0;
        for (int i = 0; i < n; i++) {
            int nxtPoint = -1;
            int minSteps = -1;
            for (int j = 0; j < n; j++) {
                if (!chosen[j]) {
                    int nx = squares[j].first;
                    int ny = squares[j].second;
                    int k = 0;
                    while (true) {
                        int dx = nx - cx - vx * k;
                        int dy = ny - cy - vy * k;
                        int sum = k * (k + 1) / 2;
                        if (abs(dx) <= sum && abs(dy) <= sum) {
                            break;
                        }
                        k++;
                    }
                    if (nxtPoint == -1 || k < minSteps) {
                        nxtPoint = j;
                        minSteps = k;
                    }
                }
            }
            chosen[nxtPoint] = true;
            order[i] = nxtPoint;
            int nx = squares[nxtPoint].first;
            int ny = squares[nxtPoint].second;
            int k = minSteps;
            int dx = nx - cx - vx * k;
            int dy = ny - cy - vy * k;
            for (int j = k; j >= 1; j--) {
                int ax = 0;
                int ay = 0;
                if (dx >= j) {
                    dx -= j;
                    ax = 1;
                }
                if (dx <= -j) {
                    dx += j;
                    ax = -1;
                }
                if (dy >= j) {
                    dy -= j;
                    ay = 1;
                }
                if (dy <= -j) {
                    dy += j;
                    ay = -1;
                }
                vx += ax;
                vy += ay;
            }
            cnt += k;
            cx = nx;
            cy = ny;
        }
    }

    void greedyByDist(std::vector<int> &order) {
        std::vector<bool> chosen(n);
        order.resize(n);
        int cx = 0;
        int cy = 0;
        for (int i = 0; i < n; i++) {
            int nxtPoint = -1;
            int minDist = -1;
            for (int j = 0; j < n; j++) {
                if (!chosen[j]) {
                    int dist = abs(cx - squares[j].first) + abs(cy - squares[j].second);
                    if (nxtPoint == -1 || dist < minDist) {
                        nxtPoint = j;
                        minDist = dist;
                    }
                }
            }
            chosen[nxtPoint] = true;
            order[i] = nxtPoint;
            cx = squares[nxtPoint].first;
            cy = squares[nxtPoint].second;
        }
    }

    int calcMinStepsLazy(long cx, int cy, int nx, int ny, int vx, int vy, int r) {
        int l = 0;
        while (l <= r) {
            int m = (l + r) / 2;
            int dx = nx - cx - vx * m;
            int dy = ny - cy - vy * m;
            int sum = m * (m + 1) / 2;
            if (abs(dx) <= sum && abs(dy) <= sum) {
                r = m - 1;
            }
            else {
                l = m + 1;
            }
        }
        return l;
    }

    int calcMinSteps(long cx, int cy, int nx, int ny, int vx, int vy) {
        int k = 0;
        while (true) {
            int dx = nx - cx - vx * k;
            int dy = ny - cy - vy * k;
            int sum = k * (k + 1) / 2;
            if (abs(dx) <= sum && abs(dy) <= sum) {
                return k;
            }
            k++;
        }
    }

public:
    Solver(int testNum): testNum(testNum) {
        readInput();
    }

    void submit() {
        if (hasFound && !hasSubmitted) {
            std::string cmd = "python submit.py " + std::to_string(testNum);
            system(cmd.c_str());
            hasSubmitted = true;
        }
    }

    void solve() {
        std::mt19937 gen(std::chrono::steady_clock::now().time_since_epoch().count());

        std::vector<int> order;
        readOrder("dist_order", order);
        bestOrder = order;
        int bestScore = eval(bestOrder, true);

        if (bestScore < MAX_MOVES) {
            eval(bestOrder, true);
            writeToFile("output", moves);
            hasFound = true;
            hasSubmitted = false;
        }

        int curScore = bestScore;
        while (true) {
            int i = gen() % n;
            int j = gen() % n;
            std::swap(order[i], order[j]);
            int nxtScore = eval(order);
            if (nxtScore < curScore) {
                if (nxtScore < bestScore) {
                    bestScore = nxtScore;
                    bestOrder = order;

                    writeToFile("best_order", bestOrder);
                    std::cout << "Test #" << testNum << ": " << bestScore << std::endl;

                    if (bestScore < MAX_MOVES) {
                        eval(bestOrder, true);
                        writeToFile("output", moves);
                        hasFound = true;
                        hasSubmitted = false;
                    }
                }
                curScore = nxtScore;
            }
            else {
                std::swap(order[i], order[j]);
            }
        }
    }

};

namespace Main {
    std::vector<Solver*> solvers;

    void execSolve(Solver* solver) {
        solver->solve();
    }

    void submitAll() {
        while (true) {
            std::this_thread::sleep_for(std::chrono::seconds(API_COOL_DOWN));
            for (Solver* solver: solvers) {
                solver->submit();
            }
        }
    }

    void solveAll() {
        for (int testNum = 1; testNum <= TEST_COUNT; testNum++) {
            solvers.push_back(new Solver(testNum));
        }

        std::vector<std::thread> threads;

        for (Solver* solver: solvers) {
            threads.emplace_back(execSolve, solver);
        }

        //threads.emplace_back(submitAll);

        for (auto& thread: threads) {
            thread.join();
        }

    }
}

int main() {
    Main::solveAll();
    return 0;
}