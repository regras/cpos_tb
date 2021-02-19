import math
import random
import time
import datetime
import hashlib
import chaincontrol
# -*- coding: utf-8 -*-
def structCommitted(tau,epsilon):
    committed = {}
    sync_threshold = {}
    deltar = 2
    if(tau == 100):
        if epsilon == 0.00000001:
            committed[deltar] = 81
            committed[deltar + 1] = 72
            committed[deltar + 2] = 72
            committed[deltar + 3] = 72
            committed[deltar + 4] = 72
            committed[deltar + 5] = 72
            committed[deltar + 6] = 72
            committed[deltar + 7] = 72
            committed[deltar + 8] = 72
        elif epsilon == 0.000001:
            committed[deltar] = 76
            committed[deltar + 1] = 68
            committed[deltar + 2] = 68
            committed[deltar + 3] = 68
            committed[deltar + 4] = 68
            committed[deltar + 5] = 68
            committed[deltar + 6] = 68
            committed[deltar + 7] = 68
            committed[deltar + 8] = 68 
        #elif epsilon == 0.0001:
        #    committed[deltar] = 54
        #    committed[deltar + 1] = 60
        #    committed[deltar + 2] = 54
        #    committed[deltar + 3] = 54
        #    committed[deltar + 4] = 54
        #    committed[deltar + 5] = 54
        #    committed[deltar + 6] = 54
        #    committed[deltar + 7] = 54
        #    committed[deltar + 8] = 54
        else:
            print("epsilon error!")
        sync_threshold[deltar] = 84
        sync_threshold[deltar + 1] = 89
        sync_threshold[deltar + 2] = 89
        sync_threshold[deltar + 3] = 89
        sync_threshold[deltar + 4] = 89
        sync_threshold[deltar + 5] = 89
    if(tau == 82):
        if epsilon == 0.00000001:
            committed[deltar] = 69
            committed[deltar + 1] = 62
            committed[deltar + 2] = 62
            committed[deltar + 3] = 62
            committed[deltar + 4] = 62
            committed[deltar + 5] = 62
            committed[deltar + 6] = 62
            committed[deltar + 7] = 62
            committed[deltar + 8] = 62
        elif epsilon == 0.000001:
            committed[deltar] = 59
            committed[deltar + 1] = 65
            committed[deltar + 2] = 58
            committed[deltar + 3] = 58
            committed[deltar + 4] = 58
            committed[deltar + 5] = 58
            committed[deltar + 6] = 58
            committed[deltar + 7] = 58
            committed[deltar + 8] = 58 
        elif epsilon == 0.0001:
            committed[deltar] = 54
            committed[deltar + 1] = 60
            committed[deltar + 2] = 54
            committed[deltar + 3] = 54
            committed[deltar + 4] = 54
            committed[deltar + 5] = 54
            committed[deltar + 6] = 54
            committed[deltar + 7] = 54
            committed[deltar + 8] = 54
        else:
            print("epsilon error!")
        sync_threshold[deltar] = 68
        sync_threshold[deltar + 1] = 71
        sync_threshold[deltar + 2] = 71
        sync_threshold[deltar + 3] = 71
        sync_threshold[deltar + 4] = 71
        sync_threshold[deltar + 5] = 71

    if(tau == 73):
        if epsilon == 0.00000001:
            committed[deltar] = 63
            committed[deltar + 1] = 55
            committed[deltar + 2] = 55
            committed[deltar + 3] = 55
            committed[deltar + 4] = 55
            committed[deltar + 5] = 55
            committed[deltar + 6] = 55
            committed[deltar + 7] = 55
            committed[deltar + 8] = 55
        elif epsilon == 0.000001:
            committed[deltar] = 59
            committed[deltar + 1] = 52
            committed[deltar + 2] = 52
            committed[deltar + 3] = 52
            committed[deltar + 4] = 52
            committed[deltar + 5] = 52
            committed[deltar + 6] = 52
            committed[deltar + 7] = 52
            committed[deltar + 8] = 52 
        elif epsilon == 0.0001:
            committed[deltar] = 54
            committed[deltar + 1] = 49
            committed[deltar + 2] = 49
            committed[deltar + 3] = 49
            committed[deltar + 4] = 49
            committed[deltar + 5] = 49
            committed[deltar + 6] = 49
            committed[deltar + 7] = 49
            committed[deltar + 8] = 49
        else:
            print("epsilon error!")
        
        sync_threshold[deltar] = 59
        sync_threshold[deltar + 1] = 63
        sync_threshold[deltar + 2] = 63
        sync_threshold[deltar + 3] = 63
        sync_threshold[deltar + 4] = 63
        sync_threshold[deltar + 5] = 63
    if(tau == 64):
        if epsilon == 0.00000001:
            committed[deltar] = 57
            committed[deltar + 1] = 50
            committed[deltar + 2] = 50
            committed[deltar + 3] = 50
            committed[deltar + 4] = 50
            committed[deltar + 5] = 50
            committed[deltar + 6] = 50
            committed[deltar + 7] = 50
            committed[deltar + 8] = 50
        elif epsilon == 0.000001:
            committed[deltar] = 53
            committed[deltar + 1] = 47
            committed[deltar + 2] = 47
            committed[deltar + 3] = 47
            committed[deltar + 4] = 47
            committed[deltar + 5] = 47
            committed[deltar + 6] = 47
            committed[deltar + 7] = 47
            committed[deltar + 8] = 47 
        elif epsilon == 0.0001:
            committed[deltar] = 48
            committed[deltar + 1] = 44
            committed[deltar + 2] = 44
            committed[deltar + 3] = 44
            committed[deltar + 4] = 44
            committed[deltar + 5] = 44
            committed[deltar + 6] = 44
            committed[deltar + 7] = 44
            committed[deltar + 8] = 44
        else:
            print("epsilon error!")

        sync_threshold[deltar] = 51
        sync_threshold[deltar + 1] = 55
        sync_threshold[deltar + 2] = 55
        sync_threshold[deltar + 3] = 55
        sync_threshold[deltar + 4] = 55
        sync_threshold[deltar + 5] = 55

    if(tau == 55):
        if epsilon == 0.00000001:
            committed[deltar] = 51
            committed[deltar + 1] = 44
            committed[deltar + 2] = 44
            committed[deltar + 3] = 44
            committed[deltar + 4] = 44
            committed[deltar + 5] = 44
            committed[deltar + 6] = 44
            committed[deltar + 7] = 44
            committed[deltar + 8] = 44
        elif epsilon == 0.000001:
            committed[deltar] = 47
            committed[deltar + 1] = 41
            committed[deltar + 2] = 41
            committed[deltar + 3] = 41
            committed[deltar + 4] = 41
            committed[deltar + 5] = 41
            committed[deltar + 6] = 41
            committed[deltar + 7] = 41
            committed[deltar + 8] = 41 
        elif epsilon == 0.0001:
            committed[deltar] = 42
            committed[deltar + 1] = 38
            committed[deltar + 2] = 38
            committed[deltar + 3] = 38
            committed[deltar + 4] = 38
            committed[deltar + 5] = 38
            committed[deltar + 6] = 38
            committed[deltar + 7] = 38
            committed[deltar + 8] = 38
        else:
            print("epsilon error!")

        sync_threshold[deltar] = 43
        sync_threshold[deltar + 1] = 46
        sync_threshold[deltar + 2] = 46
        sync_threshold[deltar + 3] = 46
        sync_threshold[deltar + 4] = 46
        sync_threshold[deltar + 5] = 46

    if(tau == 46):
        if epsilon == 0.00000001:
            committed[deltar] = 45
            committed[deltar + 1] = 38
            committed[deltar + 2] = 35
            committed[deltar + 3] = 35
            committed[deltar + 4] = 35
            committed[deltar + 5] = 35
            committed[deltar + 6] = 35
            committed[deltar + 7] = 35
            committed[deltar + 8] = 35
        elif epsilon == 0.000001:
            committed[deltar] = 41
            committed[deltar + 1] = 36
            committed[deltar + 2] = 33
            committed[deltar + 3] = 33
            committed[deltar + 4] = 33
            committed[deltar + 5] = 33
            committed[deltar + 6] = 33
            committed[deltar + 7] = 33
            committed[deltar + 8] = 33 
        elif epsilon == 0.0001:
            committed[deltar] = 37
            committed[deltar + 1] = 33
            committed[deltar + 2] = 33
            committed[deltar + 3] = 33
            committed[deltar + 4] = 33
            committed[deltar + 5] = 33
            committed[deltar + 6] = 33
            committed[deltar + 7] = 33
            committed[deltar + 8] = 33
        else:
            print("epsilon error!")
        sync_threshold[deltar] = 35
        sync_threshold[deltar + 1] = 38
        sync_threshold[deltar + 2] = 38
        sync_threshold[deltar + 3] = 38
        sync_threshold[deltar + 4] = 38
        sync_threshold[deltar + 5] = 38

    if(tau == 37):
        if epsilon == 0.00000001:
            committed[deltar] = 39
            committed[deltar + 1] = 32
            committed[deltar + 2] = 30
            committed[deltar + 3] = 30
            committed[deltar + 4] = 30
            committed[deltar + 5] = 30
            committed[deltar + 6] = 30
            committed[deltar + 7] = 30
            committed[deltar + 8] = 30
        elif epsilon == 0.000001:
            committed[deltar] = 35
            committed[deltar + 1] = 30
            committed[deltar + 2] = 28
            committed[deltar + 3] = 28
            committed[deltar + 4] = 28
            committed[deltar + 5] = 28
            committed[deltar + 6] = 28
            committed[deltar + 7] = 28
            committed[deltar + 8] = 28 
        elif epsilon == 0.0001:
            committed[deltar] = 31
            committed[deltar + 1] = 27
            committed[deltar + 2] = 27
            committed[deltar + 3] = 27
            committed[deltar + 4] = 27
            committed[deltar + 5] = 27
            committed[deltar + 6] = 27
            committed[deltar + 7] = 27
            committed[deltar + 8] = 27
        else:
            print("epsilon error!")
        sync_threshold[deltar] = 27
        sync_threshold[deltar + 1] = 30
        sync_threshold[deltar + 2] = 30
        sync_threshold[deltar + 3] = 30
        sync_threshold[deltar + 4] = 30
        sync_threshold[deltar + 5] = 30
    if(tau == 31):
        if epsilon == 0.00000001:
            committed[deltar] = 34
            committed[deltar + 1] = 28
            committed[deltar + 2] = 26
            committed[deltar + 3] = 26
            committed[deltar + 4] = 26
            committed[deltar + 5] = 26
            committed[deltar + 6] = 26
            committed[deltar + 7] = 26
            committed[deltar + 8] = 26
        elif epsilon == 0.000001:
            committed[deltar] = 31
            committed[deltar + 1] = 26
            committed[deltar + 2] = 24
            committed[deltar + 3] = 24
            committed[deltar + 4] = 24
            committed[deltar + 5] = 24
            committed[deltar + 6] = 24
            committed[deltar + 7] = 24
            committed[deltar + 8] = 24 
        elif epsilon == 0.0001:
            committed[deltar] = 27
            committed[deltar + 1] = 24
            committed[deltar + 2] = 22
            committed[deltar + 3] = 21
            committed[deltar + 4] = 21
            committed[deltar + 5] = 20
            committed[deltar + 6] = 20
            committed[deltar + 7] = 20
            committed[deltar + 8] = 20
        else:
            print("epsilon error!")
        
        sync_threshold[deltar] = 22
        sync_threshold[deltar + 1] = 25
        sync_threshold[deltar + 2] = 25
        sync_threshold[deltar + 3] = 25
        sync_threshold[deltar + 4] = 25
        sync_threshold[deltar + 5] = 25
    if(tau == 28):
        if epsilon == 0.00000001:
            committed[deltar] = 32
            committed[deltar + 1] = 26
            committed[deltar + 2] = 24
            committed[deltar + 3] = 24
            committed[deltar + 4] = 24
            committed[deltar + 5] = 14
            committed[deltar + 6] = 14
            committed[deltar + 7] = 24
            committed[deltar + 8] = 24
        elif epsilon == 0.000001:
            committed[deltar] = 29
            committed[deltar + 1] = 24
            committed[deltar + 2] = 22
            committed[deltar + 3] = 22
            committed[deltar + 4] = 22
            committed[deltar + 5] = 22
            committed[deltar + 6] = 22
            committed[deltar + 7] = 22
            committed[deltar + 8] = 22 
        elif epsilon == 0.0001:
            committed[deltar] = 25
            committed[deltar + 1] = 22
            committed[deltar + 2] = 20
            committed[deltar + 3] = 20
            committed[deltar + 4] = 19
            committed[deltar + 5] = 19
            committed[deltar + 6] = 18
            committed[deltar + 7] = 18
            committed[deltar + 8] = 18
        else:
            print("epsilon error!")

        sync_threshold[deltar] = 20
        sync_threshold[deltar + 1] = 22
        sync_threshold[deltar + 2] = 22
        sync_threshold[deltar + 3] = 22
        sync_threshold[deltar + 4] = 22
        sync_threshold[deltar + 5] = 22
    if(tau == 25):
        if epsilon == 0.00000001:
            committed[deltar] = 30
            committed[deltar + 1] = 24
            committed[deltar + 2] = 22
            committed[deltar + 3] = 21
            committed[deltar + 4] = 20
            committed[deltar + 5] = 19
            committed[deltar + 6] = 19
            committed[deltar + 7] = 18
            committed[deltar + 8] = 18

        elif epsilon == 0.000001:
            committed[deltar] = 27
            committed[deltar + 1] = 22
            committed[deltar + 2] = 20
            committed[deltar + 3] = 19
            committed[deltar + 4] = 19
            committed[deltar + 5] = 18
            committed[deltar + 6] = 18
            committed[deltar + 7] = 18
            committed[deltar + 8] = 18

        elif epsilon == 0.0001:
            committed[deltar] = 24
            committed[deltar + 1] = 20
            committed[deltar + 2] = 19
            committed[deltar + 3] = 18
            committed[deltar + 4] = 17
            committed[deltar + 5] = 17
            committed[deltar + 6] = 17
            committed[deltar + 7] = 17
            committed[deltar + 8] = 17
        else:
            print("epsilon error!")

        sync_threshold[deltar] = 17
        sync_threshold[deltar + 1] = 19
        sync_threshold[deltar + 2] = 19
        sync_threshold[deltar + 3] = 19
        sync_threshold[deltar + 4] = 19
        sync_threshold[deltar + 5] = 19

    if(tau == 19):
        if epsilon == 0.00000001:
            committed[deltar] = 25
            committed[deltar + 1] = 20
            committed[deltar + 2] = 18
            committed[deltar + 3] = 17
            committed[deltar + 4] = 16
            committed[deltar + 5] = 15
            committed[deltar + 6] = 15
            committed[deltar + 7] = 15
            committed[deltar + 8] = 15

        elif epsilon == 0.000001:
            committed[deltar] = 22
            committed[deltar + 1] = 18
            committed[deltar + 2] = 17
            committed[deltar + 3] = 16
            committed[deltar + 4] = 15
            committed[deltar + 5] = 15
            committed[deltar + 6] = 14
            committed[deltar + 7] = 14
            committed[deltar + 8] = 14

        elif epsilon == 0.0001:
            committed[deltar] = 19
            committed[deltar + 1] = 16
            committed[deltar + 2] = 15
            committed[deltar + 3] = 14
            committed[deltar + 4] = 14
            committed[deltar + 5] = 14
            committed[deltar + 6] = 14
            committed[deltar + 7] = 14
            committed[deltar + 8] = 13
        else:
            print("epsilon error!")

        sync_threshold[deltar] = 12
        sync_threshold[deltar + 1] = 13
        sync_threshold[deltar + 2] = 13
        sync_threshold[deltar + 3] = 14
        sync_threshold[deltar + 4] = 14
        sync_threshold[deltar + 5] = 14

    if(tau == 16):
        if epsilon == 0.00000001:
            committed[deltar] = 22
            committed[deltar + 1] = 18
            committed[deltar + 2] = 16
            committed[deltar + 3] = 15
            committed[deltar + 4] = 14
            committed[deltar + 5] = 14
            committed[deltar + 6] = 14
            committed[deltar + 7] = 13
            committed[deltar + 8] = 13

        elif epsilon == 0.000001:
            committed[deltar] = 20
            committed[deltar + 1] = 16
            committed[deltar + 2] = 15
            committed[deltar + 3] = 14
            committed[deltar + 4] = 13
            committed[deltar + 5] = 13
            committed[deltar + 6] = 12
            committed[deltar + 7] = 12
            committed[deltar + 8] = 12

        elif epsilon == 0.0001:
            committed[deltar] = 17
            committed[deltar + 1] = 14
            committed[deltar + 2] = 13
            committed[deltar + 3] = 13
            committed[deltar + 4] = 12
            committed[deltar + 5] = 12
            committed[deltar + 6] = 11
            committed[deltar + 7] = 11
            committed[deltar + 8] = 11
        else:
            print("epsilon error!")

        sync_threshold[deltar] = 10
        sync_threshold[deltar + 1] = 11
        sync_threshold[deltar + 2] = 12
        sync_threshold[deltar + 3] = 13
        sync_threshold[deltar + 4] = 13
        sync_threshold[deltar + 5] = 13

    if(tau == 13):
        if epsilon == 0.00000001:
            committed[deltar] = 20
            committed[deltar + 1] = 15
            committed[deltar + 2] = 14
            committed[deltar + 3] = 13
            committed[deltar + 4] = 12
            committed[deltar + 5] = 12
            committed[deltar + 6] = 11
            committed[deltar + 7] = 11
            committed[deltar + 8] = 11

        elif epsilon == 0.000001:
            committed[deltar] = 17
            committed[deltar + 1] = 14
            committed[deltar + 2] = 13
            committed[deltar + 3] = 12
            committed[deltar + 4] = 11
            committed[deltar + 5] = 11
            committed[deltar + 6] = 11
            committed[deltar + 7] = 10
            committed[deltar + 8] = 10

        elif epsilon == 0.0001:
            committed[deltar] = 15
            committed[deltar + 1] = 12
            committed[deltar + 2] = 11
            committed[deltar + 3] = 10
            committed[deltar + 4] = 10
            committed[deltar + 5] = 10
            committed[deltar + 6] = 10
            committed[deltar + 7] = 10
            committed[deltar + 8] = 10
        else:
            print("epsilon error!")

        sync_threshold[deltar] = 8
        sync_threshold[deltar + 1] = 9
        sync_threshold[deltar + 2] = 10
        sync_threshold[deltar + 3] = 10
        sync_threshold[deltar + 4] = 10
        sync_threshold[deltar + 5] = 10

    if(tau == 10):
        if epsilon == 0.00000001:
            committed[deltar] = 17
            committed[deltar + 1] = 13
            committed[deltar + 2] = 11
            committed[deltar + 3] = 11
            committed[deltar + 4] = 10
            committed[deltar + 5] = 10
            committed[deltar + 6] = 9
            committed[deltar + 7] = 9
            committed[deltar + 8] = 9

        elif epsilon == 0.000001:
            committed[deltar] = 15
            committed[deltar + 1] = 12
            committed[deltar + 2] = 10
            committed[deltar + 3] = 10
            committed[deltar + 4] = 9
            committed[deltar + 5] = 9
            committed[deltar + 6] = 8
            committed[deltar + 7] = 8
            committed[deltar + 8] = 7
        elif epsilon == 0.0001:
            committed[deltar] = 13
            committed[deltar + 1] = 10
            committed[deltar + 2] = 9
            committed[deltar + 3] = 9
            committed[deltar + 4] = 8
            committed[deltar + 5] = 7
            committed[deltar + 6] = 7
            committed[deltar + 7] = 7
            committed[deltar + 8] = 7
        else:
            print("epsilon error!")

        sync_threshold[deltar] = 5
        sync_threshold[deltar + 1] = 6
        sync_threshold[deltar + 2] = 7
        sync_threshold[deltar + 3] = 7
        sync_threshold[deltar + 4] = 7
        sync_threshold[deltar + 5] = 7 
        
    elif(tau == 7):
        if epsilon == 0.00000001:
            committed[deltar] = 14
            committed[deltar + 1] = 11
            committed[deltar + 2] = 9
            committed[deltar + 3] = 8
            committed[deltar + 4] = 8
            committed[deltar + 5] = 7
            committed[deltar + 6] = 7
            committed[deltar + 7] = 7
            committed[deltar + 8] = 6            

        elif epsilon == 0.000001:
            committed[deltar] = 12
            committed[deltar + 1] = 9
            committed[deltar + 2] = 8
            committed[deltar + 3] = 8
            committed[deltar + 4] = 7
            committed[deltar + 5] = 6
            committed[deltar + 6] = 6
            committed[deltar + 7] = 6
            committed[deltar + 8] = 6
            
        elif epsilon == 0.0001:
            committed[deltar] = 10
            committed[deltar + 1] = 8
            committed[deltar + 2] = 7
            committed[deltar + 3] = 7
            committed[deltar + 4] = 6
            committed[deltar + 5] = 6
            committed[deltar + 6] = 6
            committed[deltar + 7] = 6
            committed[deltar + 8] = 6
            committed[deltar + 9] = 6
            committed[deltar + 10] = 6
        else:
            print("epsilon error!")

        sync_threshold[deltar] = 3
        sync_threshold[deltar + 1] = 4
        sync_threshold[deltar + 2] = 4
        sync_threshold[deltar + 3] = 4
        sync_threshold[deltar + 4] = 5
        sync_threshold[deltar + 5] = 5 

    elif(tau == 4):
        if epsilon == 0.00000001:
            committed[deltar] = 11
            committed[deltar + 1] = 8
            committed[deltar + 2] = 7
            committed[deltar + 3] = 6
            committed[deltar + 4] = 6
            committed[deltar + 5] = 5
            committed[deltar + 6] = 5
            committed[deltar + 7] = 5
            committed[deltar + 8] = 5
            committed[deltar + 9] = 4
            committed[deltar + 10] = 4
            committed[deltar + 11] = 4
            committed[deltar + 12] = 4
            committed[deltar + 13] = 4
            committed[deltar + 14] = 4
            committed[deltar + 15] = 4
            committed[deltar + 16] = 4
            committed[deltar + 17] = 4
            committed[deltar + 18] = 4
            committed[deltar + 19] = 4
            committed[deltar + 20] = 3

        elif epsilon == 0.000001:
            committed[deltar] = 9
            committed[deltar + 1] = 7
            committed[deltar + 2] = 6
            committed[deltar + 3] = 5
            committed[deltar + 4] = 5
            committed[deltar + 5] = 5
            committed[deltar + 6] = 5
            committed[deltar + 7] = 4
            committed[deltar + 8] = 4
            committed[deltar + 9] = 4
            committed[deltar + 10] = 4 
            committed[deltar + 11] = 4 
            committed[deltar + 12] = 4 
            committed[deltar + 13] = 4 
            committed[deltar + 14] = 4 
            committed[deltar + 15] = 4 
            committed[deltar + 16] = 4 
            committed[deltar + 17] = 3 
            
        elif epsilon == 0.0001:
            committed[deltar] = 7
            committed[deltar + 1] = 6
            committed[deltar + 2] = 5
            committed[deltar + 3] = 5
            committed[deltar + 4] = 4
            committed[deltar + 5] = 4
            committed[deltar + 6] = 4
            committed[deltar + 7] = 3
            committed[deltar + 8] = 3
        else:
            print("epsilon error!")
        ##sync threshold##
        sync_threshold[deltar] = 1
        sync_threshold[deltar + 1] = 1
        sync_threshold[deltar + 2] = 2
        sync_threshold[deltar + 3] = 2
        sync_threshold[deltar + 4] = 2
        sync_threshold[deltar + 5] = 2 
        
    return committed,sync_threshold

def TrustandPeers():
    #trust nodes
    trusted = []
    exp=8
    num = 2**exp - 1
    cont = 0
    while(num <= trust):
        cont = cont+1
        exp=exp+1
        num = 2**exp - 2 ** (cont)

    contIPs = 0
    for i in range(0,cont+2):
        if i == 0:
            first = 2
        else:
            first = 0
        for j in range(first,256):            
            trusted=trusted+['10.1'+str(i)+'.'+str(j)]
            contIPs=contIPs+1
            if(contIPs == trust):
                break
        if(contIPs==trust):
            break
    #print trusted

    #define all IPs peers
    peers = []
    exp=8
    num = 2**exp - 1
    cont = 0
    while(num <= nodes):
        cont = cont+1
        exp=exp+1
        num = 2**exp - 2 ** (cont)

    contIPs = 0
    #print cont
    for i in range(0,cont+2):
        if i == 0:
            first = 2
        else:
            first = 0
        for j in range(first,256):
            #if (i != 1) or (i == 1 and j < 146 or j > 165):
            peers=peers+['10.1.'+str(i)+'.'+str(j)]
            contIPs=contIPs+1
            if(contIPs == nodes):
                break
        if(contIPs==nodes):
            break
    #print peers
    return trusted,peers

def comb(tal,w):
    combi = {}
    for k in range(0,tal+201):
        index = "("+str(w)+","+str(k)+")"
        combi[index] = chaincontrol.Combinations(w,k)
    return combi

def firstCoinsValue():
    values = []
    with open("firstblocks") as file:
        for line in file:          
            values = values + [line]
    return values

def bPayload():
    values = None
    file = open('tx.txt', mode='r')
    values = file.read()
    file.close()
    return values
    
def defineStake(W):
    #mode = 1 (Aleatorio)
    #mode = 2 (x% do stake concentrado com y% dos participantes)
    #mode = 3 (stake dividido igualmente entre os participantes)
    #mode = 4 (stake concentrado em apenas um participante)
    #mode = 5 (x% do stake concentrado com y% dos participantes e distribuicao igual do stake)
    numStake = {}
    i = 1
    rate = {}
    rate[4] = [0.10,0.90]
    rate[5] = [0.10,0.70]
    rate[6] = [0.10,0.50]
    rate[7] = [0.50,0.90]
    rate[8] = [0.50,0.70]
    rate[9] = [0.50,0.50]
    rate[10] = [0.10,0.90]
    rate[11] = [0.10,0.70]
    rate[12] = [0.10,0.50]
    rate[13] = [0.50,0.90]
    rate[14] = [0.50,0.70]
    while(i == 1):
        #print(nodes)
        if((i >= 2 and i <=3) or i == 16):
            stakeTotal = W - nodes
            stake = random.randint(0,stakeTotal) + 1
            numStake[i] = {}
            j = 1
            for ip in peers:
                h = hashlib.sha256(str(ip)).hexdigest()
                if(j == nodes):
                    numStake[i][h] = [stakeTotal + 1]
                else:
                    numStake[i][h] = [stake]
                stakeTotal = stakeTotal - (stake - 1)
                stake = random.randint(0,stakeTotal) + 1 
                j = j + 1
                                
        elif(i > 3 and i <= 9):
            con = rate[i][0]
            stakeCon = rate[i][1]
            numNodesCon = int(math.floor(con * nodes))
            restNodes = nodes - numNodesCon
            if(numNodesCon > 0):
                stake1 = int(math.floor(stakeCon*(W)))
                stake2 = (W - stake1) - restNodes
                stake1 = stake1 - numNodesCon
            else:
                stake1 = 0
                stake2 = W - nodes
            numStake[i] = {}
            for ip in peers:
                h = hashlib.sha256(str(ip)).hexdigest()            
                if(h <= numNodesCon):
                    if(h == numNodesCon):
                        numStake[i][h] = [stake1 + 1]
                    else:
                        stake = random.randint(0,stake1) + 1
                        numStake[i][h] = [stake]
                        stake1 = stake1 - (stake - 1)
                else:
                    #print(stake2)
                    if(h == nodes):
                        numStake[i][h] = [stake2 + 1]
                    else:
                        stake = random.randint(0,stake2) + 1
                        numStake[i][h] = [stake]
                        stake2 = stake2 - (stake - 1)                
                #print(numStake)    
        
        elif(i > 9 and i <= 14):
            con = rate[i][0]
            stakeCon = rate[i][1]
            numNodesCon = int(math.floor(con * nodes))
            restNodes = nodes - numNodesCon
            if(numNodesCon > 0):
                stake1 = int(math.floor(stakeCon*(W)))
                stake2 = (W - stake1)
                flag1 = stake1 % numNodesCon
                flag2 = stake2 % restNodes
                stake1 = int(math.floor(float(stake1) / numNodesCon))
                stake2 = int(math.floor(float(stake2) / restNodes))
            else:
                stake1 = 0
                stake2 = W - nodes
            numStake[i] = {}
            j = 1
            for ip in peers:
                h = hashlib.sha256(str(ip)).hexdigest()
                
                if(j <= numNodesCon):
                    if(h == 1):
                        numStake[i][h] = [stake1 + flag1]
                    else:
                        numStake[i][h] = [stake1]
                else:
                    if(h == numNodesCon + 1):
                        numStake[i][h] = [stake2 + flag2]
                    else:
                        numStake[i][h] = [stake2]
                j = j + 1
            #print(numStake) 
        elif(i == 15):
            stake = W - (nodes - 3000)
            numStake[i] = {}
            j = 0
            for ip in peers:
                h = hashlib.sha256(str(ip)).hexdigest()            
                if(j == 0):
                    numStake[i][h] = [stake]
                else:
                    numStake[i][h] = [3000]
                j = j + 1

        elif(i == 1):
            stake = hW / nodes
            numStake[i] = {}
            for ip in peers:
                h = hashlib.sha256(str(ip)).hexdigest()            
                numStake[i][h] = [stake]

        i = i + 1
    return numStake

# Initial Arrive Time
GEN_ARRIVE_TIME = 1573486728
#GEN_ARRIVE_TIME = time.mktime(datetime.datetime.now().timetuple())
# Threshold that the blockchain can grown and accept one previous block with the best round.
THRESHOLD = 2

# Time in seconds
timeout = 90
#phase1 = timeout * (float(1)/2)
phase1 = 45
phase2 = 45
#phase2 = timeout / float((float(2)/3))
#phase2 = timeout * (float(1)/2)
# difficulty

### Test Variables ###
num_block_created = 0
test_num_nodes = 10

HASH_FIRST_TRANSACTION = hashlib.sha256(str('PPoS the best distribution consensus of the world')).hexdigest()

FIRST_HASH = "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b"

AVG_LATENCY = [24,24,24,24,24,24,24,24,24,24]

#TOLERANCY = timeout * 1.4

roundTolerancy = 0 #stable round tolerance

tol = 2 #round tolerance

round_buffer = 1 #round interval that a block can wait on the listen buffer

epsilon = 0.000001 #reversion prob.

TEST = 1800 #test time

W = 10000 #all network coins

q = 0  #attackers probability

hW = int(W * float(1 - q)) #honest coins

qW = int(W * float(q)) #dishonest coins

tal = 46 #proposer parameter

txround = 1000

difficulty = float(math.log(W,2) - math.log(tal,2)) 

nodes = 400 #num nodes
k = 3 #fraction of connected peers
trust = 2 #fraction of trust nodes
theta = 0.5 #threshold

sendblocks = 4 #in each round only sendblocks are transmitted


trusted,peers = TrustandPeers()
#defineNeighbors(peers)

#define distribution stake
numStake = defineStake(hW)
#numStake = {}
#numStake[1]

#some combinations
combination = comb(tal,hW)
combinations_conluio = comb(tal,qW)
        
#define first coins values
values = firstCoinsValue()

#block payload
pblock = bPayload()

#calc committed expected per round and sync_threshold
committed,sync_threshold = structCommitted(tal,epsilon)

lenblocks = [98,489,684,977,1465,1661,1954,2930,4883,7813]
