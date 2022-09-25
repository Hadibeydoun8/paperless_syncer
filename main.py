import time

import APIHandler

token = '1bf756322d822760d3153f9f54be7bfe1cea94a6'
api_url = 'http://192.168.86.34:2550/api'
config_path = '/config'

f = APIHandler.APIHandler(token, api_url, config_path)
print("APIHandler created")

error_counter = 0

while True:
    try:
        f.update()
        error_counter = 0
        time.sleep(2)
    except ConnectionResetError:
        if error_counter == 5:
            print("Connection Reset Error 5 times in a row, exiting")
            exit(1)
        print("ConnectionResetError")
        error_counter += 1
        time.sleep(5)
