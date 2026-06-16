"""
Parser Generator #2: PLY (Python Lex-Yacc)  —  LALR(1)
==========================================================
Full test suite: 5 team tests + 5 personal tests
"""

import sys, os
import ply.yacc as yacc
from pascal_lexer import tokens, lexer   # noqa: F401

# ── AST node classes ──────────────────────────────────────────────────────────
class Program:
    def __init__(self, name, dec_list, stmt_list):
        self.name = name; self.dec_list = dec_list; self.stmt_list = stmt_list

class DecList:
    def __init__(self, decs): self.decs = decs

class Dec:
    def __init__(self, names, type_): self.names = names; self.type_ = type_

class StmtList:
    def __init__(self, stmts): self.stmts = stmts

class Assign:
    def __init__(self, var, exp): self.var = var; self.exp = exp

class Read:
    def __init__(self, names): self.names = names

class Write:
    def __init__(self, names): self.names = names

class For:
    def __init__(self, var, start, stop, body):
        self.var = var; self.start = start; self.stop = stop; self.body = body

class Body:
    def __init__(self, stmts): self.stmts = stmts

class BinOp:
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right

class Num:
    def __init__(self, value): self.value = value

class Var:
    def __init__(self, name): self.name = name


# ── AST pretty-printer ────────────────────────────────────────────────────────
def print_ast(node, indent=0):
    prefix = "  " * indent
    if isinstance(node, Program):
        print(f"{prefix}[Program: {node.name}]")
        print_ast(node.dec_list, indent + 1)
        print_ast(node.stmt_list, indent + 1)
    elif isinstance(node, DecList):
        print(f"{prefix}[DecList]")
        for d in node.decs:
            print_ast(d, indent + 1)
    elif isinstance(node, Dec):
        print(f"{prefix}[Dec: {', '.join(node.names)} : {node.type_}]")
    elif isinstance(node, StmtList):
        print(f"{prefix}[StmtList]")
        for s in node.stmts:
            print_ast(s, indent + 1)
    elif isinstance(node, Assign):
        print(f"{prefix}[Assign: {node.var} :=]")
        print_ast(node.exp, indent + 1)
    elif isinstance(node, Read):
        print(f"{prefix}[Read: {', '.join(node.names)}]")
    elif isinstance(node, Write):
        print(f"{prefix}[Write: {', '.join(node.names)}]")
    elif isinstance(node, For):
        print(f"{prefix}[For: {node.var} :=]")
        print(f"{prefix}  [Start]")
        print_ast(node.start, indent + 2)
        print(f"{prefix}  [Stop]")
        print_ast(node.stop, indent + 2)
        print(f"{prefix}  [Body]")
        print_ast(node.body, indent + 2)
    elif isinstance(node, Body):
        print(f"{prefix}[Body]")
        for s in node.stmts:
            print_ast(s, indent + 1)
    elif isinstance(node, BinOp):
        print(f"{prefix}[BinOp: {node.op}]")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
    elif isinstance(node, Num):
        print(f"{prefix}[Num: {node.value}]")
    elif isinstance(node, Var):
        print(f"{prefix}[Var: {node.name}]")
    else:
        print(f"{prefix}{repr(node)}")


# ── Grammar rules ─────────────────────────────────────────────────────────────
def p_prog(p):
    """prog : PROGRAM ID VAR dec_list BEGIN stmt_list END DOT"""
    p[0] = Program(p[2], p[4], p[6])

def p_dec_list_single(p):
    """dec_list : dec"""
    p[0] = DecList([p[1]])

def p_dec_list_multi(p):
    """dec_list : dec_list SEMICOLON dec"""
    p[0] = DecList(p[1].decs + [p[3]])

def p_dec(p):
    """dec : id_list COLON type_rule"""
    p[0] = Dec(p[1], p[3])

def p_type_rule(p):
    """type_rule : INTEGER"""
    p[0] = "INTEGER"

def p_id_list_single(p):
    """id_list : ID"""
    p[0] = [p[1]]

def p_id_list_multi(p):
    """id_list : id_list COMMA ID"""
    p[0] = p[1] + [p[3]]

def p_stmt_list_single(p):
    """stmt_list : stmt"""
    p[0] = StmtList([p[1]])

def p_stmt_list_multi(p):
    """stmt_list : stmt_list SEMICOLON stmt"""
    p[0] = StmtList(p[1].stmts + [p[3]])

def p_stmt(p):
    """stmt : assign_stmt
            | read_stmt
            | write_stmt
            | for_stmt"""
    p[0] = p[1]

def p_assign_stmt(p):
    """assign_stmt : ID ASSIGN exp"""
    p[0] = Assign(p[1], p[3])

def p_exp_term(p):
    """exp : term"""
    p[0] = p[1]

def p_exp_plus(p):
    """exp : exp PLUS term"""
    p[0] = BinOp("+", p[1], p[3])

def p_exp_minus(p):
    """exp : exp MINUS term"""
    p[0] = BinOp("-", p[1], p[3])

def p_term_factor(p):
    """term : factor"""
    p[0] = p[1]

def p_term_times(p):
    """term : term TIMES factor"""
    p[0] = BinOp("*", p[1], p[3])

def p_term_div(p):
    """term : term DIV factor"""
    p[0] = BinOp("DIV", p[1], p[3])

def p_factor_id(p):
    """factor : ID"""
    p[0] = Var(p[1])

def p_factor_int(p):
    """factor : INT_LITERAL"""
    p[0] = Num(p[1])

def p_factor_paren(p):
    """factor : LPAREN exp RPAREN"""
    p[0] = p[2]

def p_read_stmt(p):
    """read_stmt : READ LPAREN id_list RPAREN"""
    p[0] = Read(p[3])

def p_write_stmt(p):
    """write_stmt : WRITE LPAREN id_list RPAREN"""
    p[0] = Write(p[3])

def p_for_stmt(p):
    """for_stmt : FOR index_exp DO body"""
    var, start_exp, stop_exp = p[2]
    p[0] = For(var, start_exp, stop_exp, p[4])

def p_index_exp(p):
    """index_exp : ID ASSIGN exp TO exp"""
    p[0] = (p[1], p[3], p[5])

def p_body_stmt(p):
    """body : stmt"""
    p[0] = Body([p[1]])

def p_body_compound(p):
    """body : BEGIN stmt_list END"""
    p[0] = Body(p[2].stmts)

def p_error(p):
    if p:
        print(f"[PARSE ERROR] Unexpected token '{p.value}' ({p.type}) at line {p.lineno}")
    else:
        print("[PARSE ERROR] Unexpected end of input")

parser_obj = yacc.yacc(debug=False, write_tables=False)


# ── AST Evaluator ─────────────────────────────────────────────────────────────
class Evaluator:
    def __init__(self):
        self.env = {}

    def run(self, node):
        return getattr(self, "eval_" + type(node).__name__)(node)

    def eval_Program(self, node):
        print(f"\n=== Pascal Program '{node.name}' ===\n")
        self.run(node.dec_list)
        self.run(node.stmt_list)

    def eval_DecList(self, node):
        for d in node.decs:
            self.run(d)

    def eval_Dec(self, node):
        for name in node.names:
            self.env[name] = 0
            print(f"  DECLARE  {name} : INTEGER  (init=0)")

    def eval_StmtList(self, node):
        for s in node.stmts:
            self.run(s)

    def eval_Assign(self, node):
        if node.var not in self.env:
            raise NameError(f"Undeclared variable: '{node.var}'")
        val = self.run(node.exp)
        self.env[node.var] = val
        print(f"  ASSIGN   {node.var} := {val}")

    def eval_Read(self, node):
        for name in node.names:
            if name not in self.env:
                raise NameError(f"Undeclared variable: '{name}'")
            val = int(input(f"  READ     {name} = ? "))
            self.env[name] = val

    def eval_Write(self, node):
        for name in node.names:
            if name not in self.env:
                raise NameError(f"Undeclared variable: '{name}'")
            print(f"  WRITE    {name} = {self.env[name]}")

    def eval_For(self, node):
        if node.var not in self.env:
            raise NameError(f"Undeclared loop variable: '{node.var}'")
        start = self.run(node.start)
        stop  = self.run(node.stop)
        print(f"  FOR      {node.var} := {start} TO {stop}")
        for i in range(start, stop + 1):
            self.env[node.var] = i
            self.run(node.body)

    def eval_Body(self, node):
        for s in node.stmts:
            self.run(s)

    def eval_BinOp(self, node):
        left  = self.run(node.left)
        right = self.run(node.right)
        if node.op == "+":   return left + right
        if node.op == "-":   return left - right
        if node.op == "*":   return left * right
        if node.op == "DIV": return left // right
        raise ValueError(f"Unknown op: {node.op}")

    def eval_Num(self, node):
        return node.value

    def eval_Var(self, node):
        if node.name not in self.env:
            raise NameError(f"Undeclared variable: '{node.name}'")
        return self.env[node.name]


# ── parse + run helper ────────────────────────────────────────────────────────
def parse_and_run(source: str, label: str):
    print("=" * 60)
    print(f"  {label}")
    print("=" * 60)
    print("\n[Source Code]")
    print(source)
    try:
        ast = parser_obj.parse(source, lexer=lexer.clone())
        if ast is None:
            print("[ERROR] Parse returned no AST (syntax error above)")
            return
        print("\n[AST]")
        print_ast(ast)
        print("\n[Execution Trace]")
        ev = Evaluator()
        ev.run(ast)
        print("\n[Final Variable State]")
        for k, v in ev.env.items():
            print(f"  {k} = {v}")
        print("\n=> Parse & execution SUCCESS\n")
    except Exception as e:
        print(f"\n[ERROR] {e}\n")


# ── Team Test programs ─────────────────────────────────────────────────────────
TEST1 = """\
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

TEST2 = """\
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

TEST3 = """\
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

TEST4 = """\
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

TEST5 = """\
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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            source = f.read()
        parse_and_run(source, f"File: {sys.argv[1]}")
    else:
        # Team tests
        parse_and_run(TEST1, "Test 1 — SumDemo       (FOR loop, sum 1..5 = 15)")
        parse_and_run(TEST2, "Test 2 — ArithDemo     (* and DIV operators)")
        parse_and_run(TEST3, "Test 3 — ParenDemo     (parenthesised expressions)")
        parse_and_run(TEST4, "Test 4 — NestedFor     (3x3 = 9)")
        parse_and_run(TEST5, "Test 5 — ErrorDemo     (syntax error handling)")
        # Personal tests
        parse_and_run(TEST_READ,       "Personal Test 1 — ReadDemo      (READ input)")
        parse_and_run(TEST_MIXED,      "Personal Test 2 — MixedArith    (mixed operators)")
        parse_and_run(TEST_MULTIDEC,   "Personal Test 3 — MultiDec      (multiple declarations)")
        parse_and_run(TEST_FIBONACCI,  "Personal Test 4 — Fibonacci     (sequence)")
        parse_and_run(TEST_SUMSQUARES, "Personal Test 5 — SumOfSquares  (sum of squares)")