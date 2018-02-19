'''
This module represents how to create an automata 
    to validate a set of production rules
    outputing a file with thre recognized identifiers
'''
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

    def addNextTransition(self, l, de,a, ident = None):
        '''
        adds a transition from the elements in l to state [i+1]
        ident = <string> then adds transition from elements l to
        [ident,i+1]
        '''
        a = a + 1
        for el in l:
            if len(self.qt[de][ord(el)-1]) != 0 and not ident:
                return False , self.qt[de][ord(el)-1]
            if ident:
                self.qt[de][ord(el)-1].add((ident,a))
            else:
                self.qt[de][ord(el)-1].add(a)
        if len(self.qt)-1 < a:
            self.qt.append([set() for x in range(0, CHARRANGE)])
        return True,0
        

    def addFirstInput(self, val):
        '''
        add an element to the starting transitions list for this DFA
        '''
        if len(val) == 1:
            self.firstInput.add(val) #identifier
        else:
            self.firstInput |=AUTOMATAS[val].firstInput #state

    def addNextShorthandTransition(self, de,a, ident = None):
        #TODO add recognized shorhand symbols and selected transitions 
        pass
    def checarToken(self,path,pos,oldpos=-1, oldedo=-1):
        with open(path) as f:
            f.seek(pos,0)
            edo = 0
            s = ''
            while True:
                oldpos = f.tell()
                oldedo = edo
                c = f.read(1)
                if not c or c.isspace():
                    if self.isFinalState(oldedo):
                        return True,oldpos,s
                    return False,oldpos,s
             
                edo = self.qt[edo][ord(c)-1]
                for camino in edo: #{0,2,3,("id",23)}
                    if isinstance(camino, int ):
                       
                        edo = camino
                        s+=c
                        break
                    else:
                        aut = AUTOMATAS[camino[0]]
                        res = camino[1]
                        intento = aut.checarToken(path,f.tell()-1,oldpos,oldedo)
                        if intento[0]:
                            edo = res
                            f.seek(intento[1],0)
                            s+=intento[2]
                            break
                if not edo or not isinstance(edo, int ):
                    if self.isFinalState(oldedo):
                        return True,oldpos,s
                    return False,oldpos,s
                
        

    def __repr__(self):
        a = ' {} (fi = {}, len_qt ={}, F = {})\n'.format(
            self.__class__.__name__, self.firstInput, len(self.qt), self.F)
        return a

def getAutomata(ident):
    if ident in AUTOMATAS:
        return AUTOMATAS[ident]
    return False

#crea los automatas a usar para el analizador lexico
def createAutomata(ident, expr):
    
    a = 0
    de = 0
    aut = DFA(ident)
    wasNonTerminal = False
    wasOp = False
    shorthand = False
    nextAsChar = False
    ident = None
    s = '' 
    for c in expr:
        if wasNonTerminal:
            if c.isspace():
                    raise RuntimeError('unfinished non terminal ') from ValueError
            if c != '}':
                s+=c
                continue
            print(s)
            nested = getAutomata(s)
            print(nested)
            if nested:
                ident = s
                c ="".join(nested.firstInput)
            else:
                raise RuntimeError('no rule defined') from ValueError
        if c.isspace():
            continue
        if shorthand:
            aut.addNextShorthandTransition(c,de,a)
        if c == '{'and  not nextAsChar:
            if(wasNonTerminal):
                 raise RuntimeError('nested non-terminals ') from ValueError
            wasNonTerminal = True
            continue
        if c == '\\'and not nextAsChar:
            nextAsChar = True
            continue
        if c == '$' and not nextAsChar:
            shorthand = True
            continue
        if c == '+' and not nextAsChar:
            # past was final state
            if wasOp and de==a:
                 raise RuntimeError('duplicate assigment') from ValueError
            if wasOp:
                raise RuntimeError('two add ops together') from ValueError
            
            aut.addFinalState(a)
            de = 0
            wasOp = True
            continue
        added = aut.addNextTransition(c,de,a,ident)
        if not added[0]:
            for el in added[1]:
             de= el
            continue
        if de == 0 and not ident:
            aut.addFirstInput(c)
        elif de==0:
             aut.addFirstInput(ident)
        a += 1
        de = a
        wasNonTerminal = False
        wasOp = False
        shorthand = False
        nextAsChar = False
        ident = None
        s = '' 

    if a != 0:
        aut.addFinalState(a)
    else:
        raise RuntimeError('no rules defined') from ValueError
    return aut

# agrega los automatas finitos al diccionario lexico
tokenNum = 0
def addAutomata(mid, expr,use):
    global tokenNum 
    aut = createAutomata(mid,expr)
    print("created... ")
    AUTOMATAS[mid] = aut
    if use:
        print("added... \n ",aut)
        for el in aut.firstInput:
            LEXDICT[ord(el)-1][mid] = aut 
            #agrega automata para mid  al dict del analizador lexico
            if mid not in RECTOKENS:
                RECTOKENS[mid] =  tokenNum
                tokenNum+=1


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
    oldfound = False , -1,''
    found = False , -1,''
    size = 0
    oldsize = 0
    oldcurrentKey =''
    with open(INFILE) as f:
        while True:
            oldcurrentKey =''
            oldfound = False , -1,''
            found = False , -1,''
            size = 0
            oldsize = 0
            c = f.read(1)
            if not c:
                print("\nEnd of file\n")
                return
            if c.isspace():
                continue
            autDict = LEXDICT[ord(c)-1]
            for k, v in autDict.items():
                currentKey = k
                #print(k, " ",f.tell()-1, c)
                found = v.checarToken(INFILE,f.tell()-1)
                size = found[1] - f.tell()+1
                
                if found[0] and size > oldsize:
                    oldsize = size
                    oldfound = found
                    oldcurrentKey =currentKey
            if oldfound[0]:
                write2TokenStream(currentKey,oldfound)
                print("Found symbol = ", oldcurrentKey , "val = ", oldfound)
                f.seek(found[1])
                # else:
                #     print("no rule for symbol was found = ")

# read lexical rules
with open(FILENAME) as f:
    while True:
        l = f.readline()
        if not l:
            print("End of file")
            break
        print("Read a line:", l)
        import re
        p = re.compile(r'(?P<use>[\*]?)(?P<id>[A-Za-z0-9]+)::(?P<expr>.+)')
        m = p.match(l)
        use = m.group('use')
        if use:
            print('use ',use)
        mid = m.group('id')
        expr = m.group('expr')
        addAutomata(mid, expr,use)
test()
