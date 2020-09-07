#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import string
import pandas as pd

print("Generate Password")

df = pd.read_csv("test.csv", encoding='utf-8')

nids = df.username.to_list()

seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
passwd = []
for nid in nids:
    sa = []
    for i in range(8):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    passwd.append(salt)

df = pd.DataFrame({"username":nids, "passwd":passwd})
df.to_csv("account.csv", encoding='utf-8', index=False)