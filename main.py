import APIHandler
import time

token = '1bf756322d822760d3153f9f54be7bfe1cea94a6'
api_url = 'http://192.168.86.34:2550/api'
config_path = '/config'

f = APIHandler.APIHandler(token, api_url, config_path)
print("APIHandler created")

while True:
    f.update()
    time.sleep(2)
