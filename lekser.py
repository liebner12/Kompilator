import ply.lex as lex

tokens = (
	'DECLARE', 'BEGIN', 'END', "COMMA", 'COLON', 'SEMICOLON', 'ASSIGN', 'ID',
	'READ', 'WRITE',
	'NUMBER', 'PLUS', 'MINUS', 'MULT', 'DIV', 'MOD',
	'EQUALS', 'NEQUALS', 'LESS', 'GREATER', 'LESSEQ', 'GREATEREQ',
	'PAREN_OPEN', 'PAREN_CLOSE',  'IF', 'THEN', 'ELSE', 'ENDIF',
	'FOR', 'FROM', 'TO', 'DOWNTO', 'DO', 'ENDFOR',
	'WHILE', 'ENDWHILE', 'REPEAT', 'UNTIL',
)

t_DECLARE = r'DECLARE'
t_BEGIN = r'BEGIN'
t_END = r'END'
t_COMMA = r','
t_COLON = r':'
t_SEMICOLON = r';'
t_ASSIGN = r':='
t_ID = r'[_a-z]+'
t_READ = r'READ'
t_WRITE = r'WRITE'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_MULT = r'\*'
t_DIV = r'\/'
t_MOD = r'\%'
t_EQUALS = r'='
t_NEQUALS = r'!='
t_LESS = r'<'
t_GREATER = r'>'
t_LESSEQ = r'<='
t_GREATEREQ = r'>='
t_PAREN_OPEN = r'\('
t_PAREN_CLOSE = r'\)'
t_IF = r'IF'
t_THEN = r'THEN'
t_ELSE = r'ELSE'
t_ENDIF = r'ENDIF'
t_FOR = r'FOR'
t_FROM = r'FROM'
t_TO = r'TO'
t_DOWNTO = r'DOWNTO'
t_DO = r'DO'
t_ENDFOR = r'ENDFOR'
t_WHILE = r'WHILE'
t_ENDWHILE = r'ENDWHILE'
t_REPEAT = r'REPEAT'
t_UNTIL = r'UNTIL'


def t_NUMBER(t):
	r'\d+'
	t.value = int(t.value)
	return t


def t_COMMENT(t):
	r'\[[^\]]*\]'
	pass


t_ignore = ' \t'


def t_newline(t):
	r'\r?\n+'
	t.lexer.lineno += len(t.value)


def t_error(t):
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)


def p_error(p):
	print("Syntax error in line %d" % p.lineno)


lexer = lex.lex()
