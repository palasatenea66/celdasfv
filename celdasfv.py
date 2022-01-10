import numpy as np                    #importo las librerías que necesitaré
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# defino las funciones que usaré

def leerArchivoEntrada(nombreArchivo):     
    """Lee archivo de entrada por líneas y lo escribe en un archivo a designar.
    Los parámetros a entrar son el nombre del archivo a leer y el nombre con que 
    se desea designar la entrada."""
    nombreEntrada = []
    try:
        fileIn = open(nombreArchivo, "r")
    except FileNotFoundError:
        print("Archivo no encontrado:", nombreArchivo)
        exit()
    nombreEntrada = fileIn.readlines()
    fileIn.close()
    return nombreEntrada


def limpioDatosCreoLista(entrada):   
    """Saco saltos de línea (\n) y también espacios (si hubiere) de los datos de entrada 
    y armo las listas de datos, tomando como separador entre datos los \t (tabuladores).
    El parámetro a ingresar es el nombre del archivo de entrada. """
    nombreLista = []
    for linea in entrada:
        lineaSinEnter = linea.rstrip("\n")
        lineaSinEspacio = lineaSinEnter.strip()
        lineaSinTab = lineaSinEspacio.split("\t")
        nombreLista.append(lineaSinTab)
    return nombreLista


def pasoAfloat(listaDeNumerosComoString):
    """Toma una lista de números que son String y entrega una lista de números Float.
    El argumento es el nombre de la lista que queremos pasar a float."""
    listaLimpia = []
    for linea in listaDeNumerosComoString:     
        listaDeNumeros = []
        for numeroComoString in linea:
            listaDeNumeros.append(float(numeroComoString))
        listaLimpia.append(listaDeNumeros)
    return listaLimpia


def calculoFactoresDeCorreccion(listaTempRad):
    """Calculo los factores de corrección para todas las celdas, cada línea de la lista corresponde a una celda.
    El argumento de entrada es la lista con los datos de temperatura y radiación."""  
    factores = []
    for i in range(len(listaTempRad)):
        tAmb = listaTempRad[i][1]
        rad = listaTempRad[i][2]
        tCelda = tAmb + 0.03*rad
        factV = 2.3*36*(tCelda - 25)/1000
        factores.append(factV)
        factI = 1000/float(rad) 
        factores.append(factI) 
    return factores    


def corregirVoltajeCorriente(datos, factoresCorreccion):
    """Corrije los datos de voltaje y corriente por sus factores correspondientes y los almacena en la misma lista.
    El argumento de entrada es la lista a modificar."""
    for i in range(len(datos)):
        for j in range(len(datos[0])):
            if (j%2 == 0):   # estas son las columnas pares
                datos[i][j] = datos[i][j] + factoresCorreccion[i][j]    #voltaje corregido
            else:            # estas son las columnas impares
                datos[i][j] = datos[i][j]*factoresCorreccion[i][j]     #corriente corregida 
    return datos


def calcularPotencia(listaDatosCorregidos):
    """Calculo la potencia para todas las celdas para cada par de datos de voltaje/corriente.
    Los valores calculados se guardan en una nueva lista.
    El argumento de entrada es el archivo con los valores V-I ya corregidos."""
    potenciaTodasLasCeldas = []
    for j in range(len(listaDatosCorregidos)):
        potencia = []
        for i in range(0, len(listaDatosCorregidos[j]), 2):
            potenciaCelda = listaDatosCorregidos[j][i]*listaDatosCorregidos[j][i+1]     # potencia = V*I
            potencia.append(potenciaCelda)
        potenciaTodasLasCeldas.append(potencia)
    return potenciaTodasLasCeldas


def traspuesta(matriz):
    """Traspone una matriz (que Python interpreta como una lista de listas) de n filas x m columnas.
    El argumento de entrada es la lista de listas que define a la matriz."""
    n = len(matriz)      #número de filas
    m = len(matriz[0])   # número de columnas
    tras = []
    for i in range(m):
        tras.append([])
        for j in range(n):
            tras[i].append(matriz[j][i]) 
    return tras


def buscaMaximoXlinea(lista):
    """Busca el máximo de una lista y lo escribe en otra lista.
    El argumento de entrada es la lista a analizar."""
    maximos = [round(max(linea),1) for linea in lista]
    return maximos


def datosFloatComoString(listaFloat):
    """Convierte una lista de elementos float a una lista de elementos string.
    El argumento de entrada es la lista con los datos float. """
    floatToString = [str(elemento) for elemento in listaFloat]
    return floatToString


def escribeOutListaDeListas(listaOut, nombreOut):
    """Escribe el contenido de una LISTA DE LISTAS en un archivo de salida, línea x línea.
    Los argumentos de entrada son la lista a transcribir y el nombre que se dará al archivo de salida."""
    with open(nombreOut,"w") as file:
        file.write("\n".join([" ; ".join(sublista) for sublista in listaOut]))


def func(x, a, b, c):
    """Defino la función que propongo para ajustar los datos medidos de I vs V.
    ´x´ es la variable independiente, mientras que a, b y c son los coeficientes que 
    se deben ajustar. """
    return a + b*np.exp(c*x)


def fnPotencia(x, a, b, c, d):
    """Idem con la ¨func¨ anterior pero para ajustar la curva de potencia. 
    Como P = I*V e I = f(V) = a + b*(exp(c*V)), será P = f(V) = a + b*V + c*V*exp(d*V)."""
    return a + b*x + c*x*np.exp(d*x)



#  EMPEZAMOS!!!!!
print("\n", "\n", "\n")
print("BIENVENID@S! Este programa ajusta parámetros para celdas FV", "\n", "\n", "\n")
print("*********IMPORTANTE***********", "\n", "\n", "\n")
print("Por favor, tenga en cuenta que los archivos de datos deben tener las líneas")
print("separadas por ENTER y los valores separados por TAB", "\n", "\n", "\n")
print("Ahora, ingrese nombre de archivo de datos de Temperatura y radiación:")
tempRad = input()         #pido nombre de archivo de datos de entrada de Temp y Rad
# tempRad = "Datos_T_rad.txt"
print("Gracias! Ahora ingrese el nombre del archivo de datos de V y I:")
celdasIV = input()        #pido nombre de archivo de datos de entrada de voltaje y corriente
# celdasIV = "Datos_V_I.txt"

f1 = leerArchivoEntrada(tempRad)                          # lee archivos de entrada 
f2 = leerArchivoEntrada(celdasIV)
datosLimpiosConTitulo1 = limpioDatosCreoLista(f1)         # inicio con el archivo de T ambiente y radiación
datosLimpiosConTitulo2 = limpioDatosCreoLista(f2)         # ahora el archivo de corriente y voltaje de las celdas

cabecera1 = datosLimpiosConTitulo1[0]                 #construyo una lista con la línea que tiene los títulos
datosLimpiosConTitulo1.pop(0)                         # elimino la línea de los títulos, para que me queden sólo los valores medidos
datosLimpios1 = pasoAfloat(datosLimpiosConTitulo1)    #paso los valores a tipo float para poder operar con ellos
cabeceraCeldas = datosLimpiosConTitulo2[0]            #guardo una lista con los títulos de las celdas
cabecera2 = datosLimpiosConTitulo2[1]                 #guardo en otra lista las líneas de los títulos del archivo de I - V 
datosLimpiosConTitulo2.pop(0)                         #quito las 2 líneas de los títulos
datosLimpiosConTitulo2.pop(0)
datosLimpios2 = pasoAfloat(datosLimpiosConTitulo2)    #paso los valores a tipo float para poder operar con ellos

# mostrar por pantalla el contenido de los archivos de entrada
print("Gracias! Ud. ingresó los siguientes datos:", "\n", "\n", "\n")
print("TEMPERATURA Y RADIACIÓN","\n", "\n", "\n")
print(cabecera1, "\n")
[print(linea, "\n") for linea in datosLimpios1]
print( "\n", "\n", "\n")
print("VOLTAJE Y CORRIENTE PARA CADA CELDA", "\n", "\n")
print(cabeceraCeldas, "\n")
print(cabecera2, "\n")
[print(linea, "\n") for linea in datosLimpios2]
print("\n", "\n", "\n")
print("Aguarde unos momentos, por favor", "\n", "\n", "\n")

# CORRECCIÓN DE DATOS DE VOLTAJE Y CORRIENTE POR TEMPERATURA Y RADIACIÓN
#calculo los factores de corrección para voltaje y corriente y los guardo alternados en la misma lista
fac = calculoFactoresDeCorreccion(datosLimpios1)

superFac = []        #armo una matriz(lista de listas) con los factores de corrección
for i in range(len(datosLimpios2)):
    superFac.append(fac)

# hago las correcciones en los valores de V - I
vCorrIcorr = corregirVoltajeCorriente(datosLimpios2, superFac)

"""POTENCIA 
Calculo la potencia para cada par de valores V - I para todas las celdas y los guardo en otra lista
Las columnas son los valores obtenidos para cada celda."""
potenciaCeldas = calcularPotencia(vCorrIcorr)
# traspongo la lista de listas de potencia para todas las celdas, así queda CADA CELDA EN UNA FILA
potenciaCeldaXlinea = traspuesta(potenciaCeldas)
# Obtengo los valores de potencia máxima para cada celda y los guardo en otra lista
maximaPotenciaXcelda = buscaMaximoXlinea(potenciaCeldaXlinea)
maxPotXceldaComoString = datosFloatComoString(maximaPotenciaXcelda)    #paso los números float a string
# Creo la lista con los títulos de las celdas y sus valores de potencia máxima
potenciaMaxCeldas = []
potenciaMaxCeldas.append(cabeceraCeldas)
potenciaMaxCeldas.append(maxPotXceldaComoString)
# Muestro por pantalla los valores de la potencia máxima para cada celda
print("POTENCIA MÁXIMA")
[print(linea, "\n") for linea in potenciaMaxCeldas]
# escribo archivo de salida con las potencias máximas para cada celda
escribeOutListaDeListas(potenciaMaxCeldas, "PotenciaMaximaCeldas.txt")

# CURVA DE AJUSTE DE CORRIENTE VS. VOLTAJE
"""Se desean ajustar las curvas experimentales con una expresión del tipo:
I = k1 + k2*(exp(k3*V))
donde I y V son los valores ya corregidos por temperatura y radiación.
Debido a las características de las celdas fv, k1 debería ser el valor máximo de corriente medida: k1 = max(Icorr).
(debería corresponder aproximadamente con la I0 o corriente de cortocircuito).
Existe un método (curve_fit) en la librería Scipy que sirve para ajustar curvas, a partir de una expresión 
que le proponemos a curve_fit. El método ajusta los coeficientes a partir de la expresión de la 
función y los datos con los que se entrena al modelo.
Antes de determinar la curva de ajuste, tengo que modificar las listas de datos.
Voy a trasponer la matriz/lista de listas con los datos corregidos para todas las celdas.
De esta manera, los valores de voltaje y corriente de cada celda quedarán en líneas y ordenadas de a pares, 
siendo la primera línea la lista de voltajes para la celda 1, la segunda línea la lista de corrientes de la celda 1,
y así sucesivamente para todas las celdas. Las líneas pares son voltajes y las líneas impares, corrientes."""

datosEnLineaXcelda = traspuesta(vCorrIcorr)

# Ahora, vamos a correr los ajustes y generar los gráficos para cada celda
coeficientesCeldas = []
for i in range(len(cabeceraCeldas)):
    coef = []
    # transforma las listas de datos en un array de numpy de floats para que curve_fit pueda trabajar
    x = np.array(datosEnLineaXcelda[2*i], dtype=float)    # voltaje de la celda 
    y = np.array(datosEnLineaXcelda[2*i+1], dtype=float)  # voltaje de la celda 
    celda = cabeceraCeldas[i]                             # nombre de la celda
    popt, pcov = curve_fit(func, x, y)    # llama a curve_fit para que ajuste los coeficientes de la fn sugerida
    # popt[0] = a , popt[1] = b, popt[2] = c ---> Los mando a una lista, luego irán a un archivo. 
    coef = [celda, str(round(popt[0],8)), str(round(popt[1],8)), str(round(popt[2],8))]
    coeficientesCeldas.append(coef)
    v = np.arange(0, 23, 1)  # creo un vector de valores de V para evaluar la curva de ajuste
    # El gráfico de los valores medidos y la curva de ajuste se guardan en un archivo celda"n".png
    plt.figure()
    plt.plot(v, func(v, *popt), label="Curva ajustada", color = "red", linewidth = 2)      # la curva de ajuste en línea roja
    plt.plot(datosEnLineaXcelda[2*i], datosEnLineaXcelda[2*i+1], 'bo', label="Datos medidos")   # los datos medidos en círculos azules,"bo" significa círculos azules
    plt.legend(loc='lower left')
    plt.xlabel("V(voltios)")
    plt.ylabel("I(amperes)")
    plt.title("Curva I vs V: %s" % (celda), loc = "left")    # título de la celda "n"
    # ecuación de la curva ajustada con sus coeficientes
    plt.title("I = %s + (%s)*exp(%s*V)" % (round(popt[0],3), round(popt[1],5), round(popt[2],3)), loc = "right")
    plt.savefig('%s.png' %(celda), dpi=300)    # guarda el gráfico como .png
    plt.close()

"""CURVA DE AJUSTE DE POTENCIA VS VOLTAJE
Análogo a la curva de I vs. V para cada celda, podemos construir una curva de Potencia vs V y
graficarla para buscar el máximo de potencia. Y también podemos proponer una curva que ajuste
la potencia como función de V.
Usando la misma curva de ajuste para I = f(V), obtenemos un ajuste para P.
P(V) = I*V = a + b*V + c*V*exp(d*V)"""

coefPotCeldas = []
for i in range(len(cabeceraCeldas)):
    coef = []
    # transforma las listas de datos en un array de numpy de nros. floats para que curve_fit pueda trabajar
    x = np.array(datosEnLineaXcelda[2*i], dtype=float)  # voltaje de la celda 
    y = np.array(potenciaCeldaXlinea[i], dtype=float)   # potencia de la celda 
    celda = cabeceraCeldas[i]                           # nombre de la celda
    popt, pcov = curve_fit(fnPotencia, x, y)    # llama a curve_fit para que ajuste los coeficientes de la fn sugerida
    # popt[0] = a , popt[1] = b, popt[2] = c, popt[3] = d ---> Los mando a una lista, luego irán a un archivo. 
    coef = [celda, str(round(popt[0],8)), str(round(popt[1],8)), str(round(popt[2],8)), str(round(popt[3],8))]
    coefPotCeldas.append(coef)
    v = np.arange(0, 23, 1)  # creo un vector de valores para V para evaluar la curva de ajuste
    # El gráfico de los valores de potencia y la curva de ajuste se guardan en un archivo potencia_celda"n".png
    plt.figure()
    plt.plot(v, fnPotencia(v, *popt), label="Curva ajustada", color = "cyan", linewidth = 2)   # la curva de ajuste en línea cyan
    plt.plot(datosEnLineaXcelda[2*i], potenciaCeldaXlinea[i], 'mx',label="Datos medidos")   # los datos medidos en cruces magenta
    plt.legend(loc='lower center')
    plt.xlabel("V(voltios)")
    plt.ylabel("Potencia(vatios)")
    plt.title("Curva Pot vs V: %s" % (celda), loc = "left", fontsize = 10)    # título de la celda "n"
    # ecuación de la curva ajustada con sus coeficientes
    plt.title("P = %s + %s*V +(%s)*V*exp(%s*V)" % (round(popt[0],2), round(popt[1],1), round(popt[2],5), round(popt[3],3)), loc = "right", fontsize = 10)
    plt.savefig('potencia_%s.png' %(celda), dpi=300)    # guarda el gráfico a un archivo .png
    plt.close()

# Armo las listas de coeficientes ajustados con su identificación y los guardo en archivos .txt
cabeceraCoef = ['      ', 'k1        ', 'k2         ', 'k3']
cabeceraCoefPotencia = ['      ', 'a          ', 'b         ', 'c          ', 'd']
listaCoef = [cabeceraCoef] + coeficientesCeldas
listaCoefPot = [cabeceraCoefPotencia] + coefPotCeldas
escribeOutListaDeListas(listaCoef, 'CoeficientesK.txt')
escribeOutListaDeListas(listaCoefPot, 'CoefPotencia.txt')

print("PUEDE ENCONTRAR LOS RESULTADOS DE POTENCIA EN LOS ARCHIVOS PotenciaMaximaCeldas.txt")
print("EN EL ARCHIVO 'CoeficientesK.txt' y 'CoefPotencia.txt' SE ENCUENTRAN LOS COEFICIENTES DE LAS CURVAS DE AJUSTE PARA C/ CELDA.")
print("LOS GRÁFICOS DE I vs. V Y SU CURVA DE JUSTE SE ENCUENTRAN EN 'celda'i'.PNG', i ES EL NÚMERO DE CELDA.")
print("LOS GRÁFICOS DE POTENCIA vs. V Y SU CURVA DE AJUSTE SE ENCUENTRAN EN 'potencia_celda'i'.PNG', i ES EL NÚMERO DE CELDA.")
print("QUÉ TENGA UN EXCELENTE DÍA!!!")
# LISTO!!!! Ya terminamos :)