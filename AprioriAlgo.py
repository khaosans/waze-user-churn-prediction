import requests
import os
from itertools import combinations, chain

os.chmod('output.txt', 0o644)
def read_data_from_file(filename):
    with open(filename, 'r') as file:
        transactions = [line.strip().split(';') for line in file]
    return transactions

def generate_all_itemsets(transactions):
    single_items = set(chain.from_iterable(transactions))
    all_itemsets = {frozenset([item]): 0 for item in single_items}
    for transaction in transactions:
        for size in range(2, len(transaction) + 1):
            for itemset in combinations(transaction, size):
                all_itemsets[frozenset(itemset)] = 0
    return all_itemsets

def filter_itemsets_by_support(transactions, all_itemsets, min_support):
    for transaction in transactions:
        for itemset in all_itemsets.keys():
            if itemset.issubset(transaction):
                all_itemsets[itemset] += 1
    return {itemset: count for itemset, count in all_itemsets.items() if count >= min_support}

def write_frequent_itemsets_to_file(itemsets, filename, length=None):
    with open(filename, 'w') as file:
        for itemset, count in sorted(itemsets.items(), key=lambda x: (-x[1], x[0])):
            if length is None or len(itemset) == length:
                formatted_itemset = ';'.join(sorted(itemset))
                file.write(f"{count}:{formatted_itemset}\n")

def main(filename, min_support):
    transactions = read_data_from_file(filename)
    all_itemsets = generate_all_itemsets(transactions)
    frequent_itemsets = filter_itemsets_by_support(transactions, all_itemsets, min_support)

    # Task 1: Output length-1 frequent categories
    write_frequent_itemsets_to_file(frequent_itemsets, "patterns_length_1.txt", length=1)

    # Task 2: Output all frequent category sets
    write_frequent_itemsets_to_file(frequent_itemsets, "patterns_all.txt")

    # Optionally, print the results
    for itemset, count in sorted(frequent_itemsets.items(), key=lambda x: (-x[1], x[0])):
        formatted_itemset = ';'.join(sorted(itemset))
        print(f"{count}:{formatted_itemset}")

filename = "output.txt"
min_support = 771
main(filename, min_support)