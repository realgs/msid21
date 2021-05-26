lista = [5, 2, 3, 4, 8, 11, -5, 10]

for i in range(len(lista)-1, 0, -1):
    max_val = lista[0]
    max_index = 0
    for j in range(1, i+1):
        if lista[j] > max_val:
            max_val = lista[j]
            max_index = j
    lista[i], lista[max_index] = lista[max_index], lista[i]
    

print(lista)