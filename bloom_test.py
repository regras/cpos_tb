from bloomfilter import BloomFilter
from random import shuffle

bloomf = BloomFilter(80)
print("Size of bit array:{}".format(bloomf.size))
print("Number of hash functions:{}".format(bloomf.hash_count))

bit_array = bloomf.new_filter()

# words to be added
word_present = ["10.1.0.1", "10.1.0.100"]

# word not added
word_absent = ["10.1.0.50", "10.1.0.67", "10.1.0.101", "10.1.0.2", "10.1.0.104"]

for item in word_present:
    bloomf.add(item, bit_array)

shuffle(word_present)
shuffle(word_absent)

test_words = word_present[:10] + word_absent
shuffle(test_words)
for word in test_words:
    if bloomf.check(word, bit_array):
        if word in word_absent:
            print("'{}' is a false positive!".format(word))
        else:
            print("'{}' is probably present!".format(word))
    else:
        print("'{}' is definitely not present!".format(word))
