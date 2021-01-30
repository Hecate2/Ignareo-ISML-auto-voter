'''
g = list_cycle_gen(iterable)
next(g); next(g); next(g); next(g); ...
'''
def list_cycle_gen(_list):
    while 1:
        for i in _list:
            yield i

