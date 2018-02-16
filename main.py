"""This module represents how to create an automata 
    to validate a set of production rules
    outputing a file with thre recognized identifiers
"""
import collections
FILENAME = "lex.txt"
AUTOMATAS = {}
CHARRANGE = 127
LEXDICT = [collections.OrderedDict() for x in range(0, CHARRANGE)]
INFILE = "in.txt"
RECTOKENS = {}


class DFA:
    """Represents a deterministic finite automata with functions """
    def __init__(self,ident):
        '''
        Construct am empty DFA with the given ident to parse
        '''
        # q0 = 0
        # Q = len(qt)
        # first input for sorting purposes
        self.ident =ident
        self.firstInput = set()
        self.qt = [[set() for x in range(0, CHARRANGE)]]
        self.F = set()

    def isFinalState(self, state):
        return state in self.F

    def addFinalState(self, state):
        self.F.add(state)

    def addNextTransition(self, l, de,a=None, ident = None):
        '''
        adds a transition from the elements in l to state [i+1]
        ident = <string> then adds transition from elements l to
        [ident,i+1]
        '''
        nr = de + 1
        if a:
            nr = a + 1
        for el in l:
            if len(self.qt[de][ord(el)-1]) != 0 and not ident:
                return False
            if ident:
                self.qt[de][ord(el)-1].add((ident,nr))
            else:
                self.qt[de][ord(el)-1].add(nr)
        if len(self.qt)-1 < nr:
            self.qt.append([set() for x in range(0, CHARRANGE)])
        return True
        

    def addFirstInput(self, val):
        '''
        add an element to the starting transitions list for this DFA
        '''
        if len(val) == 1:
            self.firstInput.add(val) #identifier
        else:
            self.firstInput |=AUTOMATAS[val].fi #state

    def addNextShorthandTransition(self, c,i):
        #TODO add recognized shorhand symbols and selected transitions 
        pass
    def checkNested(self, f):
        i = 0
        pos = -1
        f.seek(f.tell()-1, 0)
        while True:
            c = f.read(1)
            code = ord(c)-1
            if  self.qt[i][code]:
                i = self.qt[i][code]
                if len(i) >1:
                    #TODO add for to iter set
                    pos = AUTOMATAS[i[0]].checkNested(f)
                    if pos > -1:
                        i = i[1]
                        f.seek(pos,0)
                    else:
                        return False #TODO show error
                else:
                    i = i[0]
                if self.isFinalState(i):
                    pos = f.tell()-1
                for path in i:
                    if isinstance(path, str):
                        i = path
                    if self.isFinalState(i):
                        pos = f.tell()-1
                    else:
                        pos = AUTOMATAS[path[0]].checkNested(f)
                        if pos > -1:
                            i = i[1]
                            f.seek(pos,0)
                    else:
                        continue #TODO show error
                continue
            else:
                return pos

    def checkMain(self, f):
        i = 0
        s = ''
        f.seek(f.tell()-1, 0)
        while True:
            c = f.read(1)
            s+=c
            if not c or c.isspace():
                if self.isFinalState(i):
                    return s
            #print("Read a char:", c)
            code = ord(c)-1
            if  self.qt[i][code]:
                i = self.qt[i][code] 
                for path in i:
                    if isinstance(path, str):
                        i = path
                    else:
                        res = AUTOMATAS[path[0]].checkNested(f)
                        if res == -1:
                            i = i[1]
                            f.seek(f.tell()-1,0)
                    else:
                        continue #TODO show error
                continue
            else:
                while True:
                    c = f.read(1)
                    if not c or c.isspace():
                        return False
        

    def __repr__(self):
        a = ' {} (fi = {}, len_qt ={}, F = {})\n'.format(
            self.__class__.__name__, self.firstInput, len(self.qt), self.F)
        import numpy as np
        x = np.array(self.qt)
        a += str(x)
        return a

def getAutomata(ident):
    if ident in AUTOMATAS:
        return AUTOMATAS[ident.ident]
    return False

#crea los automatas a usar para el analizador lexico
def createAutomata(ident, expr):
    
    i = 0
    de = 0
    aut = DFA(ident)
    wasNonTerminal = False
    wasOp = False
    shorthand = False
    nextAsChar = False
    s = '' 
    for c in expr:
        if wasNonTerminal:
            if c.isspace():
                    raise RuntimeError('unfinished non terminal ') from ValueError
            if c != '}':
                s+=c
                continue
            nested = getAutomata(s)
            if nested:
                if wasOp:
                    aut.addNextTransition(nested.fi,0,ident = s)
                    aut.addFirstInput(nested.fi)
                else:
                    aut.addNextTransition(nested.fi,i,ident = s)
                nextAsChar = False
                wasOp = False
                i += 1
                continue
            else:
                raise RuntimeError('no rule defined') from ValueError
        if c.isspace():
            continue
        if shorthand:
            aut.addNextShorthandTransition(c,i)
        if c == '{'and  not nextAsChar:
            if(wasNonTerminal):
                 raise RuntimeError('nested non-terminals ') from ValueError
            wasNonTerminal = True
            # TODO add check symbol was defined
        if c == '\\'and not nextAsChar:
            nextAsChar = True
            continue
        if c == '$' and not nextAsChar:
            shorthand = True
            continue
        if c == '+' and not nextAsChar:
            # past was final state
            if(wasOp):
                raise RuntimeError('two add ops together') from ValueError
            aut.addFinalState(i)
            wasOp = True
            continue
        if wasOp:
           print("next tran",i," ",c)
           if not aut.addNextTransition(c,de,i):
               de+=1
               continue
           aut.addFirstInput(c)
        else:
            print("next tran",i," ",c)
            if not aut.addNextTransition(c, i):
                continue
        if i == 0:
            aut.addFirstInput(c)
      
        nextAsChar = False
        wasOp = False
        i += 1
    if i != 0:
        aut.addFinalState(i)
    else:
        raise RuntimeError('no rules defined') from ValueError
    return aut

# agrega los automatas finitos al diccionario lexico
tokenNum = 0
def addAutomata(mid, expr):
    global tokenNum 
    aut = createAutomata(mid,expr)
    AUTOMATAS[mid] = aut
    for el in aut.firstInput:
        LEXDICT[ord(el)-1][mid] = aut 
        #agrega automata para mid  al dict del analizador lexico
        if mid not in RECTOKENS:
            RECTOKENS[mid] =  tokenNum
            tokenNum+=1


##TODO analizador sintactico 
### el archivo de reglas sintacticas NO debe tener simbolos terminales
### el archivo de reglas sintactias solo debe tener identificadores que coincidan con los del archivo de reglas lexicas con la siguiente estructura 
####A:([{token lexico}]|[{{simbolo no terminal sintactico}}])+
#### el token stream tendra la siguiente estrucutra
# codigo(|valor)?
# ejemplo:
# 0
# 1
# 2
# 3|hola
# 4
# 5|adios
# 3|tre
# 2
# 3
# 4
#TODO crear automata sintactico
## lee el arhivo de reglas sintacticas
##regla n
###divide regla en id y expr
###se crea el automata a partir de expr
#####leer expr letra por letra 
######reconocer tokens como simbolos  terminales
#######estos empiezan con { y terminan con }
########una vez reconocido el interior se busca en el dict de tokens
######### si es encontrado se usa el valor definido como input en el automata
########## se construye usando la misma sintaxis qu el automa lexico
###########al final termina un dictionario sintactico tal como el lexico

##TODO parsear token stream
##leer letra  por letra 
##se divide en num y val
##se toma el num y se usa de input en el automata sintactico
## se valida que el stream fue  valido en el automata sintactico




def write2TokenStream(ident, val):
    pass
    ##TODO put token in the form #|val? from token dict
    # ejemplo:
    # 0
    # 1
    # 2
    # 3|hola
    # 4
    # 5|adios
    # 3|tre
    # 2
    # 3
    # 4



# test rules
# prueba el archivo usando el diccionario lexico previamente creado
def test():
    currentKey = ''
    found = False
    with open(INFILE) as f:
        while True:
            found = False
            c = f.read(1)
            if not c:
                print("\nEnd of file\n")
                return
            if c.isspace():
                continue
            autDict = LEXDICT[ord(c)-1]
            for k, v in autDict.items():
                currentKey = k
                found = v.checkMain(f)
                if found:
                    write2TokenStream(currentKey,found)
                    print("Found symbol = ", currentKey , "val = ", found)
                else:
                    print("no rule for symbol was found")

# read lexical rules
with open(FILENAME) as f:
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
test()

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
