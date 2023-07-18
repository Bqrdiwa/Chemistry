import requests


sender = '+983000505'
to = '09222945873'
msg = 'salam '
uname = '09397962707'
passw = 'Faraz@3242523601'

apiKey = 'inj29QmiusdNG2Meu0kbD2LHG9n18Fi1i5nUGkEYkWo='

url = f'http://ippanel.com:8080/?apikey={apiKey}&pid=pattern-code&fnum=sender-number&tnum=phone-number&p1=variable2&p2=variable2&v1=value1&v2=value2'
req = requests.get(url)
print(req.content)


