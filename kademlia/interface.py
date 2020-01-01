import asyncio
import argparse
from network import Server

# command line interface
class app(object):
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
                                 metavar=('bootstrap node address', 'bootstrap node port'))
        (options, args) = self.parser.parse_args()
        if options.first_node: return None
        else:
            try:
                return options.bootstrap
            except:
                print('To start a node and join existing network, you need a bootstrap node to connect the exist network.')

    def print_help(self):
        commands = {
            'help': 'print this help',
            'get': 'get the value for given key',
            'put': 'update the value of the specified key',
            'delete': 'delete the key in the storage system',
            'quit': 'exit the system'
        }
        self.parser.print_help()
        print('\n\tCLI commands:')
        for command, description in commands:
            print( "%-10s %s" % (command, description) )

    def quit(self, server, loop):
        server.stop()
        loop.close()

    def run(self):
        print("""Welcome to this p2p key-value system.
            To find out what other commands exist, type 'help'""")

        bootstrap_node =self.parse_commandline()

        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(True)
        self.server = Server()
        self.loop.run_until_complete(self.server.listen(8468))
        if bootstrap_node:
            bootstrap_node = (bootstrap_node[0], int(bootstrap_node[1]))
            self.loop.run_until_complete(self.server.bootstrap([bootstrap_node]))
        while True:
            try:
                io = input('Command: ')
                if io == 'help':
                    self.print_help()
                elif io == 'get':
                    print("Usage:<key>")
                    args = input().split(' ')
                    if len(args) != 1: print("Number of parameters does not match.")
                    else:
                        result = self.loop.run_until_complete(self.server.get(args[0]))
                        print("Get result:", result)
                elif io == 'put':
                    print("Usage: <key> <value>")
                    args = input().split(' ')
                    if len(args) != 2: print('Number of parameters dose not match.')
                    self.loop.run_until_complete(self.server.set(args[0], args[1]))
                elif io == 'delete':
                    print("Usage: <key>")
                elif io == 'quit':
                    print('Bye ~ Have a nice day.')
                    self.quit()
            except EOFError:
                self.quit()