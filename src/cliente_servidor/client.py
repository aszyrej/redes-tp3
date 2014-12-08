#Tampoco vi que hayan estimado el RTT real, lo cual es importante para contrastar con lo encontradi -*- coding: utf-8 -*-

try:
    from ptc import Socket, SHUT_WR
except:
    import sys
    sys.path.append('../catedra/')
    from ptc import Socket, SHUT_WR

import time
import pylab
import argparse


SERVER_IP = '127.0.0.1'
SERVER_PORT = 6677

to_send = 'msg'
end     = 'end'

def conectar_server(cliente, n):
    time.sleep(1)
    a, b = cliente['alpha'], cliente['beta']
    d, p = cliente['delay'], cliente['proba']
    verbose = True

    with Socket(a, b, p, d, verbose) as client_sock:
        client_sock.connect((SERVER_IP, SERVER_PORT), timeout=5)
    
        for i in xrange(n):
            client_sock.send(to_send)

        time.sleep(1)

        rto, rtt = client_sock.alumnos_print_rto()
        perdidos = client_sock.alumnos_get_retransmitions()

        #El ultimo mensaje tiene que llegar si o si
        client_sock.alumnos_change_proba(0.0)
        client_sock.send(end)
        
    return rto, rtt, perdidos


def n_vs_rto():
    print "N VS RTO"

    time.sleep(1)

    alpha, beta  = 1./8., 1./2.
    delay, proba = 25.0 , 0.0
    verbose = False
    rtos = []
    rtts = []

    with Socket(alpha, beta, proba, delay, verbose ) as client_sock:
        client_sock.connect((SERVER_IP, SERVER_PORT), timeout=5)

        #Veo el RTO
        client_sock.alumnos_print_rto()       

        for i in xrange(30*5):

            client_sock.send(to_send)

            if i%5 == 0:
                # Cada 5 envios veo el RTO luego de
                # asegurarme que llegaron todos los paquetes
                time.sleep(1)
                rto, rtt = client_sock.alumnos_print_rto()       
                rtos += [rto]
                rtts += [rtt]
                
        print "termino"            
        #El ultimo mensaje tiene que llegar si o si
        client_sock.send(end)

    paquetes = [i*5 for i in xrange(30)]
    pylab.plot(paquetes, rtos)
    pylab.plot(paquetes, rtts)   

    pylab.xlabel('Cantidad Paquetes Enviados')
    pylab.ylabel('RTO (ticks)')
    pylab.title ('RTO vs Numero de Paquetes')
    pylab.legend(['rto','rtt'])
    pylab.tight_layout()
    pylab.savefig('n_vs_rto', format='pdf', orientation='landscape')
    pylab.clf()
 
def rto_vs_alpha_vs_beta(): 
    print "ALPHA, BETA VS RTO"

    arr_alpha = pylab.arange(0., 1.2, 0.2)
    arr_betas = pylab.arange(0., 1.2, 0.2)
    n = 50
    lalpha = len(arr_alpha)
    lbetas = len(arr_betas)
    resus = [ [0. for i in xrange(lalpha)] for j in xrange(lbetas)]

    for i in xrange(lalpha):
        for j in xrange(lbetas):
        
            a = arr_alpha[i]
            b = arr_betas[j]
            cliente = {'alpha':a, 'beta':b, 'proba':0.0, 'delay':25.0}
            rto, rtt, _ = conectar_server(cliente, n)

            print rto, rtt
            
            resus[lalpha-1-i][j] = rto

    #color_plot(resus)
    arr_betas_r = [b for b in reversed(arr_betas)]
    pylab.xticks(xrange(lalpha), arr_alpha)
    pylab.yticks(xrange(lbetas), arr_betas_r)
    pylab.imshow(resus, interpolation='nearest')
    pylab.colorbar()
    pylab.xlabel(r'$\beta$')
    pylab.ylabel(r'$\alpha$')
    pylab.title (r'RTO para valores de $\alpha$ y $\beta$')
    pylab.tight_layout()
    pylab.savefig('colormap', format='pdf', orientation='landscape')
    pylab.clf()

def perdidos_vs_alpha_vs_beta(): 
    print "ALPHA, BETA VS RTO"

    arr_alpha = pylab.arange(0., 1.2, 0.2)
    arr_betas = pylab.arange(0., 1.2, 0.2)
    n = 300
    lalpha = len(arr_alpha)
    lbetas = len(arr_betas)
    resus = [ [0. for i in xrange(lalpha)] for j in xrange(lbetas)]

    for i in xrange(lalpha):
        for j in xrange(lbetas):
        
            a = arr_alpha[i]
            b = arr_betas[j]
            cliente = {'alpha':a, 'beta':b, 'proba':0.0, 'delay':25.0}
            _, _, cant = conectar_server(cliente, n)
    
            print cant
            resus[lalpha-1-i][j] = cant

    #color_plot(resus)
    arr_betas_r = [b for b in reversed(arr_betas)]
    pylab.xticks(xrange(lalpha), arr_alpha)
    pylab.yticks(xrange(lbetas), arr_betas_r)
    pylab.imshow(resus, interpolation='nearest')
    pylab.colorbar()
    pylab.xlabel(r'$\beta$')
    pylab.ylabel(r'$\alpha$')
    pylab.title (r'Retransmisiones para $\alpha$ y $\beta$')
    pylab.tight_layout()
    pylab.savefig('ret_colormap', format='pdf', orientation='landscape')
    pylab.clf()

class congestion_subida:
    def __init__(self, alpha=0, beta=0, delay_inicial=25, proba=0, delay_final=50, verbose=True, size_burst=150, output = 'congestion.pdf', ylim = None):
        self.rtos = []
        self.rtts = []

        self.alpha = alpha
        self.beta = beta
        self.delay_inicial = delay_inicial
        self.proba = proba
        self.delay_final = delay_final
        self.verbose = verbose
        self.size_burst = size_burst
        self.output = output
        self.ylim = ylim

    def burst(self, times=150):
        for i in xrange(times):
            self.client_sock.send(to_send)

            if i%5 == 0:
                # Cada 5 envios veo el RTO luego de
                # asegurarme que llegaron todos los paquetes
                time.sleep(0.6)
                rto, rtt = self.client_sock.alumnos_print_rto()       
                self.rtos += [rto]
                self.rtts += [rtt]

    def run(self):
        print "Calculando parametros con congestion"
        with Socket(self.alpha, self.beta, self.proba, self.delay_inicial, self.verbose) as self.client_sock:
            self.client_sock.connect((SERVER_IP, SERVER_PORT), timeout=5)

            if self.verbose:
                print('\nCalculando todo con delay = {}'.format(self.delay_inicial))
            self.burst(times = self.size_burst)
            self.client_sock.alumnos_print_rto()

            if self.verbose:
                print('\nCalculando todo con delay = {}'.format(self.delay_final))
            self.client_sock.alumnos_change_delay(self.delay_final)
            self.burst(times = self.size_burst)
                
            #El ultimo mensaje tiene que llegar si o si
            self.client_sock.send(end)
            time.sleep(1)

            self.write_report()

    def write_report(self):
        paquetes = [5 * i for i in xrange(0, len(self.rtts))]
        pylab.plot(paquetes, self.rtos)
        pylab.plot(paquetes, self.rtts)   

        if self.ylim:
            pylab.gca().set_ylim([0, self.ylim])

        pylab.xlabel('Cantidad Paquetes Enviados')
        pylab.ylabel('RTO (ticks)')
        pylab.title ('RTO vs Numero de Paquetes ($^{{d_0}}/_{{d_f}} = {}$)'.format(self.delay_inicial * 1. / self.delay_final))
        pylab.legend(['rto','rtt'])
        pylab.tight_layout()
        pylab.savefig(self.output, format='pdf', orientation='landscape')
        pylab.clf()

def main():
#   n_vs_rto()
#   rto_vs_alpha_vs_beta()
#   perdidos_vs_alpha_vs_beta()


    parser = argparse.ArgumentParser(description='Hacer algunos experimentos.')
    parser.add_argument('--alpha', type=float, nargs='?', default=1./2)
    parser.add_argument('--beta', type=float, nargs='?', default=1./4)
    parser.add_argument('--size_burst', type=int, nargs='?', default=200)
    parser.add_argument('--delay_prop', type=float, nargs='?', default=2)
    parser.add_argument('--output', type=str, nargs='?', default='congestion.pdf')
    parser.add_argument('--ylim', type=int, nargs='?')
    args = parser.parse_args()

    congestion_subida(output = args.output, ylim = args.ylim, alpha = args.alpha, beta = args.beta, size_burst = args.size_burst, delay_inicial = 25, delay_final = 25 * args.delay_prop).run()

if __name__ == "__main__":
    main()
