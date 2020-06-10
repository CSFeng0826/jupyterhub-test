import os
import crypt
import pandas as pd
from subprocess import call

data = pd.read_csv("code.csv", encoding = 'utf-8')

nids = list(set(data["nid"].to_list()))

pwd='chishong656123'

for nid in nids:
    call('echo {} | sudo -S {}'.format(pwd, "docker exec --user " + nid + " jupyterhub pip install --user pandas"), shell=True)
    call('echo {} | sudo -S {}'.format(pwd, "docker exec --user " + nid + " jupyterhub python set_nbgrader.py"), shell=True)
