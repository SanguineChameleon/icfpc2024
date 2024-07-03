import z3 

class Tree:
    def __init__(self, labels, edges):
        self.labels = labels
        self.children = [[] for i in range(len(labels))]
        for (u, v) in edges:
            self.children[u].append(v)

    def dfs(self, u):
        if self.labels[u].startswith("var"):
            return self.variables[int(self.labels[u][3:]) - 1]
        children = []
        for v in self.children[u]:
            children.append(self.dfs(v))
        if self.labels[u] == "U!":
            return z3.Not(children[0])
        if self.labels[u] == "B|":
            return z3.Or(children[0], children[1])
        if self.labels[u] == "B&":
            return z3.And(children[0], children[1])
        assert False

    def solve(self):
        solver = z3.Solver()
        self.variables = [z3.Bool(f"var{i}") for i in range(1, 41)]
        solver.add(self.dfs(99))
        min_res = None
        while True:
            if solver.check() == z3.unsat:
                break
            model = solver.model()
            res = 0
            conditions = []
            for variable in model:
                name = variable.name()
                var_num = int(name[3:]) - 1
                if model[variable]:
                    res |= 1 << var_num
                    conditions.append(self.variables[var_num])
                else:
                    conditions.append(z3.Not(self.variables[var_num]))
            if min_res == None or res < min_res:
                min_res = res
            print(res)
            solver.add(z3.Not(z3.And(*conditions)))
        print()
        print(min_res)

def main():
    with open("tree.dot", "r") as file:
        lines = file.read().split("\n")
        labels = []
        edges = []
        for line in lines:
            line = line.strip()
            if "label" in line:
                label = line.split("[label = ")[1][1:-3]
                labels.append(label)
            if "->" in line:
                u, v = map(int, line[:-1].split("->"))
                edges.append((u, v))
        Tree(labels, edges).solve()

if __name__ == "__main__":
    main()