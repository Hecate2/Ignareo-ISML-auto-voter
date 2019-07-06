class AsyncIteratorWrapper:
    def __init__(self, obj):
        self._it = iter(obj)
 
    def __aiter__(self):
        return self
 
    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value

async def printer(numRange):
    #async for i in AsyncIteratorWrapper(range(numRange)):
    async for i in AsyncIteratorWrapper([1,2,3,4,'艾瑟雅天下第一']):
        print(i)
    
    

if __name__ == "__main__":
    try:
        printer(10).send(None)
    except StopIteration as e:
        print(e.value)
