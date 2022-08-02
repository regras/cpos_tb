#!/usr/bin/env python

from __future__ import division
import sqldb
import os
import parameter
import math


def newReversion(round, lastround):
    return sqldb.insertReversion(round, lastround)


def addBlocksReversion(node, fblock, lblock, idreversion):
    blocks = sqldb.getBlockIntervalByRound(fblock.round, lblock.round)
    if os.path.isfile(fileName):
        results = open(fileName, "a")
    # else:
    #    results = open(fileName, 'a')
    #    results.write('################Analise Reversao longo alcance################\n')

    results.write("Numero de blocos revertidos: " + (str(len(blocks))) + "\n\n")

    for block in blocks:
        results.write(
            "indice do bloco revertido: "
            + str(block[1])
            + "\n"
            + "rodada do bloco revertido: "
            + str(block[2])
            + "\n"
            + "hash do bloco revertido: "
            + str(block[4])
            + "\n"
            + "rodada de confirmacao: "
            + str(block[14])
            + "\n"
        )

    results.write("#################################################\n")
    results.close()


def calcParameters(node, startSimulation, endSimulation, lastForks, numBlocks):
    blocks = sqldb.getBlocks(numBlocks)
    numForks = sqldb.dbNumForks() - len(lastForks)
    forks = sqldb.getForks(lastForks)
    numBlocks = sqldb.dbNumBlocks(numBlocks)
    # calculating fork duration in rounds
    avg = 0.0
    numBlocksFork = 0
    for fork in forks:
        forkQuery = forks[fork][0]
        print("forks to realize")
        print(forkQuery)
        ###store fork on the lastForks variable
        if lastForks:
            index = max(lastForks) + 1
        else:
            index = 0
        lastForks[index] = []
        lastForks[index].append(forkQuery)
        ###fork stored on lastForks variable
        startTime = forkQuery[3]
        if startTime != parameter.GEN_ARRIVE_TIME:
            endTime = forkQuery[4]
            r = int(math.floor((int(endTime) - int(startTime)) / parameter.timeout))
            avg = avg + r
            # calculating number of blocks
            startBlock = forkQuery[1]
            endBlock = forkQuery[2]
            numBlocksFork = numBlocksFork + ((int(endBlock) - int(startBlock)) + 1)
        else:
            numForks = numForks - 1
    if numForks:
        numBlocksFork = numBlocksFork / numForks
        avg = avg / numForks
    else:
        numBlocksFork = 0
        avg = 0

    timeSimulation = endSimulation - startSimulation

    # calculating the average interval between two blocks
    sumRounds = 0
    lastRound = 0
    avgRound = 0.0
    i = 0
    for block in blocks:
        roundBlock = block[2]
        if i > 0:
            sumRounds = sumRounds + (roundBlock - lastRound)

        lastRound = roundBlock
        i = i + 1
    if numBlocks:
        print("sumRounds")
        print(sumRounds)
        if numBlocks > 1:
            avgRound = sumRounds / (numBlocks - 1)
        else:
            avgRound = sumRounds / (numBlocks)
        print("avgRound")
        print(avgRound)
        # avgRound = roundBlock(avgRound,2)
    ipaddr = str(node.getNodeIp())
    countRound = node.getCountRound()

    fileName = "results_" + ipaddr + ".txt"
    if os.path.isfile(fileName):
        results = open(fileName, "a")
        results.write(
            "Numero de Forks:"
            + str(numForks)
            + "\n"
            + "Duracao media dos forks em rodadas:"
            + str(avg)
            + "\n"
            + "Duracao media dos forks em numero de blocks: "
            + str(numBlocksFork)
            + "\n"
            + "Tempo total da Simulacao:"
            + str(timeSimulation)
            + "\n"
            + "Numero de blocos na Simulacao:"
            + str(numBlocks)
            + "\n"
            + "Numero de rodadas media entre blocos:"
            + str(avgRound)
            + "\n"
            + "Numero de rodadas totais:"
            + str(countRound)
            + "\n"
            + "\n"
        )
    else:
        results = open(fileName, "a")
        results.write(
            "################Analise Forks e Rodadas Entre Blocos################\n"
            + "Numero de Forks:"
            + str(numForks)
            + "\n"
            + "Duracao media dos forks em rodadas:"
            + str(avg)
            + "\n"
            + "Duracao media dos forks em numero de blocks:"
            + str(numBlocksFork)
            + "\n"
            + "Tempo total da Simulacao:"
            + str(timeSimulation)
            + "\n"
            + "Numero de blocos na Simulacao:"
            + str(numBlocks)
            + "\n"
            + "Numero de rodadas media entre blocos:"
            + str(avgRound)
            + "\n"
            + "Numero de rodadas totais:"
            + str(countRound)
            + "\n"
            + "\n"
        )

    results.close()
    return lastForks, numBlocks
