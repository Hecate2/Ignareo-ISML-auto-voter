import timeit

d = {i: i+1 for i in range(3)}
print(timeit.repeat(lambda: next(iter(d.values()))))
print(timeit.repeat(lambda: list(d.values())[0]))
