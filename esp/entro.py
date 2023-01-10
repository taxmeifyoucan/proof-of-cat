from collections import Counter
from math import log2

# Generate a random number from given variables 
def rng(arr, a, b, m):
    x = 0
    i = 0
    while True:
        if i >= len(arr):
            i = 0
        x = (a * x + arr[i]) % m
        yield x
        i += 1

# Check how much entropy is in the data
def entropy(data):
    n_elements = len(data)
    entropy = 0
    counter = Counter(data)
    for count in counter.values():
        p = count / n_elements
        entropy += -p * log2(p)
    return entropy
