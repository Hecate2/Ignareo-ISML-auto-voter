from requests import post

headers={'ipNum':'5'}
payload={'0':'1.1.1.1:8080',
         '1':'2.2.2.2:8080',
         '2':'2.2.2.2:8080',
         '3':'2.2.2.2:8080',
         '4':'2.2.2.2:8080',}
response=post(url='http://127.0.0.1:8999/main',headers=headers,json=payload)
pass