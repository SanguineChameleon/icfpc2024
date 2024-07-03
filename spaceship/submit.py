import sys
import threading
sys.path.insert(0, "..")
import basic

if __name__ == "__main__":
    test_num = int(sys.argv[1])
    file_path = f"files/test{test_num}/output.txt"
    with open(file_path, "r") as file:
        moves = file.read()

        if len(moves) % 2 == 1:
            moves = moves + "0"

        moves_hash = ""
        for i in range(0, len(moves), 2):
            moves_hash += chr(33 + (ord(moves[i]) - ord('1')) * 10 + (ord(moves[i + 1]) - ord('0')))

        prefix = basic.Parser.encode_ascii(f"solve spaceship{test_num} ")
        if_part = ""
        for i in range(9):
            for j in range(10):
                s = chr(33 + i * 10 + j)
                t = basic.Parser.encode_ascii(chr(ord('1') + i))
                if j > 0:
                    t += basic.Parser.encode_ascii(chr(ord('0') + j))
                if_part += f"? B= v5 S{s} S{t} "
        if_part += "S"

        program = f'B. S{prefix} B$ B$ L1 L2 B$ B$ v1 v1 v2 L3 L4 ? B= v4 S S B. B$ L5 {if_part} BT I" v4 B$ B$ v3 v3 BD I" v4 S{moves_hash}'

        print(basic.Parser(program).parse())

        #print(basic.Parser(basic.send_program(program)).parse())

