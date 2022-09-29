import time

import APIHandler

token = '1bf756322d822760d3153f9f54be7bfe1cea94a6'
api_url = 'http://192.168.86.34:2550/api'
config_path = '/config'

f = APIHandler.APIHandler(token, api_url, config_path)
print("APIHandler created")

error_counter = 0
sleep_time = 2

while True:
    try:
        f.update()
        error_counter = 0
        sleep_time = 2
        time.sleep(sleep_time)
    except (ConnectionResetError, OSError, ConnectionError) as e:
        if error_counter == 5:
            print(f"{e} 5 times in a row, exiting")
            exit(1)
        print(f"{e} occurred, waiting {sleep_time} seconds")
        error_counter += 1
        sleep_time += 1
        time.sleep(5)
