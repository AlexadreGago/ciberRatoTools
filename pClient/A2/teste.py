import timeit




def teste(direction):
    if direction == "right" or direction == "left":
        return True
    else:
        return False

def teste2(direction):
    if direction in {"right", "left"}:
        return True
    else:
        return False

T=timeit.Timer("teste('right')", globals=globals())
T2 = timeit.Timer("teste('left')", globals=globals())

T3=timeit.Timer("teste2('right')", globals=globals())
T4 = timeit.Timer("teste2('left')", globals=globals())

print(T.timeit(1000000))
print(T2.timeit(1000000))
print(T3.timeit(1000000))
print(T4.timeit(1000000))