
from itertools import combinations


THUMBS = ('U', 'C')
FINGERS = ('U', 'R', 'C')

comb = set()
for lt in THUMBS:
    for rt in THUMBS:
        for l1 in FINGERS:
            for l2 in FINGERS:
                for l3 in FINGERS:
                    for l4 in FINGERS:
                        for r1 in FINGERS:
                            for r2 in FINGERS:
                                for r3 in FINGERS:
                                    for r4 in FINGERS:
                                        # comb.add(f"{l4}{l3}{l2}{l1} {lt} {rt} {r1}{r2}{r3}{r4}")
                                        comb.add(f"{l4}{l2}{l2}{l1} {lt} {rt} {r1}{r2}{r2}{r4}")

def valid_comb(combination):
    if "CU" in combination or "UC" in combination:
        return False

    return True

total = 0
valids = set()
ALL = 26244
for c in comb:
    if valid_comb(c):
        total += 1
        valids.add(c)

print(f"{total}/{ALL} ({total/ALL*100:.2f}%) Valid Gestures")

import random
print(random.choice(list(valids)))