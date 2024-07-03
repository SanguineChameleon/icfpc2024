#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <algorithm>
#include <thread>

const int TEST_COUNT = 21;

class Solver {
private:
    int testNum;
    int beamWidth;
    std::vector<std::string> grid;
    int n, m, sx, sy;

    void readInput() {
        std::string filePath = "input/input" + std::to_string(testNum) + ".txt";
        std::ifstream inputFile(filePath);
        std::string row;
        while (inputFile >> row) {
            grid.push_back(row);
        }
        n = grid.size();
        m = grid[0].size();
        sx = -1;
        sy = -1;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                if (grid[i][j] == 'L') {
                    sx = i;
                    sy = j;
                }
            }
        }
    }

    class State {
    public:
        State(std::vector<std::string>& grid, int cx, int cy, State* prvState): grid(grid), cx(cx), cy(cy), prvState(prvState) {
            n = grid.size();
            m = grid[0].size();
            this->grid[cx][cy] = '#';
            calcScore();
        }

        State* makeMove(int d) {
            int nx = cx + dx[d];
            int ny = cy + dy[d];
            bool isValid = (0 <= nx && nx < n) && (0 <= ny && ny < m) && (grid[nx][ny] == '.');
            if (!isValid) {
                return nullptr;
            }
            return new State(grid, nx, ny, this);
        }

        int getScore() {
            return score;
        }

        std::string traceMoves() {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < m; j++) {
                    vis[i][j] = false;
                }
            }
            State* curState = this;
            std::string mainPath;
            while (true) {
                cx = curState->cx;
                cy = curState->cy;
                vis[cx][cy] = true;
                State *prvState = curState->prvState;
                if (!prvState) {
                    break;
                }
                int px = prvState->cx;
                int py = prvState->cy;
                for (int d = 0; d < 4; d++) {
                    if (px + dx[d] == cx && py + dy[d] == cy) {
                        mainPath += dirs[d];
                        break;
                    }
                }
                curState = prvState;
            }
            std::reverse(mainPath.begin(), mainPath.end());
            dfs(cx, cy, true);
            for (auto c: mainPath) {
                for (int d = 0; d < 4; d++) {
                    if (dirs[d] == c) {
                        cx += dx[d];
                        cy += dy[d];
                        moves += c;
                        break;
                    }
                }
                dfs(cx, cy, true);
            }
            return moves;
        }

    private:
        static constexpr int dx[4] = {-1, 1, 0, 0};
        static constexpr int dy[4] = {0, 0, -1, 1};
        static constexpr char dirs[4] = {'U', 'D', 'L', 'R'};

        std::vector<std::string> grid;
        std::vector<std::vector<bool>> vis;
        int n, m, cx, cy;
        int score;
        std::string moves;
        State* prvState;

        void dfs(int cx, int cy, bool trace = false) {
            score++;
            vis[cx][cy] = true;
            for (int d = 0; d < 4; d++) {
                int nx = cx + dx[d];
                int ny = cy + dy[d];
                bool isValid = (0 <= nx && nx < n) && (0 <= ny && ny < m) && (grid[nx][ny] == '.') && !vis[nx][ny];
                if (isValid) {
                    if (trace) {
                        moves += dirs[d];
                    }
                    dfs(nx, ny, trace);
                    if (trace) {
                        moves += dirs[d ^ 1];
                    }
                }
            }
        }

        void calcScore() {
            vis.resize(n);
            for (int i = 0; i < n; i++) {
                vis[i].resize(m);
            }
            score = 0;
            dfs(cx, cy);
        }
    };

    std::string findSolution() {
        class Compare {
        public:
            bool operator()(State* lhs, State* rhs) {
                return false;
            }
        } comp;

        State* start = new State(grid, sx, sy, nullptr);

        State* bestState = start;

        std::vector<State*> curStates = {start};

        while (!curStates.empty()) {
            bestState = curStates[0];

            std::vector<State*> nxtStates;

            for (State* curState: curStates) {
                for (int d = 0; d < 4; d++) {
                    State* nxtState = curState->makeMove(d);
                    if (nxtState) {
                        nxtStates.push_back(nxtState);
                    }
                }
            }
            std::sort(nxtStates.begin(), nxtStates.end(), comp);

            if ((int)nxtStates.size() > beamWidth) {
                nxtStates.resize(beamWidth);
            }

            curStates.swap(nxtStates);
        }

        return bestState->traceMoves();
    }

    void writeToFile(std::string message) {
        std::string filePath = "output/output" + std::to_string(testNum) + ".txt";
        std::ofstream messageFile(filePath);
        messageFile << message;
    }

    void submit() {
        std::string cmd = "python submit.py " + std::to_string(testNum);
        system(cmd.c_str());
    }

public:
    Solver(int testNum, int beamWidth): testNum(testNum), beamWidth(beamWidth) {
        readInput();
    }

    void solve() {
        std::string moves = findSolution();
        writeToFile(moves);
        submit();
    }

};

void execSolve(Solver* solver) {
    solver->solve();
}

void solveAll() {
    std::vector<Solver*> solvers;
    for (int testNum = 1; testNum <= TEST_COUNT; testNum++) {
        if (testNum == 9 || testNum == 10 || testNum == 17 || testNum == 18 || testNum == 20 || testNum == 21) {
            //solvers.push_back(new Solver(testNum, 20));
        }
        else {
            solvers.push_back(new Solver(testNum, 30000));
        }
    }

    std::vector<std::thread> threads;

    for (Solver* solver: solvers) {
        threads.emplace_back(execSolve, solver);
    }

    for (auto& thread: threads) {
        thread.join();
    }

}

int main() {
    solveAll();
    return 0;
}