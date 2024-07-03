import sys
import threading
sys.path.insert(0, "..")
import basic

DIRS = "UDLR"

if __name__ == "__main__":
    test_num = int(sys.argv[1])
    file_path = f"output/output{test_num}.txt"
    with open(file_path, "r") as file:
        moves = file.read()

        moves_hash = 1
        for d in moves:
            moves_hash = moves_hash * 4 + DIRS.index(d)

        prefix = basic.Parser.encode_ascii(f"solve lambdaman{test_num} ")
        program = f'B. S{prefix} B$ B$ L1 L2 B$ B$ v1 v1 v2 L3 L4 ? B= v4 I" S B. B$ B$ v3 v3 B/ v4 I% B$ L5 ? B= v5 I! SO ? B= v5 I" S> ? B= v5 I# SF SL B% v4 I% I{basic.Parser.encode_base94(moves_hash)}'

        text = basic.send_program(program)

        print(basic.Parser(text).parse())

