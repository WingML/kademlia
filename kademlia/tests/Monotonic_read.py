import logging
import asyncio
import time

from kademlia.network import Server

loop = asyncio.get_event_loop()
loop.set_debug(True)

server = Server()
loop.run_until_complete(server.listen(8469))

bootstrap_node = ('0.0.0.0', 8468)
loop.run_until_complete(server.bootstrap([bootstrap_node]))
for i in range(200):
    key = 'test_monotonic_read'
    value = time.time()
    print(key, value)
    time.sleep(0.1)
    loop.run_until_complete(server.set(key, value))

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    server.stop()
    loop.close()
