def contar_numeros(lista):
    diccionario = {}
    for numero in lista:
        if numero in diccionario:
            diccionario[numero] += 1
        else:
            diccionario[numero] = 1
    return diccionario

# Ejemplo de uso
lista = [1, 2, 3, 4, 2, 3, 1, 2, 4, 4, 5]
resultado = contar_numeros(lista)
print(resultado)
