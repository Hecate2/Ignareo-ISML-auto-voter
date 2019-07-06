from multiprocessing import Process
import os

# 子进程要执行的代码
def run_proc(name):
    print('Run child process %s (%s)...' % (name, os.getpid()))
    while 1:
        pass

if __name__=='__main__':
    print('Parent process %s.' % os.getpid())
    p = Process(target=run_proc, args=('test',))
    p.start()
    #p.join()
    p = Process(target=run_proc, args=('test',))
    p.start()
    p = Process(target=run_proc, args=('test',))
    p.start()
    #print('Child process end.')