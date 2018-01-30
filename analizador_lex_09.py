alfabeto = { 'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 
			 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 
			 'k': 10,  'l': 11,  'm': 12,  'n': 13,  'o': 14, 
			 'p': 15,  'q': 16,  'r': 17,  's': 18,  't': 19, 
			 'u': 20,  'v': 21,  'w': 22,  'x': 23,  'y': 24, 
			 'z': 25 }
#print(alfabeto.items())

palabras_Reservadas = {
	'T001' : 'break',
	'T002' : 'case',
	'T003' : 'catch',
	'T004' : 'continue',
	'T005' : 'debugger',
	'T006' : 'default',
	'T007' : 'delete',
	'T008' : 'do',
	'T009' : 'else',
	'T010' : 'finally',
	'T011' : 'for',
	'T012' : 'function',
	'T013' : 'if',
	'T014' : 'in',
	'T015' : 'instancesof',
	'T016' : 'new',
	'T017' : 'return',
	'T018' : 'switch',
	'T019' : 'this',
	'T020' : 'throw',
	'T021' : 'try',
	'T022' : 'typeof',
	'T023' : 'var',
	'T024' : 'void',
	'T025' : 'while',
	'T026' : 'with',
	'T027': 'class',
	'T028': 'const',
	'T029': 'enum',
	'T030': 'export',
	'T031': 'extends',
	'T032': 'import',
	'T033': 'super',
	'T034': 'implements',
	'T035': 'interface',
	'T036': 'let',
	'T037': 'package',
	'T038': 'private',
	'T039': 'protected',
	'T040': 'public',
	'T041': 'static',
	'T042': 'yield',
	'T040': 'null',
	'T041': 'true',
	'T042': 'false'
}

terminal_words = []

def NumMatrixRows(FileName): #cuenta el numero de filas de una matriz en un archivo
	rows = 1
	with open(FileName, 'r') as f:
		while True:
			c = f.read(1)
			if not c:
				#print("End of file")
				break
			if ord(c) == 10:
				rows += 1
	return rows

def CreateMatrixT(FileName, rows, cols):#mete una matriz de Transicion a un arreglo bidimensional apartir de un archivo con estados separados por TAB

	matrixRW = [['' for x in range(cols)] for y in range(rows)] #matriz de palabras reservadas => matrixRW[ROWS][26]
	#print(matrixRW)

	i = 0 #filas de la matriz
	j = 0 #columnas de la matriz

	with open(FileName, 'r') as m:
		while True:

			mc = m.read(1) #lee un caracter

			if not mc:
				#print("End of file")
				break

			if ord(mc) == 9:
				#print("TAB")
				j += 1

			if ord(mc) == 10:
				#print("NUEVA LINEA")
				i += 1
				j = 0

			if ord(mc) != 9 and ord(mc) != 10: 
				#print(mc)
				matrixRW[i][j] = matrixRW[i][j] + mc

	return matrixRW

def CreateListScript(ScriptFileName): #crea una lista bidimensional con todas las letras del script que vamos a identificar
	listaA = []
	listaB = []
	i = 0
	with open(ScriptFileName, 'r') as f:

		while True:
			c = f.read(1)
			if not c:
				listaB.append(listaA)
				#print("End of file")
				break

			if ord(c) != 32:
				if ord(c) != 10:
					if ord(c) != 9:
						listaA.append(c)
						#print(c)

			if ord(c) == 32 or ord(c) == 10 or ord(c) == 9: #si es ESPACIO, NUEVA LINEA, TAB
				if len(listaA) != 0:
					listaB.append(listaA)
					#print(listaA)
					listaA = []

	return listaB

def LenListOfLists(ListOfLists):
	return sum(1 for x in ListOfLists if isinstance(x, list))

def IdentifyScript(TransitionMatrix, ScriptList, Alphabet): #clasifica el script de acuerdo al automata y al alfabeto definido

	len_matriz_script = LenListOfLists(ScriptList) -1
	i, j = 0, 0
	actual_state = 0 #estado actual en la matriz de transicion
	next_state = 0 #estado siguente en la matriz de transicion

	#print(len_matriz_script)

	while len_matriz_script != 0: #CAMBIAR A len_matriz_script != 0 
		
		if j >= len(ScriptList[i]):
			j = 0
			i += 1

		if i > len_matriz_script:
			break

		try: #cuando llega al ultimo indice de la lista esta puede no tener nada en caso de que el usuario haya dejado espacios/saltos/tabs, esto nos indica que ya no hay palabras
			char_script = ScriptList[i][j]
			#print(char_script)
		except IndexError: #estado terminal
			break


		char_script_alf = Alphabet[char_script] #numero que le corresponde al caracter, leido, en el alfabeto

		next_state = TransitionMatrix[actual_state][char_script_alf]

		# Recorre next state para saber si en ese estado hay simbolos terminales y/o siguientes estados
		#EJEM => next_state = 'T001-9' #simbolo terminal-siguente_estado
		str_estado = ['', '']
		flag = 0

		for x in range(len(next_state)): #recorre todo el string del estado

			if next_state[x] == '-': # si hay un '-' se detecta que tambien hay estado siguente en ese estado
				flag = 1
				x = x + 1
			else:
				if flag == 0: #no se ha detectado '-'
					str_estado[0] = str_estado[0] + next_state[x]
				else:
					str_estado[1] = str_estado[1] + next_state[x]

		#PC -> str_estado['T001', '9']
		#print(str_estado)

		if str_estado[0][0] == 'T' and len(str_estado[1]) != 0: #si tiene simbolo terminal y estado siguente
			try: #checaamos que haya siguente letra sino entonces ya es estado teminal
				if ScriptList[i][j+1]:
					actual_state = int(str_estado[1])
			except IndexError: #estado terminal
				terminal_words.append(str_estado[0])
				actual_state = 0

			#print(int(str_estado[1]))

		if str_estado[0][0] == 'T' and len(str_estado[1]) == 0: #si solo tiene estado terminal
			terminal_words.append(str_estado[0])
			actual_state = 0

		if str_estado[0][0] != 'T': #si solo tiene estado siguente
			actual_state = int(str_estado[0])

		j += 1
		

	return terminal_words


ROWS = NumMatrixRows('matriz.txt') #filas de nuestra matriz
COLS = 26 #cantidad de simbolos en nuestro alfabeto

matriz_transicion = CreateMatrixT('matriz.txt', ROWS, COLS)

matriz_script = CreateListScript('Script.txt')

Lista_Symbolos_Iden = IdentifyScript(matriz_transicion, matriz_script, alfabeto)

#print(matriz_transicion)
#print(matriz_script)
print (Lista_Symbolos_Iden)


for x in range(0, len(Lista_Symbolos_Iden)):
	print(palabras_Reservadas[Lista_Symbolos_Iden[x]] + '	Palabras Reservadas')
