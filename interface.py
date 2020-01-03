import asyncio
import logging
import argparse
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
        options = self.parser.parse_args()
        if options.first_node: return (None, options.port)
        else:
            try:
                return (options.bootstrap, options.port)
            except:
                print('To join existing network, you need a bootstrap node to connect the exist network.')

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

    def quit(self, server, loop):
        server.stop()
        loop.close()

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
        bootstrap_node, port =self.parse_commandline()
        print(bootstrap_node)
        # create server and run
        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(True)
        self.server = Server()
        self.loop.run_until_complete(self.server.listen(int(port[0])))
        if bootstrap_node:
            bootstrap_node = (bootstrap_node[0], int(bootstrap_node[1]))
            self.loop.run_until_complete(self.server.bootstrap([bootstrap_node]))
        while True:
            try:
                io = input('Command: ').lstrip().rstrip()
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
                    self.quit(self.server, self.loop)
                    break
                else:
                    print('Sorry! Invalid command.')
            except EOFError:
                self.quit(self.server, self.loop)
                break


if __name__ == '__main__':
    app = App()
    app.run()