# -*- coding: utf-8 -*-

try:
    from ptc import Socket, SHUT_WR
except:
    import sys
    sys.path.append('../catedra/')
    from ptc import Socket, SHUT_WR

import time

SERVER_IP = '127.0.0.1'
SERVER_PORT = 6677

to_send = 'msg'
end     = 'end'

def conectar_server(cliente, n):
    '''cliente =  {'alpha':X, 'beta':X, 'proba':X, 'delay':X}
       n       = numero de msg que envia '''

    time.sleep(1)

    a, b = cliente['alpha'], cliente['beta']
    d, p = cliente['proba'], cliente['delay']
    verbose = True

    with Socket(a, b, d, p, verbose=True) as client_sock:
        client_sock.connect((SERVER_IP, SERVER_PORT), timeout=5)

        for i in xrange(n):
            client_sock.send(to_send)
       
        #El ultimo mensaje tiene que llegar si o si
        client_sock.alumnos_change_proba(0.0)
        client_sock.send('end')

def n_vs_rto():
    print "N VS RTO"

    envios  = [1,5,10,15,20,25]
    cliente = {'alpha':1./8., 'beta':1./2., 'proba':0.0, 'delay':0.0}
    
    print "ENVIOS:", envios

    for n in envios:
        conectar_server(cliente, n)

def beta_vs_rto(): 
    print "BETA VS RTO"

    n     = 10
    betas = [0., 1./4., 1./2., 3./4., 1.]

    print "BETAS:", betas

    for beta in betas:
        cliente = {'alpha':1./8., 'beta':beta, 'proba':0.0, 'delay':0.0}
        conectar_server(cliente, n)

def alpha_vs_rto(): 
    print "ALPHA VS RTO"

    n      = 10
    alphas = [0., 1./4., 1./2., 3./4., 1.]

    print "ALPHAS:", alphas

    for alpha in alphas:
        cliente = {'alpha':alpha, 'beta':1./2., 'proba':0.0, 'delay':0.0}
        conectar_server(cliente, n)

def delay_vs_rto(): 
    print "DELAY VS RTO"

    n      = 10
    delays = [0., 5., 10., 15., 20.]

    print "DELAYS", delays

    for delay in delays:
        cliente = {'alpha':1./8., 'beta':1./2., 'proba':0.0, 'delay':delay}
        conectar_server(cliente, n)

def proba_vs_rto(): 
    print "PROBA VS RTO"

    n      = 10
    probas = [0., 0.1, 0.2, 0.3, 0.4]

    print "PROBAS", probas

    for proba in probas:
        cliente = {'alpha':1./8., 'beta':1./2., 'proba':proba, 'delay':0.0}
        conectar_server(cliente, n)

def main():
    n_vs_rto()
    alpha_vs_rto()
    beta_vs_rto()
    delay_vs_rto()
    proba_vs_rto()
    


if __name__ == "__main__":
    main()
