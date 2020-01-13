"""
General catchall for functions that don't make sense as methods.
"""
import hashlib
import operator
import asyncio


def to_flood(iprange_l, iprange_r, ports):
    '''
    Find out all ip:port within range [iprange_l, iprange_r)
    and with given ports.

    Args:
        iprange_l, iprange_r: str, dot decimal format, e.g. '192.168.2.1'
        ports: A 'list' of int ports
    '''
    ip_l = ip2dec(iprange_l)
    ip_r = ip2dec(iprange_r)

    addrs = []
    for ip in range(ip_l, ip_r):
        # if ip & 0xff == 0 or ip & 0xff00 == 0:
        if ip & 0xff == 0:
            continue

        dec_ip = dec2ip(ip)
        for port in ports:
            addr = (dec_ip, port)
            addrs.append(addr)
    return addrs


def ip2dec(ip):
    segs = [int(s) for s in ip.split('.')]
    return sum([segs[i] << (24, 16, 8, 0)[i] for i in range(4)])


def dec2ip(dec):
    segs = [str(dec >> bias & 0xff) for bias in (24, 16, 8, 0)]
    return '.'.join(segs)


async def gather_dict(dic):
    cors = list(dic.values())
    results = await asyncio.gather(*cors)
    return dict(zip(dic.keys(), results))


def digest(string):
    if not isinstance(string, bytes):
        string = str(string).encode('utf8')
    return hashlib.sha1(string).digest()


def shared_prefix(args):
    """
    Find the shared prefix between the strings.

    For instance:

        sharedPrefix(['blahblah', 'blahwhat'])

    returns 'blah'.
    """
    i = 0
    while i < min(map(len, args)):
        if len(set(map(operator.itemgetter(i), args))) != 1:
            break
        i += 1
    return args[0][:i]


def bytes_to_bit_string(bites):
    bits = [bin(bite)[2:].rjust(8, '0') for bite in bites]
    return "".join(bits)
