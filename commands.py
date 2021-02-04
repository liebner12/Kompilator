import ply.yacc as yacc
from compilerStorage import CompilerStorage
from errorManager import ErrorManager
from lekser import tokens
from pointers import clearLines, addJumpPoints

compiler = CompilerStorage()
check = ErrorManager(compiler)


def p_program(p):
    '''program : DECLARE declarations BEGIN commands END'''
    p[0] = clearLines(p[4] + "HALT")


def p_expression_value(p):
    '''expression : value'''
    value, lineno = p[1], p.lineno(1)
    p[0] = loadVar(value, "b", lineno)


def p_value_number(p):
    '''value : NUMBER'''
    p[0] = ("num", p[1])


def p_value_identifier(p):
    '''value : identifier'''
    p[0] = (p[1])


def p_identifier_id(p):
    '''identifier : ID'''
    p[0] = ("id", p[1])


def p_identifier_tab_id(p):
    '''identifier : ID PAREN_OPEN ID PAREN_CLOSE'''
    p[0] = ("tab", p[1], ("id", p[3]))


def p_identifier(p):
    '''identifier : ID PAREN_OPEN NUMBER PAREN_CLOSE'''
    p[0] = ("tab", p[1], ("num", p[3]))


def p_declarations_variable(p):
    '''declarations	: declarations COMMA ID'''
    id, lineno = p[3], p.lineno(3)
    compiler.addVariable(id, lineno)


def p_declarations_array(p):
    '''declarations	: declarations COMMA ID PAREN_OPEN NUMBER COLON NUMBER PAREN_CLOSE'''
    id, begin, end, lineno = p[3], p[5], p[7], p.lineno(3)
    compiler.addArray(id, begin, end, lineno)


def p_declarations_last_variable(p):
    '''declarations	: ID'''
    id, lineno = p[1], p.lineno(1)
    compiler.addVariable(id, lineno)


def p_declarations_last_array(p):
    '''declarations	: ID PAREN_OPEN NUMBER COLON NUMBER PAREN_CLOSE'''
    id, begin, end, lineno = p[1], p[3], p[5], p.lineno(1)
    compiler.addArray(id, begin, end, lineno)


def p_declarations_empty(p):
    '''declarations : '''


def p_commands_mult(p):
    '''commands : commands command'''
    p[0] = p[1] + p[2]


def p_commands_one(p):
    '''commands	: command'''
    p[0] = p[1]


def p_command_assign(p):
    '''command : identifier ASSIGN expression SEMICOLON'''
    identifier, expression, lineno = p[1], p[3], p.lineno(1)
    check.changedIterator(identifier[1], str(lineno))
    p[0] = expression + varAddress(identifier, lineno) + "STORE b a\n"
    compiler.inits[identifier[1]] = True


def p_command_input(p):
    '''command : READ identifier SEMICOLON'''
    identifier, lineno = p[2], p.lineno(1)
    compiler.inits[identifier[1]] = True
    p[0] = varAddress(identifier, lineno) + "GET a\n"


def p_command_output(p):
    '''command : WRITE value SEMICOLON'''
    value, lineno = p[2], p.lineno(1)
    if value[0] == "num":
        compiler.addVariable(value, lineno)
        p[0] = loadVar(value, "b", lineno) + genVariable(compiler.variables[value], "a") + "STORE b a\n" + "PUT a\n"
        compiler.deleteVariable(value)
    else:
        check.variableInit(value[1], str(lineno))
        p[0] = varAddress(value, lineno) + "PUT a\n"


def p_expression_plus(p):
    '''expression : value PLUS value'''
    value1, value2, lineno = p[1], p[3], p.lineno(1)
    p[0] = add(value1, value2, lineno)


def p_expression_minus(p):
    '''expression : value MINUS value'''
    value1, value2, lineno = p[1], p[3], p.lineno(1)
    p[0] = sub(value1, value2, lineno)


def p_expression_mult(p):
    '''expression : value MULT value'''
    value1, value2, lineno = p[1], p[3], p.lineno(1)
    p[0] = multiply(value1, value2, lineno)


def p_expression_div(p):
    '''expression : value DIV value'''
    value1, value2, lineno = p[1], p[3], p.lineno(1)
    p[0] = divide(value1, value2, lineno)


def p_expression_mod(p):
    '''expression : value MOD value'''
    value1, value2, lineno = p[1], p[3], p.lineno(1)
    p[0] = modulo(value1, value2, lineno)


def p_iterator(p):
    '''iterator	: ID'''
    id, lineno = p[1], p.lineno(1)
    p[0] = id
    compiler.addVariable(id, lineno)
    compiler.inits[id] = True
    compiler.iterators[id] = True


def p_command_for_to(p):
    '''command : FOR iterator FROM value TO value DO commands ENDFOR'''
    iterator, begin, end, code, lineno = p[2], p[4], p[6], p[8], p.lineno(1)
    check.loopsError(begin[1], end[1], iterator, lineno)
    p[0] = forLoop(iterator, begin, end, code, lineno)
    compiler.deleteVariable(iterator)


def p_command_for_downto(p):
    '''command : FOR iterator FROM value DOWNTO value DO commands ENDFOR'''
    iterator, begin, end, code, lineno = p[2], p[4], p[6], p[8], p.lineno(1)
    check.loopsError(begin[1], end[1], iterator, lineno)
    p[0] = forDecLoop(iterator, begin, end, code, lineno)
    compiler.deleteVariable(iterator)


def p_command_while(p):
    '''command : WHILE condition DO commands ENDWHILE'''
    condition, code, lineno = p[2], p[4], p.lineno(1)
    p[0] = whileLoop(condition, code)


def p_command_if(p):
    '''command : IF condition THEN commands ENDIF'''
    condition, ifCommand, lineno = p[2], p[4], p.lineno(1)
    p[0] = condition[0] + ifCommand + condition[1]


def p_command_if_else(p):
    '''command : IF condition THEN commands ELSE commands ENDIF'''
    condition, ifCommand, elseCommand, lineno = p[2], p[4], p[6], p.lineno(1)
    labels, jumps = addJumpPoints(1)
    p[0] = condition[0] + \
           ifCommand + \
           "JUMP " + jumps[0] + "\n" + \
           condition[1] + \
           elseCommand + \
           "" + labels[0]


def p_condition_equals(p):
    '''condition : value EQUALS value'''
    value1, value2, lineno = p[1], p[3], str(p.lineno(1))
    p[0] = equal(value1, value2, lineno)


def p_condition_repeat_equal(p):
    '''command : REPEAT commands UNTIL value EQUALS value SEMICOLON'''
    code, value1, value2, lineno = p[2], p[4], p[6], str(p.lineno(1))
    condition = notEqual(value1, value2, lineno)
    labels, jumps = addJumpPoints(1)
    p[0] = "" + labels[0] + code + condition[0] + "JUMP " + jumps[0] + "\n" + condition[1]


def p_condition_repeat_nequal(p):
    '''command : REPEAT commands UNTIL value NEQUALS value SEMICOLON'''
    code, value1, value2, lineno = p[2], p[4], p[6], str(p.lineno(1))
    condition = equal(value1, value2, lineno)
    labels, jumps = addJumpPoints(1)
    p[0] = "" + labels[0] + code + condition[0] + "JUMP " + jumps[0] + "\n" + condition[1]


def p_condition_nequals(p):
    '''condition : value NEQUALS value'''
    value1, value2, lineno = p[1], p[3], str(p.lineno(1))
    p[0] = notEqual(value1, value2, lineno)


def p_condition_repeat_less(p):
    '''command : REPEAT commands UNTIL value LESS value SEMICOLON'''
    code, value1, value2, lineno = p[2], p[4], p[6], str(p.lineno(1))
    condition = greaterOrEqual(value1, value2, lineno)
    labels, jumps = addJumpPoints(1)
    p[0] = "" + labels[0] + code + condition[0] + "JUMP " + jumps[0] + "\n" + condition[1]


def p_condition_less(p):
    '''condition : value LESS value'''
    value1, value2, lineno = p[1], p[3], str(p.lineno(1))
    p[0] = less(value1, value2, lineno)


def p_condition_repeat_greater(p):
    '''command : REPEAT commands UNTIL value GREATER value SEMICOLON'''
    code, value1, value2, lineno = p[2], p[4], p[6], str(p.lineno(1))
    condition = lessOrEqual(value1, value2, lineno)
    labels, jumps = addJumpPoints(1)
    p[0] = "" + labels[0] + code + condition[0] + "JUMP " + jumps[0] + "\n" + condition[1]


def p_condition_greater(p):
    '''condition : value GREATER value'''
    value1, value2, lineno = p[1], p[3], str(p.lineno(1))
    p[0] = greater(value1, value2, lineno)


def p_condition_repeat_lesseq(p):
    '''command : REPEAT commands UNTIL value LESSEQ value SEMICOLON'''
    code, value1, value2, lineno = p[2], p[4], p[6], str(p.lineno(1))
    condition = greater(value1, value2, lineno)
    labels, jumps = addJumpPoints(1)
    p[0] = "" + labels[0] + code + condition[0] + "JUMP " + jumps[0] + "\n" + condition[1]


def p_condition_lesseq(p):
    '''condition : value LESSEQ value'''
    value1, value2, lineno = p[1], p[3], str(p.lineno(1))
    p[0] = lessOrEqual(value1, value2, lineno)


def p_condition_repeat_greatereq(p):
    '''command : REPEAT commands UNTIL value GREATEREQ value SEMICOLON'''
    code, value1, value2, lineno = p[2], p[4], p[6], str(p.lineno(1))
    condition = less(value1, value2, lineno)
    labels, jumps = addJumpPoints(1)
    p[0] = "" + labels[0] + code + condition[0] + "JUMP " + jumps[0] + "\n" + condition[1]


def p_condition_greatereq(p):
    '''condition : value GREATEREQ value'''
    value1, value2, lineno = p[1], p[3], str(p.lineno(1))
    p[0] = greaterOrEqual(value1, value2, lineno)


def genVariable(value, register):
    output = ""

    while value != 0:
        if value % 2 != 0:
            output = "INC " + register + "\n" + output
            value = value - 1
        else:
            output = "SHL " + register + "\n" + output
            value = value // 2

    output = "RESET " + register + "\n" + output
    return output


def varAddress(value, lineno):
    lineno = str(lineno)
    if value[0] == "id":
        check.variableAddress(value[1], lineno)
        return genVariable(compiler.variables[value[1]], "a")
    elif value[0] == "tab":
        check.arrayAddress(value[1], lineno)
        index, begin, _ = compiler.arrays[value[1]]
        return loadVar(value[2], "a", lineno) + \
               genVariable(begin, "c") + \
               "SUB a c" + "\n" + \
               genVariable(index, "c") + \
               "ADD a c" + "\n"


def loadVar(value, register, lineno):
    lineno = str(lineno)
    if value[0] == "num":
        return genVariable(value[1], register)
    if value[0] == "id":
        check.variableInit(value[1], lineno)
    return varAddress(value, lineno) + "LOAD " + register + " a" + "\n"


def add(value1, value2, lineno):
    return loadVar(value1, "b", lineno) + loadVar(value2, "c", lineno) + "ADD b c\n"


def sub(value1, value2, lineno):
    return loadVar(value1, "b", lineno) + loadVar(value2, "c", lineno) + "SUB b c\n"


def multiply(value1, value2, lineno):
    return loadVar(value1, "b", lineno) + \
           loadVar(value2, "c", lineno) + \
           "RESET d\n" + \
           "JZERO c 9\n" + \
           "JODD c 4\n" + \
           "SHL b\n" +\
           "SHR c\n" + \
           "JUMP -4\n" + \
           "ADD d b\n" + \
           "SHL b\n" + \
           "SHR c\n" + \
           "JUMP -8\n" + \
           "RESET b\n" + \
           "ADD b d\n"


def divide(value1, value2, lineno):
    return loadVar(value1, "b", lineno) + \
           loadVar(value2, "c", lineno) + \
           "JZERO c 24\n" + \
           "RESET d\n" + \
           "INC d\n" + \
           "RESET a\n" + \
           "ADD a b\n" + \
           "SUB a c\n" + \
           "JZERO a 4\n" + \
           "SHL c\n" + \
           "SHL d\n" + \
           "JUMP -6\n" + \
           "RESET e\n" + \
           "ADD e b\n" + \
           "RESET b\n" + \
           "RESET a\n" + \
           "ADD a c\n" + \
           "SUB a e\n" + \
           "JZERO a 2\n" + \
           "JUMP 3\n" + \
           "SUB e c\n" + \
           "ADD b d\n" + \
           "SHR c\n" + \
           "SHR d\n" + \
           "JZERO d 3\n" + \
           "JUMP -10\n" + \
           "RESET b\n"


def modulo(value1, value2, lineno):
        return loadVar(value1, "b", lineno) + \
           loadVar(value2, "c", lineno) + \
           "JZERO c 24\n" + \
           "RESET d\n" + \
           "INC d\n" + \
           "RESET a\n" \
           "ADD a b\n" + \
           "SUB a c\n" + \
           "JZERO a 4\n" + \
           "SHL c\n" + \
           "SHL d\n" + \
           "JUMP -6\n" + \
           "RESET e\n" \
           "ADD e b\n" + \
           "RESET b\n" + \
           "RESET a\n" \
           "ADD a c\n" + \
           "SUB a e\n" + \
           "JZERO a 2\n" + \
           "JUMP 3\n" + \
           "SUB e c\n" + \
           "ADD b d\n" + \
           "SHR c\n" + \
           "SHR d\n" + \
           "JZERO d 3\n" + \
           "JUMP -10\n" + \
           "RESET b\n" + \
            loadVar(value2, "c", lineno) + \
            "JZERO c 3\n" +\
            "RESET b\n" +\
            "ADD b e\n"


def equal(value1, value2, lineno):
    to, jump = addJumpPoints(2)
    return loadVar(value1, "b", lineno) + \
           loadVar(value2, "c", lineno) + \
           "RESET d\n" + \
           "ADD d b\n" + \
           "SUB d c\n" + \
           "JZERO d 2\n" + \
           "JUMP " + jump[1] + "\n" +\
           "RESET d\n" + \
           "ADD d c\n" + \
           "SUB d b\n" + \
           "JZERO d 2\n" + \
           "JUMP " + jump[1] + "\n" + \
           to[0], to[1]


def notEqual(value1, value2, lineno):
    to, jump = addJumpPoints(2)
    return loadVar(value1, "b", lineno) + \
           loadVar(value2, "c", lineno) + \
           "RESET d\n" + \
           "ADD d b\n" + \
           "SUB d c\n" + \
           "JZERO d 2\n" +\
           "JUMP " + jump[0] + "\n"\
           "RESET d\n" + \
           "ADD d c\n" + \
           "SUB d b\n" + \
           "JZERO d " + jump[1] + "\n" + \
           to[0], to[1]


def less(value1, value2, lineno):
    to, jump = addJumpPoints(1)
    return loadVar(value1, "b", lineno) + \
           loadVar(value2, "c", lineno) + \
           "RESET d\n" + \
           "ADD d c\n" + \
           "SUB d b\n" + \
           "JZERO d " + jump[0] + "\n" + \
           "", to[0]


def greater(value1, value2, lineno):
    to, jump = addJumpPoints(1)
    return loadVar(value2, "b", lineno) + \
           loadVar(value1, "c", lineno) + \
           "RESET d\n" + \
           "ADD d c\n" + \
           "SUB d b\n" + \
           "JZERO d " + jump[0] + "\n" + \
           "", to[0]


def lessOrEqual(value1, value2, lineno):
    to, jump = addJumpPoints(2)
    return loadVar(value2, "b", lineno) + \
           loadVar(value1, "c", lineno) + \
           "RESET d\n" + \
           "ADD d c\n" + \
           "SUB d b\n" + \
           "JZERO d " + jump[0] + "\n" + \
           "JUMP " + jump[1] + "\n" + \
           "" + to[0], to[1] + ""


def greaterOrEqual(value1, value2, lineno):
    to, jump = addJumpPoints(2)
    return loadVar(value1, "b", lineno) + \
           loadVar(value2, "c", lineno) + \
           "RESET d\n" + \
           "ADD d c\n" + \
           "SUB d b\n" + \
           "JZERO d " + jump[0] + "\n" + \
           "JUMP " + jump[1] + "\n" + \
           to[0], to[1]


def forLoop(iterator, begin, end, code, lineno):
    to, jump = addJumpPoints(3)
    temp = compiler.addVariableTempo()
    valTemp = ("id", temp)
    it = ("id", iterator)

    return loadVar(end, "e", lineno) + \
           varAddress(valTemp, lineno) + \
           "STORE e a\n" + \
           loadVar(begin, "f", lineno) + \
           varAddress(it, lineno) + \
           "STORE f a\n" + \
           to[2] + \
           loadVar(valTemp, "e", lineno) + \
           loadVar(it, "f", lineno) + \
           "SUB f e\n" + \
           "JZERO f " + jump[0] + "\n" + \
           "JUMP " + jump[1] + "\n" + \
           to[0] + code + \
           loadVar(it, "f", lineno) + \
           "INC f\n" + \
           varAddress(it, lineno) + \
           "STORE f a\n" + \
           "JUMP " + jump[2] + "\n" + to[1]


def forDecLoop(iterator, begin, end, code, lineno):
    to, jump = addJumpPoints(3)
    temp = compiler.addVariableTempo()
    valTemp = ("id", temp)
    it = ("id", iterator)
    return loadVar(end, "e", lineno) + \
           varAddress(valTemp, lineno) + \
           "STORE e a\n" + \
           loadVar(begin, "f", lineno) + \
           varAddress(it, lineno) + \
           "STORE f a\n" + to[2] +\
           loadVar(valTemp, "e", lineno) + \
           loadVar(it, "f", lineno) + \
           "SUB e f\n" + \
           "JZERO e " + jump[0] + "\n" + \
           "JUMP " + jump[1] + "\n" + \
           to[0] + code + \
           loadVar(it, "f", lineno) + \
           varAddress(it, lineno) + \
           "JZERO f " + jump[1] + "\n" + \
           "DEC f\n" + \
           "STORE f a\n" + \
           "JUMP " + jump[2] + "\n" + to[1]


def whileLoop(condition, code):
    labels, jumps = addJumpPoints(1)
    return "" + labels[0] + \
           condition[0] + \
           code + \
           "JUMP " + jumps[0] + "\n" + \
           condition[1] + ""


parser = yacc.yacc()
