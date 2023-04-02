#!/usr/bin/env python
import logging

#logging.basicConfig(filename = 'testenode.log',filemode ="w", level = logging.DEBUG, format =" %(asctime)s - %(levelname)s - %(message)s")
def Combinations(m,n):
      # calcula o fatorial de m
    k = m
    k_fat = 1
    cont = 1
    while cont < k:
        cont += 1      
        k_fat *= cont  

    m_fatorial = k_fat
    # calcula o fatorial de n
    k = n
    k_fat = 1
    cont = 1
    while cont < k:
        cont += 1       
        k_fat *= cont   

    n_fatorial = k_fat
    # calcula o fatorial de m - n
    k = m-n
    k_fat = 1
    cont = 1
    while cont < k:
        cont += 1       
        k_fat *= cont   

    mn_fatorial = k_fat

    return (m_fatorial/(mn_fatorial * n_fatorial))

######################################
n = 3
f = 0.1
while(f <= 0.5):
    prob = 0
    for m in range(0, n + 1):
        logging.debug("OK")
        prob = prob + Combinations(m+n-1,m)*(((f**m * (1-f)**n) - (f**n * (1-f)**m)))
    logging.debug("f: "+str(f))
    logging.info("Prob. double spending: "+str(1 - prob))
    f = f + float(1) / 10