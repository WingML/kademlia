import logging
import asyncio
import time
import random

from kademlia.network import Server

loop = asyncio.get_event_loop()
loop.set_debug(True)

server = Server()
loop.run_until_complete(server.listen(8468))

bootstrap_node = ('192.168.1.240', 8468)
loop.run_until_complete(server.bootstrap([bootstrap_node]))
avg_response_time = 0

key = 'performance_test'
value = 'testValue'
loop.run_until_complete(server.set(key, value))

for i in range(500):
    option = random.randint(1, 3)
    start = time.time()
    if option == 1: # read
        loop.run_until_complete(server.get(key))
    elif option == 2: # write
        loop.run_until_complete(server.set(key, value))
    else:
        loop.run_until_complete(server.delete(key))
    end = time.time()
    print('Operation time: %d' % (end-start))
    avg_response_time += (end-start)
avg_response_time /= 500
print('Average respone time: %d' % avg_response_time)
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    server.stop()
    loop.close()
