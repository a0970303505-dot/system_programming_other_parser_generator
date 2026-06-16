"""
PLY Lexer for Simplified Pascal (Figure 5.2)
=============================================
PLY (Python Lex-Yacc) provides lex and yacc tools as Python modules.
The lexer tokenises a Pascal-like source into token objects consumed by the parser.
"""

import ply.lex as lex

# ── Reserved keywords ──────────────────────────────────────────────────────────
reserved = {
    "PROGRAM" : "PROGRAM",
    "VAR"     : "VAR",
    "BEGIN"   : "BEGIN",
    "END"     : "END",
    "INTEGER" : "INTEGER",
    "READ"    : "READ",
    "WRITE"   : "WRITE",
    "FOR"     : "FOR",
    "DO"      : "DO",
    "TO"      : "TO",
    "DIV"     : "DIV",
}

# ── Token list ─────────────────────────────────────────────────────────────────
tokens = list(reserved.values()) + [
    "ID",
    "INT_LITERAL",
    "ASSIGN",       # :=
    "COLON",        # :
    "SEMICOLON",    # ;
    "COMMA",        # ,
    "DOT",          # .
    "LPAREN",       # (
    "RPAREN",       # )
    "PLUS",         # +
    "MINUS",        # -
    "TIMES",        # *
]

# ── Simple token rules ─────────────────────────────────────────────────────────
t_ASSIGN    = r":="
t_COLON     = r":"
t_SEMICOLON = r";"
t_COMMA     = r","
t_DOT       = r"\."
t_LPAREN    = r"\("
t_RPAREN    = r"\)"
t_PLUS      = r"\+"
t_MINUS     = r"-"
t_TIMES     = r"\*"

# ── Identifier / keyword rule ──────────────────────────────────────────────────
def t_ID(t):
    r"[a-zA-Z][a-zA-Z0-9]*"
    t.type = reserved.get(t.value, "ID")   # check reserved words
    return t

# ── Integer literal ────────────────────────────────────────────────────────────
def t_INT_LITERAL(t):
    r"\d+"
    t.value = int(t.value)
    return t

# ── Whitespace / newlines (ignored, but track line numbers) ───────────────────
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

t_ignore = " \t\r"

# ── Error handler ─────────────────────────────────────────────────────────────
def t_error(t):
    print(f"[LEX ERROR] Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# ── Build the lexer ───────────────────────────────────────────────────────────
lexer = lex.lex()
