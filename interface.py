import asyncio
import logging
import argparse
from time import sleep
from threading import Thread
from kademlia.network import Server


# command line interface
class App(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='A p2p key-value databse.')

    def parse_commandline(self):
        self.parser.add_argument('-f', '--first',
                                 action = 'store_true',
                                 dest = 'first_node',
                                 default = False,
                                 help="Start the first node in the p2p network")
        self.parser.add_argument('-b', '--bootstrap',
                                 nargs = 2,
                                 dest = 'bootstrap',
                                 metavar=('<address>', '<port>'),
                                 help = "Start a node and connect to bootstrap node in existing network")
        self.parser.add_argument('-p', '--port',
                                 nargs = 1,
                                 dest = 'port',
                                 metavar=('<port>'),
                                 default = [8468],
                                 help = 'Server listen to this port.')
        self.parser.add_argument('--flooding',
                                 dest='flooding',
                                 nargs=3,
                                 metavar=('<iprange_l>', '<iprange_r>', '<ports>'),
                                 default=None,
                                 help="Flooding neighbors instead of explicit bootstrapping given node. "
                                      "Format of <ports>:"
                                      "I: 9468,8469,8890 (equals [9468, 8469, 8890])"
                                      "II: 8469~8891 (equals list(range(8469, 8892)))"
                                      "Example: 192.168.1.1 192.168.2.0 8468~8470")
        self.parser.add_argument('-t', '--timeout',
                                 nargs=1,
                                 dest='wait_timeout',
                                 metavar='<timeout>',
                                 default=(5, ),
                                 help='Wait timeout for bootstrapping and flooding')
        self.parser.add_argument('-r', '--record',
                                 action='store_true',
                                 dest='record',
                                 default=False,
                                 help='If True, record active neighbors in the 0-th k-bucket')
        options = self.parser.parse_args()
        try:
            return (options.flooding, options.bootstrap, options.port, options.wait_timeout, options.record)
        except:
            print('To join existing network, you need a bootstrap node or flooding setting.')
        # if options.first_node: return (options.flooding, options.bootstrap, options.port)
        # else:
        #     try:
        #         return (options.flooding, options.bootstrap, options.port)
        #     except:
        #         print('To join existing network, you need a bootstrap node to connect the exist network.')

    def print_help(self):
        commands = {
            'help': 'print this help',
            'get': 'get the value for given key',
            'put': 'update the value of the specified key',
            'delete': 'delete the key in the storage system',
            'quit': 'exit the system'
        }
        self.parser.print_help()
        print('\nCLI commands:')
        for command, description in commands.items():
            print( "%-10s %s" % (command, description) )

    def quit(self):
        self.server.stop()
        self.loop.close()

    def start_loop(self):

        self.loop.set_debug(True)
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.server.stop()
            self.loop.close()

    def run(self):
        print("""Welcome to this p2p key-value system. To find out what other commands exist, type 'help'""")

        # log
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        log = logging.getLogger('kademlia')
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)

        # command information
        flooding_nodes, bootstrap_node, port, timeout, record =self.parse_commandline()

        # run subthread
        self.loop = asyncio.new_event_loop()
        self.t = Thread(target=self.start_loop)
        self.server = Server(timeout=int(timeout[0]), record=record)

        self.t.setDaemon(True)
        self.t.start()

        # self.server.reset(timeout=int(timeout[0]), record=record)

        asyncio.run_coroutine_threadsafe(self.server.listen(int(port[0])), self.loop).result()
        if bootstrap_node is not None:
            bootstrap_node = (bootstrap_node[0], int(bootstrap_node[1]))
            re = asyncio.run_coroutine_threadsafe(self.server.bootstrap([bootstrap_node]), self.loop).result()
        elif flooding_nodes is not None:
            iprange_l, iprange_r, ports = flooding_nodes
            if '~' in ports:
                l, r = ports.split('~')
                ports = list(range(int(l), int(r)))
            else:
                str_ports = ports.split(',')
                ports = [int(i) for i in str_ports]

            re = asyncio.run_coroutine_threadsafe(self.server.bootstrap(flooding=True, iprange_l=iprange_l,
                                                                        iprange_r=iprange_r, ports=ports),
                                                  self.loop).result()

        while True:
            sleep(0.3)
            try:
                io = input('Command: ').lstrip().rstrip()
                if io == 'help':
                    self.print_help()
                elif io == 'get':
                    print("Usage:<key>")
                    args = input().split(' ')
                    if len(args) != 1: print("Number of parameters does not match.")
                    else:
                        result = asyncio.run_coroutine_threadsafe(self.server.get(args[0]), self.loop).result()
                        result = result[0] if result else None
                        print("Get result:", result)
                elif io == 'put':
                    print("Usage: <key> <value>")
                    args = input().split(' ')
                    if len(args) != 2: print('Number of parameters dose not match.')
                    else:
                        asyncio.run_coroutine_threadsafe(self.server.set(args[0], args[1]), self.loop).result()
                elif io == 'delete':
                    print("Usage: <key>")
                    args = input().split(' ')
                    if len(args) != 1: print('Number of parameters dose not match.')
                    else:
                        asyncio.run_coroutine_threadsafe(self.server.delete(args[0]), self.loop).result()
                elif io == 'quit':
                    print('Bye ~ Have a nice day.')
                    self.loop.call_soon_threadsafe(self.quit)
                    break
                else:
                    print('Sorry! Invalid command.')
            except EOFError:
                self.loop.call_soon_threadsafe(self.quit)
                break


if __name__ == '__main__':
    app = App()
    app.run()
