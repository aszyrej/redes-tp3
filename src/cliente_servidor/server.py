# -*- coding: utf-8 -*-

try:
    from ptc import Socket
except:
    import sys
    sys.path.append('../catedra/')
    from ptc import Socket

import time

SERVER_IP = '127.0.0.1'
SERVER_PORT = 6677

while True:

    print ("Starting server!")
    with Socket() as server_sock:

        server_sock.bind((SERVER_IP, SERVER_PORT))
        server_sock.listen()
        server_sock.accept(timeout=60)

        not_exit = True
        while not_exit:
            received = str()
            received += server_sock.recv(3)

            # Some packages come shifted.
            while received != 'msg' and received != 'end':
                time.sleep(.01)
                received += server_sock.recv(3 - len(received))

                if received != 'msg' and received != 'end':
                    print("Incomplete message! Now it's {}".format(received))

            not_exit = received != 'end'

