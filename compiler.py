import sys
from commands import parser


def readFile(file):
    with open(file, "r") as file:
        return file.read()


def writeFile(file, program):
    with open(file, "w") as file:
        file.write(program)


def outputHandler():
    inputFile = sys.argv[1]
    outputFile = sys.argv[2]
    file = readFile(inputFile)
    try:
        parsed = parser.parse(file, tracking=True)
    except Exception as e:
        print(e)
        exit()
    writeFile(outputFile, parsed)


outputHandler()
