from json import loads

class mainHandler():
    def get_ip(self,ipNum):
        ipNum=int(ipNum)
        data=loads(self)
        for num in range(ipNum):
            print(data[str(num)])
            # 创建协程