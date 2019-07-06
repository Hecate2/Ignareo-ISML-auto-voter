import stackless
import stacklesssocket30
stacklesssocket30.install()

import requests

def test(i):
    r = requests.get('http://httpbin.org/get')
    print(r.text)

for i in range(5):
    stackless.tasklet(test)(i)

stackless.run()
