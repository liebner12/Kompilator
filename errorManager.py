class ErrorManager:
    inits = {}
    arrays = {}
    variables = {}
    iterators = {}

    def __init__(self, compiler):
        self.inits = compiler.inits
        self.arrays = compiler.arrays
        self.variables = compiler.variables
        self.iterators = compiler.iterators

    def variableInit(self, id, lineno):
        if id not in self.inits:
            raise Exception("Zmienna " + id + " jest niezainicjonowana" + " - linia " + lineno)

    def arrayAddress(self, id, lineno):
        if id not in self.arrays:
            if id in self.variables:
                raise Exception("Błędne użycie zmiennej " + id + " - linia " + lineno)
            else:
                raise Exception("Bład zadeklarowania tablicy " + id + " - linia " + lineno)

    def variableAddress(self, id, lineno):
        if id not in self.variables:
            if id in self.arrays:
                raise Exception("Błędne użycie tablicy " + id + " - linia " + lineno)
            else:
                raise Exception("Bład zadeklarowania zmiennej " + id + " - linia " + lineno)

    def changedIterator(self, id, lineno):
        if id in self.iterators:
            raise Exception("Próba zmiany iteratora " + id + " - linia " + lineno)

    def loopsError(self, begin, end, iterator, lineno):
        if end == iterator:
            raise Exception("Zmienna " + end + " jest niezainicjonowana o tej samej nazwie co iterator w pętli" + " - linia " + str(lineno))
        if begin == iterator:
            raise Exception("Zmienna " + begin + " jest niezainicjonowana o tej samej nazwie co iterator w pętli" + " - linia " + str(lineno))
