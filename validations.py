import consensus
import sqldb
import math
import parameter
import time
import datetime
from decimal import Decimal
import chaincontrol


def validateChallenge(block, stake):
    target = consensus.Consensus().target
    if int(block.hash, 16) < target:
        return True
    return False


def sortition(userHash, stake, cons):
    p = cons.getTarget() / float(2 ** 256)
    # p = 0.000125
    print("SUCCESS PROB: ", p)
    print("STAKE: ", stake)
    np = 1 - p
    q = int(userHash, 16) / float(2 ** 256)
    print("Q: ", q)
    j = 0

    limitInf = chaincontrol.Combinations(stake, 0) * ((np) ** (stake))
    limitSup = limitInf + chaincontrol.Combinations(stake, 1) * p * (np ** (stake - 1))

    # limitSup = limitInf + comb * p * (np**(stake - 1))
    print("LIMIT INF: ", limitInf)
    print("LIMIT SUP: ", limitSup)
    while q >= limitInf:
        j = j + 1
        limitInf = limitSup

        limitSup = limitSup + chaincontrol.Combinations(stake, j + 1) * (
            p ** (j + 1)
        ) * (np ** (stake - (j + 1)))
        # limitSup = limitSup + comb * (p**(j+1)) * (np**(stake - (j+1)))
        # print("limitSup: ", limitSup)
    print("RAFFLED NUMBER: ", j)
    return j


def validateProofHash(block, user_stake, cons):
    userHash, blockHash = cons.POS(
        lastBlock_hash=block.prev_hash, round=block.round, node=block.node, tx=block.tx
    )
    j = sortition(userHash, user_stake, cons)
    if j == block.subuser:
        proof_hash, subuser = cons.calcProofHash(userHash, blockHash, j)
        if int(proof_hash, 16) == int(block.proof_hash, 16):
            print("VERIFIED")
            return True, j
    return False, j


def validateRound(block, bc):
    chainBlock = bc.getLastBlock()
    if block.index > chainBlock.index and block.round > chainBlock.round:
        return True
    return False


def validateBlockHeader(block):
    # check block header
    if block.hash == block.calcBlockhash():
        return True
    return False


def validateBlock(block, lastBlock):
    # check block chaining
    if block.prev_hash == lastBlock.hash:
        return True
    return False


def blockPosition(block, bc, stake):
    # check if the block has a valid threshold
    chainPos, bcPos = validatePositionBlock(block, bc, stake)
    if chainPos:
        return True, bcPos
    else:
        return False, bc


def validatePositionBlock(block, bc, stake):
    i = 0
    while i < parameter.THRESHOLD:
        if len(bc.chain) > 1:
            bc.chain.pop()
        chainBlock = bc.getLastBlock()
        if (
            block.prev_hash == chainBlock.prev_hash
            and chainBlock.round > block.round
            and validateChallenge(block, stake)
        ):
            return True, bc
        i = i + 1
    return False, bc


def validateChain(bc, chain, stake):
    lastBlock = bc.getLastBlock()
    for b in chain:
        b = sqldb.dbtoBlock(b)
        if not validateBlockHeader(b):  # invalid
            # print("HEADER NOT OK")
            return b, True
        # print("lastblock index",lastBlock.index)
        # print("current block index", b.index)
        if validateBlock(b, lastBlock):
            # print("BLOCK OK")
            if (
                validateChallenge(b, stake)
                and validateRound(b, bc)
                and validateExpectedRound(b, lastBlock)
            ):
                print("BLOCO VALIDO SINCRONIZADO")
                lastBlock = b
                bc.addBlocktoBlockchain(b)
                sqldb.writeBlock(b)
                sqldb.writeChain(b)
        else:  # fork
            return b, False
    return None, False


def validateExpectedRound(block, lastBlock):
    calculated_rounds = (
        int(
            math.floor(
                (int(block.arrive_time) - int(lastBlock.arrive_time))
                / parameter.timeout
            )
        )
        + 1
    )
    expected_round = lastBlock.round + calculated_rounds
    if block.round >= expected_round - 1 and block.round <= expected_round + 1:
        # print("EXPECTED_ROUND", expected_round)
        return True
    else:
        return False


def validateExpectedLocalRound(block):
    nowTime = time.mktime(datetime.datetime.now().timetuple())
    expected_round = int(
        math.floor(
            (float(block.arrive_time) - float(parameter.GEN_ARRIVE_TIME))
            / parameter.timeout
        )
    )
    # if(calculated_rounds == 0 and ((int(block.arrive_time) - int(leaf_arrive_time)) < parameter.timeout)):
    #    calculated_rounds = 1

    # elif((int(block.arrive_time) - int(leaf_arrive_time)) > (calculated_rounds * parameter.timeout)):
    #    calculated_rounds = calculated_rounds + 1

    # expected_round = leaf_round + calculated_rounds
    print("BLOCK ROUND", block.round)
    print("EXPECTED_ROUND", expected_round)
    # print("Expected Round")
    # print(leaf_round)
    # print("Block Round")
    # print(block.round)
    # if block.round >= expected_round - parameter.roundTolerancy and block.round <= expected_round + parameter.roundTolerancy:
    if block.round >= expected_round and block.round <= expected_round + parameter.tol:
        # print("EXPECTED_ROUND", expected_round)
        return True
    else:
        return False
