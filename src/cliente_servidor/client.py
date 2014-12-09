#Tampoco vi que hayan estimado el RTT real, lo cual es importante para contrastar con lo encontradi -*- coding: utf-8 -*-

try:
    from ptc import Socket, SHUT_WR
    from ptc.exceptions import PTCError
except:
    import sys
    sys.path.append('../catedra/')
    from ptc import Socket, SHUT_WR
    from ptc.exceptions import PTCError



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
        while not client_sock.is_connected():
            client_sock.connect((SERVER_IP, SERVER_PORT), timeout=15)

            if not client_sock.is_connected():
                client_sock.close()
                client_sock = Socket(a, b, p, d, verbose)
    
        for i in xrange(n):
            done = False
            if i % 100 == 0:
                print ("Sending package number {}".format(i))
            while not done:
                try:
                    client_sock.send(to_send)
                    # time.sleep(.001)
                    done = True
                except PTCError as e:
                    # The server was disconnected.
                    # Wait for the user to reset it.
                    print("The server seems to be down!")
                    import ipdb
                    ipdb.set_trace()

        rto, rtt = client_sock.alumnos_print_rto()
        perdidos = client_sock.alumnos_get_retransmitions()

        #El ultimo mensaje tiene que llegar si o si
        client_sock.alumnos_change_proba(0.0)

        time.sleep(1)
        client_sock.send(end)
        time.sleep(1)
        
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

class perdidos_vs_alpha_vs_beta:
    def __init__(self, paquetes=300, times=1, verbose=True, output='ret_colormap.pdf'):
        self.verbose = verbose
        self.output = output
        self.paquetes = paquetes
        self.times = times

    def run(self): 
        if self.verbose:
            print "ALPHA, BETA VS RTO"

        self.arr_alpha = [x * 0.2 for x in range(0, 6)]
        self.arr_beta = [x * 0.2 for x in range (0, 6)]
        lalpha = len(self.arr_alpha)
        lbetas = len(self.arr_beta)
        self.resus = [ [0. for i in xrange(lalpha)] for j in xrange(lbetas)]

        for a in self.arr_alpha:
            for b in self.arr_beta:
                cliente = {'alpha':a, 'beta':b, 'proba':0.0, 'delay':25.0}

                cantidades = []
                for i in xrange(self.times):
                    _, _, cant = conectar_server(cliente, self.paquetes)
                    cantidades += [cant]
        
                cant = cantidades[int(self.times) / 2]
                if self.verbose:
                    print('alpha = {}, beta = {}: {}'.format(a, b, cant))

                self.resus[lalpha-1-i][j] = cant

        self.write_report()

    def write_report(self):
        pylab.xticks(xrange(len(self.arr_beta)), self.arr_beta)
        pylab.yticks(xrange(len(self.arr_alpha)), [x for x in reversed(self.arr_alpha)])
        pylab.imshow(self.resus, interpolation='nearest')
        pylab.colorbar()
        pylab.xlabel(r'$\beta$')
        pylab.ylabel(r'$\alpha$')
        pylab.title (r'Retransmisiones para $\alpha$ y $\beta$')
        pylab.tight_layout()
        pylab.savefig(self.output, format='pdf', orientation='landscape')
        pylab.clf()

class congestion_subida:
    def __init__(self, alpha=0, beta=0, delay_inicial=25, proba=0, delay_final=50, verbose=True, size_burst=150, output = 'congestion.pdf', ylim = None, delays = None):
        self.rtos = []
        self.rtts = []

        self.alpha = alpha
        self.beta = beta
        self.proba = proba
        self.verbose = verbose
        self.size_burst = size_burst
        self.output = output
        self.ylim = ylim

        if delays:
            self.delays = delays
        else:
            self.delays = [delay_inicial, delay_final]

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
        print self.delays
        with Socket(self.alpha, self.beta, self.proba, 0, self.verbose) as self.client_sock:
            self.client_sock.connect((SERVER_IP, SERVER_PORT), timeout=5)

            for period in self.delays:
                self.client_sock.alumnos_change_delay(period)
                if self.verbose:
                    print('\nCalculando todo con delay = {}'.format(period))
                self.burst(times = self.size_burst)
                self.client_sock.alumnos_print_rto()
                
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

        if len(self.delays) == 2:
            pylab.title ('RTO vs Numero de Paquetes ($^{{d_0}}/_{{d_f}} = {}$)'.format(self.delays[0] * 1. / self.delays[1]))
        else:
            pylab.title ('RTO vs Numero de Paquetes')
                
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
    parser.add_argument('--output', type=str, nargs='?')
    parser.add_argument('--ylim', type=int, nargs='?')
    parser.add_argument('--delays', type=int, nargs='*')
    parser.add_argument('--paquetes', type=int, nargs='?')
    parser.add_argument('program', type=str, nargs=1)
    args = parser.parse_args()

    if args.program[0] == 'perdidos':
        if args.output is None:
            args.output = 'perdidos.pdf'

        perdidos_vs_alpha_vs_beta(paquetes = args.paquetes, output=args.output).run()
    elif args.program[0] == 'congestion':
        if args.output is None:
            args.output = 'congestion.pdf'

        congestion_subida(output = args.output, ylim = args.ylim, alpha = args.alpha, beta = args.beta, size_burst = args.size_burst, delay_inicial = 25, delay_final = 25 * args.delay_prop, delays=args.delays).run()
    else:
        print (parser.format_usage())
        sys.exit(1)

if __name__ == "__main__":
    main()
