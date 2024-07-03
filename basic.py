import os
import requests
import time
import sys
import threading

API_URL = "https://boundvariable.space/communicate"
API_TOKEN = os.environ["ICFPC_2024_API_TOKEN"]

HUMAN_ALPHABET = """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n"""
ALIEN_ALPHABET = "".join(chr(i) for i in range(33, 127))

class Parser:
    class Literal:
        def __init__(self, value):
            self.value = value

    class Token:
        def __init__(self, value):
            self.value = value

    def __init__(self, s):
        self.tokens = []
        for value in s.split():
            self.tokens.append(Parser.Token(value))
        self.tokens.reverse()
        self.rename_cnt = 0
        self.reduce_cnt = 0

    @staticmethod
    def decode_ascii(s):
        return s.translate(str.maketrans(ALIEN_ALPHABET, HUMAN_ALPHABET))

    @staticmethod
    def encode_ascii(s):
        return s.translate(str.maketrans(HUMAN_ALPHABET, ALIEN_ALPHABET))

    @staticmethod
    def encode_base94(x):
        res = ""
        while x > 0:
            res += chr(x % 94 + 33)
            x //= 94
        res = res[::-1]
        return res

    @staticmethod
    def decode_base94(s):
        res = 0
        for c in s:
            res = res * 94 + (ord(c) - 33)
        return res

    @staticmethod
    def int_div(x, y):
        res = abs(x) // abs(y)
        if (x < 0 and y > 0) or (x > 0 and y < 0):
            res = -res
        return res

    @staticmethod
    def int_mod(x, y):
        return x - Parser.int_div(x, y) * y

    def rename_free(self, terms, free):
        renamed_terms = []
        self.rename_cnt += 1
        for term in terms:
            if isinstance(term, Parser.Token):
                indicator = term.value[0]
                if indicator == "v":
                    old_var_name = term.value[1:]
                    if old_var_name in free:
                        new_var_name = f"{Parser.decode_base94(old_var_name)}_{self.rename_cnt}"
                        renamed_terms.append(Parser.Token("v" + new_var_name))
                    else:
                        renamed_terms.append(term)
                else:
                    renamed_terms.append(term)
            else:
                renamed_terms.append(term)
        return renamed_terms

    def read_and_alpha_rename(self, terms):
        while True:
            term = terms.pop()
            if isinstance(term, Parser.Literal):
                return ([term], [])
            indicator = term.value[0]
            body = term.value[1:]
            if indicator == "(" or indicator == ")":
                continue
            break
        indicator = term.value[0]
        body = term.value[1:]
        if indicator == "T" or indicator == "F" or indicator == "I" or indicator == "S":
            return ([term], [])
        if indicator == "U":
            x_terms, x_free = self.read_and_alpha_rename(terms)
            return ([term] + x_terms, x_free)
        if indicator == "B":
            x_terms, x_free = self.read_and_alpha_rename(terms)
            y_terms, y_free = self.read_and_alpha_rename(terms)
            return ([term] + x_terms + y_terms, x_free + y_free)
        if indicator == "?":
            x_terms, x_free = self.read_and_alpha_rename(terms)
            y_terms, y_free = self.read_and_alpha_rename(terms)
            z_terms, z_free = self.read_and_alpha_rename(terms)
            return ([term] + x_terms + y_terms + z_terms, x_free + y_free + z_free)
        if indicator == "v":
            var_name = body
            return ([term], [var_name])
        if indicator == "L":
            old_var_name = body
            x_terms, x_free = self.read_and_alpha_rename(terms)
            while old_var_name in x_free:
                x_free.remove(old_var_name)
            self.rename_cnt += 1
            new_var_name = f"{Parser.decode_base94(old_var_name)}_{self.rename_cnt}"
            renamed_terms = [Parser.Token("L" + new_var_name)]
            for term in x_terms:
                if isinstance(term, Parser.Token):
                    indicator = term.value[0]
                    body = term.value[1:]
                    if indicator == "v" and body == old_var_name:
                        renamed_terms.append(Parser.Token("v" + new_var_name))
                    else:
                        renamed_terms.append(term)
                else:
                    renamed_terms.append(term)
            return (renamed_terms, x_free)


    def read_only(self, terms):
        while True:
            term = terms.pop()
            if isinstance(term, Parser.Literal):
                return [term]
            indicator = term.value[0]
            body = term.value[1:]
            if indicator == "(" or indicator == ")":
                continue
            break
        indicator = term.value[0]
        body = term.value[1:]
        if indicator == "T" or indicator == "F" or indicator == "I" or indicator == "S" or indicator == "v":
            return [term]
        if indicator == "U":
            x_terms = self.read_only(terms)
            return [term] + x_terms
        if indicator == "B":
            x_terms = self.read_only(terms)
            y_terms = self.read_only(terms)
            return [term] + x_terms + y_terms
        if indicator == "?":
            x_terms = self.read_only(terms)
            y_terms = self.read_only(terms)
            z_terms = self.read_only(terms)
            return [term] + x_terms + y_terms + z_terms
        if indicator == "L":
            x_terms = self.read_only(terms)
            return [Parser.Token("("), term] + x_terms + [Parser.Token(")")]

    def beta_reduce(self, lambda_terms, value_terms):
        self.reduce_cnt += 1
        tmp = self.reduce_cnt
        reduced_terms = []
        done = False
        in_scope = False
        has_eval = False
        for term in lambda_terms:
            if isinstance(term, Parser.Literal):
                reduced_terms.append(term)
                continue
            indicator = term.value[0]
            body = term.value[1:]
            if not done and not in_scope and indicator == "L":
                reduced_terms.pop()
                in_scope = True
                var_num = Parser.decode_base94(body)
                is_shadowed = []
            if in_scope:
                if indicator == "L":
                    if len(is_shadowed) == 0:
                        is_shadowed.append(False)
                    else:
                        if Parser.decode_base94(body) == var_num:
                            is_shadowed.append(True)
                        else:
                            is_shadowed.append(is_shadowed[-1])
                        reduced_terms.append(term)
                elif indicator == ")":
                    is_shadowed.pop()
                    if len(is_shadowed) == 0:
                        in_scope = False
                        done = True
                    else:
                        reduced_terms.append(term)
                elif indicator == "v" and Parser.decode_base94(body) == var_num and not is_shadowed[-1]:
                    if not has_eval:
                        value_terms.reverse()
                        value_terms = self.read_and_eval(value_terms)
                        has_eval = True
                    reduced_terms += value_terms
                else:
                    reduced_terms.append(term)
            else:
                reduced_terms.append(term)
        if done:
            return reduced_terms
        else:
            return None

    def read_and_eval(self, terms):
        while True:
            term = terms.pop()
            if isinstance(term, Parser.Literal):
                return [term]
            indicator = term.value[0]
            body = term.value[1:]
            if indicator == "(" or indicator == ")":
                continue
            break
        if indicator == "T":
            return [Parser.Literal(True)]
        if indicator == "F":
            return [Parser.Literal(False)]
        if indicator == "I":
            return [Parser.Literal(Parser.decode_base94(body))]
        if indicator == "S":
            return [Parser.Literal(Parser.decode_ascii(body))]
        if indicator == "U":
            x_terms = self.read_and_eval(terms)
            if len(x_terms) == 1 and isinstance(x_terms[0], Parser.Literal):
                x_value = x_terms[0].value
                if body == "-":
                    return [Parser.Literal(-x_value)]
                if body == "!":
                    return [Parser.Literal(not x_value)]
                if body == "#":
                    return [Parser.Literal(Parser.decode_base94(Parser.encode_ascii(x_value)))]
                if body == "$":
                    return [Parser.Literal(Parser.decode_ascii(Parser.encode_base94(x_value)))]
            else:
                return [term] + x_terms
        if indicator == "B":
            if body == "$":
                x_terms = self.read_and_eval(terms)
                y_terms = self.read_only(terms)
                reduced_terms = self.beta_reduce(x_terms, y_terms)
                if reduced_terms == None:
                    return [term] + x_terms + y_terms
                else:
                    reduced_terms.reverse()
                    reduced_terms = self.read_and_eval(reduced_terms)
                    return reduced_terms
            else:
                x_terms = self.read_and_eval(terms)
                y_terms = self.read_and_eval(terms)
                if len(x_terms) == 1 and isinstance(x_terms[0], Parser.Literal) and len(y_terms) == 1 and isinstance(y_terms[0], Parser.Literal):
                    x_value = x_terms[0].value
                    y_value = y_terms[0].value
                    if body == "+":
                        return [Parser.Literal(x_value + y_value)]
                    if body == "-":
                        return [Parser.Literal(x_value - y_value)]
                    if body == "*":
                        return [Parser.Literal(x_value * y_value)]
                    if body == "/":
                        return [Parser.Literal(Parser.int_div(x_value, y_value))]
                    if body == "%":
                        return [Parser.Literal(Parser.int_mod(x_value, y_value))]
                    if body == "<":
                        return [Parser.Literal(x_value < y_value)]
                    if body == ">":
                        return [Parser.Literal(x_value > y_value)]
                    if body == "=":
                        return [Parser.Literal(x_value == y_value)]
                    if body == "|":
                        return [Parser.Literal(x_value or y_value)]
                    if body == "&":
                        return [Parser.Literal(x_value and y_value)]
                    if body == ".":
                        return [Parser.Literal(x_value + y_value)]
                    if body == "T":
                        return [Parser.Literal(y_value[:x_value])]
                    if body == "D":
                        return [Parser.Literal(y_value[x_value:])]
                else:
                    return [term] + x_terms + y_terms
        if indicator == "?":
            x_terms = self.read_and_eval(terms)
            y_terms = self.read_only(terms)
            z_terms = self.read_only(terms)
            if len(x_terms) == 1 and isinstance(x_terms[0], Parser.Literal):
                x_value = x_terms[0].value
                if x_value:
                    y_terms.reverse()
                    return self.read_and_eval(y_terms)
                else:
                    z_terms.reverse()
                    return self.read_and_eval(z_terms)
            else:
                return [term] + x_terms + y_terms + z_terms
        if indicator == "v":
            return [term]
        if indicator == "L":
            x_terms = self.read_and_eval(terms)
            return [Parser.Token("("), term] + x_terms + [Parser.Token(")")]

    def print_terms(self, terms):
        for term in terms:
            print(term.value, end = " ")
        print()

    def parse(self):
        terms, free = self.read_and_alpha_rename(self.tokens)
        terms = self.rename_free(terms, free)
        terms.reverse()
        terms = self.read_and_eval(terms)
        return terms[0].value

    def build_tree(self, terms):
        node_num = len(self.nodes)
        term = terms.pop()
        assert isinstance(term, Parser.Token)

        value = term.value
        indicator = value[0]
        body = value[1:]

        label = value
        if indicator == "T":
            label = "True"
        if indicator == "F":
            label = "False"
        if indicator == "I":
            label = str(Parser.decode_base94(body))
        if indicator == "S":
            decoded = Parser.decode_ascii(body)
            decoded = decoded.replace('\n', ' ')
            decoded = decoded.replace('\\', '\\\\')
            decoded = decoded.replace('"', '\\\"')
            label = f"\\\"{decoded}\\\""
        if indicator == "L":
            label = f"lambda var{Parser.decode_base94(body)}"
        if indicator == "v":
            label = f"var{Parser.decode_base94(body)}"

        child_count = 0
        if indicator == "U" or indicator == "L":
            child_count = 1
        if indicator == "B":
            child_count = 2
        if indicator == "?":
            child_count = 3

        self.nodes.append((node_num, label))
        for i in range(child_count):
            self.edges.append((node_num, self.build_tree(terms)))

        return node_num

    def write_tree(self):
        self.nodes = []
        self.edges = []
        self.build_tree(self.tokens)
        self.nodes.sort()
        with open("tree.dot", "w") as file:
            file.write("digraph tree {\n")
            file.write("    node [fontname = Courier]\n")
            for (u, label) in self.nodes:
                file.write(f'    {u} [label = "{label}"];\n')
            for (u, v) in self.edges:
                file.write(f'    {u} -> {v};\n')
            file.write("}")

def send_program(data):
    while True:
        try:
            headers = {"authorization": f"Bearer {API_TOKEN}"}
            res = requests.post(url = API_URL, headers = headers, data = data, timeout = 60)
            if res.status_code == 200:
                text = res.text
                return text
        except:
            pass
        time.sleep(5)

def send_plaintext(s):
    return send_program("S" + Parser.encode_ascii(s))

def main():
    while True:
        print(Parser(input()).parse())

if __name__ == "__main__":
    sys.setrecursionlimit(10 ** 6)
    threading.stack_size(2 ** 27)
    thread = threading.Thread(target = main)
    thread.start()
