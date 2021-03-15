lista = [5, 2, 3, 4, 8, 11, -5, 10]

for i in range(len(lista)-1, 0, -1):
    for j in range(0, i-1):
        if lista[j] > lista[j + 1]:
            lista[j], lista[j + 1] = lista[j + 1], lista[j]

print(lista)