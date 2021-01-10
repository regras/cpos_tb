import random


def exponential_latency(avg_latency):
    """Represents the latency to transfer messages
    """
    return lambda: random.expovariate(1/float(avg_latency))
