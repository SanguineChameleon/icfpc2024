class Program:
    def print_grid(self):
        print(f"[row = {self.row_offset}, col = {self.col_offset}]")
        max_token_len = [1 for i in range(self.width)]
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] != None:
                    max_token_len[j] = max(max_token_len[j], len(str(self.grid[i][j])))
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] != None:
                    token = str(self.grid[i][j])
                else:
                    token = "."
                print(token.rjust(max_token_len[j]), end = " ")
            print()

    def fix_offset(self):
        first_row = None
        for i in range(self.height):
            is_empty = True
            for j in range(self.width):
                if self.grid[i][j] != None:
                    is_empty = False
                    break
            if not is_empty:
                first_row = i
                break

        last_row = None
        for i in range(self.height - 1, -1, -1):
            is_empty = True
            for j in range(self.width):
                if self.grid[i][j] != None:
                    is_empty = False
                    break
            if not is_empty:
                last_row = i
                break

        first_col = None
        for j in range(self.width):
            is_empty = True
            for i in range(self.height):
                if self.grid[i][j] != None:
                    is_empty = False
                    break
            if not is_empty:
                first_col = j
                break
                
        last_col = None
        for j in range(self.width - 1, -1, -1):
            is_empty = True
            for i in range(self.height):
                if self.grid[i][j] != None:
                    is_empty = False
                    break
            if not is_empty:
                last_col = j
                break

        if first_row == None:
            self.grid = [[None]]
            self.height = 1
            self.width = 1
            self.row_offset = 1
            self.col_offset = 1
            return

        new_height = last_row - first_row + 3
        new_width = last_col - first_col + 3
        new_grid = [[None for j in range(new_width)] for i in range(new_height)]
        for i in range(1, new_height - 1):
            for j in range(1, new_width - 1):
                new_grid[i][j] = self.grid[first_row + i - 1][first_col + j - 1]

        self.grid = new_grid
        self.height = new_height
        self.width = new_width
        self.row_offset += first_row - 1
        self.col_offset += first_col - 1

    def __init__(self, text):
        lines = text.split("\n")
        tokens = lines[0].split()
        variables = {}
        for i in range(0, len(tokens), 2):
            variables[tokens[i]] = int(tokens[i + 1])
        self.grid = [line.split() for line in lines[1:]]
        self.height = len(self.grid)
        self.width = max([len(row) for row in self.grid])
        self.row_offset = 1
        self.col_offset = 1
        self.timeline = []
        for row in self.grid:
            while len(row) < self.width:
                row.append(None)
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == ".":
                    self.grid[i][j] = None
                else:
                    try:
                        self.grid[i][j] = int(self.grid[i][j])
                    except:
                        pass
        self.fix_offset()
        self.print_grid()
        print()
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] in variables and self.grid[i][j] != "A" and self.grid[i][j] != "B":
                    self.grid[i][j] = variables[self.grid[i][j]]
        self.print_grid()
        print()
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == "A" or self.grid[i][j] == "B":
                    self.grid[i][j] = variables[self.grid[i][j]]

    @staticmethod
    def int_div(x, y):
        res = abs(x) // abs(y)
        if (x < 0 and y > 0) or (x > 0 and y < 0):
            res = -res
        return res

    @staticmethod
    def int_mod(x, y):
        return x - Program.int_div(x, y) * y

    def set_value(self, val, row, col):
        min_row = min(row, self.row_offset)
        max_row = max(row, self.row_offset + self.height - 1)
        min_col = min(col, self.col_offset)
        max_col = max(col, self.col_offset + self.width - 1)

        new_height = max_row - min_row + 1
        new_width = max_col - min_col + 1
        new_grid = [[None for j in range(new_width)] for i in range(new_height)]
        for i in range(new_height):
            for j in range(new_width):
                pi = i + min_row - self.row_offset
                pj = j + min_col - self.col_offset
                if 0 <= pi and pi < self.height and 0 <= pj and pj < self.width:
                    new_grid[i][j] = self.grid[pi][pj]
        new_grid[row - min_row][col - min_col] = val

        self.grid = new_grid
        self.height = new_height
        self.width = new_width
        self.row_offset = min_row
        self.col_offset = min_col
        self.timeline[-1] = (self.row_offset, self.col_offset, [row[:] for row in self.grid])

    def fix_and_print(self):
        self.fix_offset()
        self.print_grid()

    def add_to_timeline(self):
        self.timeline.append((self.row_offset, self.col_offset, self.grid))

    def step(self):
        new_grid = [row[:] for row in self.grid]
        warp_dt = None
        warps = []
        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                if self.grid[i][j] == "@":
                    dc = self.grid[i][j - 1]
                    dr = self.grid[i][j + 1]
                    val = self.grid[i - 1][j]
                    dt = self.grid[i + 1][j]
                    if isinstance(dc, int) and isinstance(dr, int) and isinstance(val, int) and isinstance(dt, int):
                        if warp_dt != None:
                            assert dt == warp_dt
                        else:
                            warp_dt = dt
                        row = i + self.row_offset - dr
                        col = j + self.col_offset - dc
                        warps.append((val, row, col))
        for i in range(self.height):
            for j in range(1, self.width - 1):
                if self.grid[i][j] == "<" and self.grid[i][j + 1] != None:
                    new_grid[i][j - 1] = self.grid[i][j + 1]
                    new_grid[i][j + 1] = None
                if self.grid[i][j] == ">" and self.grid[i][j - 1] != None:
                    new_grid[i][j + 1] = self.grid[i][j - 1]
                    new_grid[i][j - 1] = None
        for j in range(self.width):
            for i in range(1, self.height- 1):
                if self.grid[i][j] == "^" and self.grid[i + 1][j] != None:
                    new_grid[i - 1][j] = self.grid[i + 1][j]
                    new_grid[i + 1][j] = None
                if self.grid[i][j] == "v" and self.grid[i - 1][j] != None:
                    new_grid[i + 1][j] = self.grid[i - 1][j]
                    new_grid[i - 1][j] = None
        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                if self.grid[i][j] != None and not isinstance(self.grid[i][j], int):
                    op = self.grid[i][j]
                    if op != "S" and op != "@" and op != "<" and op != ">" and op != "^" and op != "v":
                        x = self.grid[i][j - 1]
                        y = self.grid[i - 1][j]
                        if isinstance(x, int) and isinstance(y, int):
                            if op == "=" or op == "#":
                                if (op == "=" and x == y) or (op == "#" and x != y):
                                    new_grid[i][j - 1] = None
                                    new_grid[i - 1][j] = None
                                    new_grid[i + 1][j] = x
                                    new_grid[i][j + 1] = y
                            else:
                                new_grid[i][j - 1] = None
                                new_grid[i - 1][j] = None
                                if op == "+":
                                    res = x + y
                                if op == "-":
                                    res = x - y
                                if op == "*":
                                    res = x * y
                                if op == "/":
                                    res = Program.int_div(x, y)
                                if op == "%":
                                    res = Program.int_mod(x, y)
                                new_grid[i][j + 1] = res
                                new_grid[i + 1][j] = res
        done = True
        for i in range(self.height):
            for j in range(self.width):
                if new_grid[i][j] != self.grid[i][j]:
                    done = False
                    if self.grid[i][j] == "S":
                        print(f"Submitted {new_grid[i][j]}.")
                        return True
        self.grid = new_grid
        if warp_dt != None:
            for i in range(warp_dt):
                self.timeline.pop()
            self.row_offset, self.col_offset, self.grid = self.timeline[-1]
            self.grid = [row[:] for row in self.grid]
            self.height = len(self.grid)
            self.width = len(self.grid[0])
            for (val, row, col) in warps:
                self.set_value(val, row, col)
            done = False
        else:
            self.add_to_timeline()
        self.fix_and_print()
        return done

    def run(self):
        self.fix_and_print()
        self.add_to_timeline()
        step_count = 0
        while True:
            if input() != "":
                break
            done = self.step()
            step_count += 1
            if done:
                print(f"Program finished. {step_count} steps.")
                break

if __name__ == "__main__":
    while True:
        file_name = input() + ".txt"
        with open(file_name, "r") as file:
            Program(file.read()).run()
