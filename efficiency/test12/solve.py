import sys

def f(var4):
    if var4 <= 2:
        return var4
    else:
        return min(var4, g(var4, 2, var4) + 1)

def h(var4, var6, var7):
    if f(var6) >= var6 and var4 % var6 == 0:
        return var7 // f(var6) * (f(var6) - 1)
    else:
        return var7

def g(var4, var6, var7):
    if var6 == var4:
        return var7
    else:
        return g(var4, var6 + 1, h(var4, var6, var7))


def main():
    for i in range(2, 21):
        print(i, f(i))

if __name__ == "__main__":
    main()