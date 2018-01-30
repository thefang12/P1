import collections
filename = "lex.txt"
automatas = [collections.OrderedDict() for x in range(0, 127)]
inFile = "in.txt"

class DFA:

    def __init__(self):
        # q0 = 0
        # Q = len(qt)
        # first input for sorting purposes
        self.fi = []
        self.qt = [[-1 for x in range(0, 127)]]
        self.F = []

    def isFinalState(self, state):
        return state in self.F

    def addFinalState(self, state):
        self.F.append(state)

    def addNextTransition(self, c, i):
        nr = i + 1
        self.qt[i][ord(c)-1] = nr
        if len(self.qt)-1 < nr:
            self.qt.append([-1 for x in range(0, 127)])

    def addFirstInput(self, val, isVar=False):
        if isVar:
            self.fi.append(val)
        else:
            self.fi.append(ord(val)-1)

    def check(self, file, path, pos, debug=False):
        i = 0
        with open(path) as file:
            file.seek(pos, 0)
            while True:
                c = file.read(1)
                if not c or (debug and c == '\n'):
                    print("End of file | state: ", i,
                          "| F ", self.isFinalState(i))
                    break
                print("Read a char:", c)
                code = ord(c)-1
                if self.qt[i][code] != -1:
                    i = self.qt[i][code]
                    continue
                else:
                    return False
        if self.isFinalState(i):
            return True

    def __repr__(self):
        a = ' {} (fi = {}, len_qt ={}, F = {})\n'.format(
            self.__class__.__name__, self.fi, len(self.qt), self.F)
        import numpy as np
        x = np.array(self.qt)
        a += str(x)
        return a


def createAutomata(expr):
    nextAsChar = False
    i = 0
    aut = DFA()
    cpast = ''
    wasOp = False
    for c in expr:
        # TODO add shorthand symbols
        # TODO add expr symbols
            # TODO add check symbol was defined
        if c == '\\'and not nextAsChar:
            nextAsChar is True
            continue
        if c == '+' and not nextAsChar:
            # past was final state
            if(wasOp):
                raise RuntimeError('two operators together') from ValueError
            aut.addFinalState(i)
            i = 0
            wasOp = True
            continue
        aut.addNextTransition(c, i)
        if i == 0:
            aut.addFirstInput(c)
        cpast = c
        nextAsChar = False
        wasOp = False
        i += 1
    if i != 0:
        aut.addFinalState(i)
    else:
        raise RuntimeError('no rule defined') from ValueError
    return aut


def addAutomata(mid, expr):
    aut = createAutomata(expr)
    print(aut)
    print("mid ", mid, " type ", type(mid))
    for el in aut.fi:
        import numbers
        if isinstance(el, numbers.Number):
            automatas[el][mid] = aut

# test rules


def test(debug=False):
    currentKey = ''
    found = False
    with open(inFile) as f:
        while True:
            found = False
            c = f.read(1)
            if not c:
                print("End of file")
                return
            if c != '\n':
                print("Read a char test:", c)
            autDict = automatas[ord(c)-1]
            for k, v in autDict.items():
                currentKey = k
                found = v.check(f, inFile, f.tell()-1, debug)
                if found:
                    print("Found symbol ", currentKey)
                elif not (debug and c == '\n'):
                    print("no rule for symbol was found")

# create lexical rules
with open(filename) as f:
    while True:
        l = f.readline()
        if not l:
            print("End of file")
            break
        print("Read a line:", l)
        import re
        p = re.compile('(?P<id>[A-Za-z0-9]+)::(?P<expr>.+)')
        m = p.match(l)
        mid = m.group('id')
        expr = m.group('expr')
        addAutomata(mid, expr)
test(debug=True)

# print(" ".isspace())
# print("a".isspace())
# print("\t".isspace())
# import re
# p = re.compile('(?P<id>[A-Za-z0-9]+)::(?P<expr>.+)')
# m = p.match("hi::bre::u")
# mid = m.group('id')
# expr = m.group('expr')
# addAutomata(mid, expr)
# lista  = [[x for x in range(0,127)] ]
# lista.append([x*2 for x in range(0,127)])
# a = 'c'
# print(len(lista))
# w = []
# len(w)
