import sys

class Tree:
    def __init__(self, labels, edges):
        self.labels = labels
        self.children = [[] for i in range(len(labels))]
        for (u, v) in edges:
            self.children[u].append(v)
        self.var_order = []

    def dfs(self, u):
        if self.labels[u].startswith("lambda"):
            self.var_order.append(self.labels[u][7:])
        children = []
        for v in self.children[u]:
            if self.labels[v] != "U!" and self.labels[v] != "B+":
                self.dfs(v);
                children.append(self.labels[v])
        if self.labels[u] == "B=":
            print(self.var_order.index(children[0]), children[1])

    def solve(self):
        self.dfs(19)

def main():
    sys.setrecursionlimit(10000)
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