# import parameter
import parameter
from decimal import Decimal

############combinations##########
def Combinations(m, n):
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
    k = m - n
    k_fat = 1
    cont = 1
    while cont < k:
        cont += 1
        k_fat *= cont

    mn_fatorial = k_fat

    return m_fatorial / (mn_fatorial * n_fatorial)


##################################################

#########input parameters#########
smean = 6
round = 1
fileName = "results_mean_smaller.txt"
#################################
# while(smean >= 1):
round = 5
tprob = 1
#    while(tprob >= (10**-6) and round <= 10):
####define initial parameters####
p = float(parameter.tal) / float(parameter.W)
limit = (round * smean) - 1
tprob = Decimal(0)
################################
while limit >= 0:
    q = MixedIntegerLinearProgram()
    w = q.new_variable(integer=True, nonnegative=True)
    for k in range(0, round):
        if k == 0:
            exp = "w[%d]" % k
        else:
            exp = exp + " +w[%d]" % k
    q.add_constraint(eval(exp) == limit)
    a = q.polyhedron().integral_points()

    # calc probability
    for k in a:
        prob = Decimal(1)
        for i in range(0, round):
            index = "(" + str(parameter.qW) + "," + str(k[i]) + ")"
            if index in parameter.combinations_conluio:
                comb = parameter.combinations_conluio[index]
            else:
                print("combinations not present in list")
                comb = Combinations(parameter.qW, k[i])
            prob_i = Decimal(comb * (p ** k[i]) * ((1 - p) ** (parameter.qW - k[i])))
            prob = prob * prob_i
        tprob = tprob + prob
    limit = limit - 1
tprob = Decimal(1) - Decimal(tprob)
print(tprob)
results = open(fileName, "a")
results.write(
    "probability: "
    + str(tprob)
    + "\n"
    + "mean higher than "
    + str(smean)
    + "\n"
    + "after "
    + str(round)
    + " rounds\n"
)
results.close()
print(
    "we have probability %f of exists other chain with the mean %f on round %d"
    % (tprob, smean, round)
)
#        round = round + 1
#    smean = smean - 1
