# github.com/Hecate2/Ignareo

import asyncio, gevent
from gevent import monkey
monkey.patch_all()

import tornado.ioloop
import tornado.web
from tornado.tcpserver import TCPServer
from tornado.iostream import StreamClosedError
from tornado.platform.asyncio import AsyncIOMainLoop

ws_port = 55568
tcp_port = 6868
worker_loop = asyncio.get_event_loop()

import tornado.websocket
from greenlet import greenlet

import time, datetime, gc

def greenlet_exit_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            func(*args, **kwargs)
        except greenlet.GreenletExit:
            print(f'GreenletExit after {time.time()-start_time} seconds')
        except:
            print(f'Unexpected error after {time.time() - start_time} seconds')
            # raise Exception
    return wrapper

@greenlet_exit_decorator  # use this to prevent greenlet corruption
def autoplay(callback, callback_message):
    # time.sleep(60)
    # func1('func1')
    # time.sleep(5*60)
    # func2('func2')
    # time.sleep(60)
    # func3('func3')
    # return True
    time.sleep(3)
    func1('func1')
    time.sleep(5)
    func2('func2')
    time.sleep(3)
    func3('func3')
    gevent.spawn(callback, callback_message)
    return True

def autostop(greenlets):
    '''
    autostop some greenlets
    :param greenlets: List[gevent.Greenlet]
    :return: Bool
    '''
    gevent.killall(greenlets)

def autostop_auto():  # autostop all greenlets
    gevent.killall([obj for obj in gc.get_objects() if isinstance(obj, gevent.Greenlet)])


def func1(*args, **kwargs):
    print(args, kwargs)
def func2(*args, **kwargs):
    print(args, kwargs)
def func3(*args, **kwargs):
    print(args, kwargs)


class WSHandler(tornado.websocket.WebSocketHandler) :
    websocket_ping_interval = 30
    websocket_ping_timeout = 10
    
    def check_origin(self, origin) :
        '''重写同源检查 解决跨域问题'''
        return True

    def open(self) :
        '''新的websocket连接后被调动'''
        pass
        # print('open')
        # self.write_message('Opened')

    def on_close(self):
        '''websocket连接关闭后被调用'''
        pass
        # print('close')

    def on_message(self, message) :
        '''接收到客户端消息时被调用'''
        print(f'{datetime.datetime.now()}: {message}')
        self.write_message(f'new message: {message}')  # 向客服端发送
        if message=='autoplay':
            gevent.spawn(autoplay, self.write_message, 'True')
        elif message=='autostop':
            autostop_auto()


class MainHandler(tornado.web.RequestHandler) :
    def get(self) :
        self.render("index.html")


class Application(tornado.web.Application) :
    def __init__(self) :
        handlers = [
            (r'/', MainHandler),
            (r'/index', MainHandler),
            (r'/ws', WSHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


class TCPHandler(TCPServer):
    async def handle_stream(self, stream, address):
        while True:
            try:
                data = await stream.read_until(b"\n", max_bytes=1024)
                # stream.write(data)
                print(f'{datetime.datetime.now()}: {data}')
                await stream.write(f'new message: {data}'.encode('utf8'))
                if b"autoplay" in data:
                    gevent.spawn(autoplay, stream.write, b'True')
                elif b"autostop" in data:
                    autostop_auto()
            except StreamClosedError:
                break


def run_proc():
    AsyncIOMainLoop().install()  # 让tornado使用asyncio的事件循环
    app = Application()
    app.listen(ws_port)
    print(f'HTTP and websocket running on port {ws_port}')

    tcp_server = TCPHandler()
    tcp_server.listen(tcp_port)
    print(f'TCP server running on port {tcp_port}')
    
    # 可以gevent.spawn
    # 写在这里的代码仅在Ignareo启动时运行一次
    
    worker_loop.run_forever()
    # 让asyncio的事件循环永远运行下去！毕竟这是个永远运行的服务器
    # 这之后写的任何代码都不会被执行


if __name__ == '__main__':
    run_proc()