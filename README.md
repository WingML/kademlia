# P2P key-value stroage system based on kadmelia 

## Environment

```
pip install -r requirements.txt
```

## Usage

If you are starting the first node in the p2p system:

```
python interface.py -f
```

And you can set the specific port by:

```
python interface.py -f -p <port>
```

If system already exists, a node want to join the system need  to specify bootstrap node information:

```
python interface.py -b <ip> <port> 
```

Of course you can set the specific port by '-b'.

If you are still in doubt, you can use help:

```
python interface -h
```


