import gc,time

gc.disable()
mem=list(range(100000000))
mem=0
gc.collect()
print('finished')
time.sleep(3600)
