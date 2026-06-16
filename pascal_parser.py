"""
Parser Generator #1: Lark (LALR) — EBNF Grammar
================================================
Full test suite: 5 team tests + 5 personal tests
"""

import sys
import os
from lark import Lark, Tree, Token
from lark.exceptions import UnexpectedToken, UnexpectedCharacters

GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), "pascal_grammar.lark")
with open(GRAMMAR_FILE, encoding="utf-8") as f:
    GRAMMAR = f.read()

parser = Lark(GRAMMAR, start="prog", parser="lalr")


def print_tree(node, indent=0):
    prefix = "  " * indent
    if isinstance(node, Tree):
        print(f"{prefix}[{node.data}]")
        for child in node.children:
            print_tree(child, indent + 1)
    elif isinstance(node, Token):
        print(f"{prefix}TOKEN({node.type}) = '{node}'")


class PascalInterpreter:
    def __init__(self):
        self.env: dict[str, int] = {}

    def _first_tree(self, node: Tree, rule: str):
        for c in node.children:
            if isinstance(c, Tree) and c.data == rule:
                return c
        return None

    def run(self, tree: Tree):
        prog_name = str(tree.children[0])
        print(f"\n=== Running Pascal Program: {prog_name} ===\n")
        dec_list  = self._first_tree(tree, "dec_list")
        stmt_list = self._first_tree(tree, "stmt_list")
        self.visit_dec_list(dec_list)
        self.visit_stmt_list(stmt_list)
        print("\n[Final Variable State]")
        for k, v in self.env.items():
            print(f"  {k} = {v}")

    def visit_dec_list(self, node: Tree):
        for child in node.children:
            if isinstance(child, Tree) and child.data == "dec":
                self.visit_dec(child)

    def visit_dec(self, node: Tree):
        id_list_node = self._first_tree(node, "id_list")
        for name in self.collect_ids(id_list_node):
            self.env[name] = 0
            print(f"  DECLARE  {name} : INTEGER  (init=0)")

    def collect_ids(self, node: Tree) -> list[str]:
        return [str(c) for c in node.children if isinstance(c, Token) and c.type == "ID"]

    def visit_stmt_list(self, node: Tree):
        for child in node.children:
            if isinstance(child, Tree) and child.data == "stmt":
                self.visit_stmt(child)

    def visit_stmt(self, node: Tree):
        child = node.children[0]
        dispatch = {
            "assign_stmt": self.visit_assign,
            "read_stmt":   self.visit_read,
            "write_stmt":  self.visit_write,
            "for_stmt":    self.visit_for,
        }
        dispatch[child.data](child)

    def visit_assign(self, node: Tree):
        name = str(node.children[0])
        exp_node = self._first_tree(node, "exp")
        value = self.eval_exp(exp_node)
        if name not in self.env:
            raise NameError(f"Undeclared variable: {name}")
        self.env[name] = value
        print(f"  ASSIGN   {name} := {value}")

    def visit_read(self, node: Tree):
        ids = self.collect_ids(self._first_tree(node, "id_list"))
        for name in ids:
            if name not in self.env:
                raise NameError(f"Undeclared variable: {name}")
            self.env[name] = int(input(f"  READ     {name} = ? "))

    def visit_write(self, node: Tree):
        ids = self.collect_ids(self._first_tree(node, "id_list"))
        for name in ids:
            if name not in self.env:
                raise NameError(f"Undeclared variable: {name}")
            print(f"  WRITE    {name} = {self.env[name]}")

    def visit_for(self, node: Tree):
        children = node.children
        var_name  = str(children[0])
        exps      = [c for c in children if isinstance(c, Tree) and c.data == "exp"]
        body_node = self._first_tree(node, "body")
        start = self.eval_exp(exps[0])
        stop  = self.eval_exp(exps[1])
        print(f"  FOR      {var_name} := {start} TO {stop}")
        for i in range(start, stop + 1):
            self.env[var_name] = i
            self.visit_body(body_node)

    def visit_body(self, node: Tree):
        for child in node.children:
            if isinstance(child, Tree):
                if child.data == "stmt":
                    self.visit_stmt(child)
                elif child.data == "stmt_list":
                    self.visit_stmt_list(child)

    def eval_exp(self, node: Tree) -> int:
        result = self.eval_term(node.children[0])
        i = 1
        while i < len(node.children):
            op    = node.children[i].type
            right = self.eval_term(node.children[i + 1])
            result = result + right if op == "PLUS" else result - right
            i += 2
        return result

    def eval_term(self, node: Tree) -> int:
        if isinstance(node, Token):
            return int(node) if node.type == "INT_LIT" else self.env[str(node)]
        result = self.eval_factor(node.children[0])
        i = 1
        while i < len(node.children):
            op    = node.children[i].type
            right = self.eval_factor(node.children[i + 1])
            result = result * right if op == "TIMES" else result // right
            i += 2
        return result

    def eval_factor(self, node) -> int:
        if isinstance(node, Token):
            return int(node) if node.type == "INT_LIT" else self.env[str(node)]
        child = node.children[0]
        if isinstance(child, Token):
            if child.type == "INT_LIT":
                return int(child)
            return self.env[str(child)]
        return self.eval_exp(child)


# ── Team Test programs ─────────────────────────────────────────────────────────
TEST_SUM = """\
PROGRAM SumDemo VAR
    i, total, n : INTEGER
BEGIN
    n := 5 ;
    total := 0 ;
    FOR i := 1 TO n DO
        total := total + i ;
    WRITE ( total )
END.
"""

TEST_ARITH = """\
PROGRAM ArithDemo VAR
    a, b, c, d : INTEGER
BEGIN
    a := 10 ;
    b := 3 ;
    c := a * b ;
    d := c DIV 5 ;
    WRITE ( a ) ;
    WRITE ( b ) ;
    WRITE ( c ) ;
    WRITE ( d )
END.
"""

TEST_PAREN = """\
PROGRAM ParenDemo VAR
    a, b, c, result : INTEGER
BEGIN
    a := 3 ;
    b := 4 ;
    c := 2 ;
    result := ( a + b ) * c ;
    WRITE ( result ) ;
    result := a + b * c ;
    WRITE ( result ) ;
    result := ( a + b ) * ( c + 1 ) ;
    WRITE ( result )
END.
"""

TEST_NESTED = """\
PROGRAM NestedFor VAR
    i, j, cnt : INTEGER
BEGIN
    cnt := 0 ;
    FOR i := 1 TO 3 DO
        FOR j := 1 TO 3 DO
            cnt := cnt + 1 ;
    WRITE ( cnt )
END.
"""

TEST_ERROR = """\
PROGRAM ErrorDemo VAR
    x : INTEGER
BEGIN
    x := + 5 ;
    y := 10
END.
"""

# ── Personal Test programs ─────────────────────────────────────────────────────
TEST_READ = """\
PROGRAM ReadDemo VAR
    a, b, result : INTEGER
BEGIN
    READ ( a ) ;
    READ ( b ) ;
    result := a + b ;
    WRITE ( result )
END.
"""

TEST_MIXED = """\
PROGRAM MixedArith VAR
    a, b, c, result : INTEGER
BEGIN
    a := 20 ;
    b := 6 ;
    c := 3 ;
    result := a - b * c + ( a DIV c ) ;
    WRITE ( result )
END.
"""

TEST_MULTIDEC = """\
PROGRAM MultiDec VAR
    x, y : INTEGER ;
    z : INTEGER ;
    result : INTEGER
BEGIN
    x := 3 ;
    y := 4 ;
    z := 5 ;
    result := x + y + z ;
    WRITE ( result )
END.
"""

TEST_FIBONACCI = """\
PROGRAM Fibonacci VAR
    i, a, b, temp, n : INTEGER
BEGIN
    n := 8 ;
    a := 0 ;
    b := 1 ;
    WRITE ( a ) ;
    WRITE ( b ) ;
    FOR i := 1 TO n DO BEGIN
        temp := a + b ;
        a := b ;
        b := temp ;
        WRITE ( b )
    END
END.
"""

TEST_SUMSQUARES = """\
PROGRAM SumOfSquares VAR
    i, n, sum, sq : INTEGER
BEGIN
    n := 5 ;
    sum := 0 ;
    FOR i := 1 TO n DO BEGIN
        sq := i * i ;
        sum := sum + sq ;
        WRITE ( sq )
    END ;
    WRITE ( sum )
END.
"""


def parse_and_run(source: str, label: str):
    print("=" * 60)
    print(f"  {label}")
    print("=" * 60)
    print("\n[Source Code]")
    print(source)

    try:
        tree = parser.parse(source)
        print("\n[Parse Tree]")
        print_tree(tree)
        print("\n[Execution Trace]")
        interp = PascalInterpreter()
        interp.run(tree)
        print("\n=> Parse & execution SUCCESS\n")
    except (UnexpectedToken, UnexpectedCharacters) as e:
        print(f"\n[PARSE ERROR] {e}\n")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n[RUNTIME ERROR] {e}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            source = f.read()
        parse_and_run(source, f"File: {sys.argv[1]}")
    else:
        # Team tests
        parse_and_run(TEST_SUM,        "Test 1 — SumDemo       (FOR loop, sum 1..5 = 15)")
        parse_and_run(TEST_ARITH,      "Test 2 — ArithDemo     (* and DIV operators)")
        parse_and_run(TEST_PAREN,      "Test 3 — ParenDemo     (parenthesised expressions)")
        parse_and_run(TEST_NESTED,     "Test 4 — NestedFor     (3x3 = 9)")
        parse_and_run(TEST_ERROR,      "Test 5 — ErrorDemo     (syntax error handling)")
        # Personal tests
        parse_and_run(TEST_READ,       "Personal Test 1 — ReadDemo      (READ input)")
        parse_and_run(TEST_MIXED,      "Personal Test 2 — MixedArith    (mixed operators)")
        parse_and_run(TEST_MULTIDEC,   "Personal Test 3 — MultiDec      (multiple declarations)")
        parse_and_run(TEST_FIBONACCI,  "Personal Test 4 — Fibonacci     (sequence)")
        parse_and_run(TEST_SUMSQUARES, "Personal Test 5 — SumOfSquares  (sum of squares)")