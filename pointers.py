import re

jumpPoints = []
clearedLines = []


def addJumpPoints(count):
    jump = []
    to = []
    for i in range(0, count):
        jumpPoints.append(-1)
        num = str(len(jumpPoints) - 1)
        jump.append("@JUMP" + num + "@")
        to.append("@TO" + num + "@")
    return to, jump


def clearLines(program):
    lineCounter = 0
    for line in program.split("\n"):
        match = re.findall("@TO[0-9]+@", line)
        if match != []:
            for myMatch in match:
                id = int(myMatch[3:-1])
                jumpPoints[id] = lineCounter
                line = re.sub("@TO[0-9]+@", "", line)
        clearedLines.append(line)
        lineCounter += 1
    return addJumps()


def addJumps():
    jumperCounter = 0
    result = ""
    for line in clearedLines:
        match = re.search("@JUMP[0-9]+@", line)
        if match is not None:
            id = int(match.group()[5:-1])
            jumpTo = jumpPoints[id] - jumperCounter
            line = re.sub("@JUMP[0-9]+@", str(jumpTo), line)
        result += line + "\n"
        jumperCounter += 1
    return result
