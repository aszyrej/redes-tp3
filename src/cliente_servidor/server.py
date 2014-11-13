# -*- coding: utf-8 -*-

try:
    from ptc import Socket
except:
    import sys
    sys.path.append('../catedra/')
    from ptc import Socket

SERVER_IP = '127.0.0.1'
SERVER_PORT = 6677

while True:

    with Socket() as server_sock:

        server_sock.bind((SERVER_IP, SERVER_PORT))
        server_sock.listen()
        server_sock.accept(timeout=10)

        not_exit = True
        while not_exit:
            received = str()
            received += server_sock.recv(3)
            not_exit = received != 'end'
