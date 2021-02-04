class CompilerStorage:
    inits = {}
    arrays = {}
    variables = {}
    iterators = {}
    memory = 1

    def addArray(self, id, begin, end, lineno):
        lineno = str(lineno)
        if id in self.arrays:
            raise Exception('Podwójna deklaracja tablicy ' + id + " - linia " + lineno)
        if begin > end:
            raise Exception('Błędny zakres tablicy ' + id + " - linia " + lineno)
        position = self.memory + 1
        self.arrays[id] = (position, begin, end)
        self.memory += (end - begin + 1)

    def addVariable(self, id, lineno):
        if id in self.variables:
            raise Exception('Podwójna deklaracja zmiennej ' + id + " - linia " + str(lineno))
        self.memory += 1
        self.variables[id] = self.memory

    def addVariableTempo(self):
        tempo = "$T" + str(self.memory)
        self.addVariable(tempo, None)
        self.inits[tempo] = True
        return tempo

    def deleteVariable(self, id):
        self.variables.pop(id)
