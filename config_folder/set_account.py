import os
from subprocess import call
import pandas as pd

df = pd.read_csv("account.csv", encoding='utf-8')

nids = df.username.to_list()

pwd='chishong656123'

for nid in nids:
    call('echo {} | sudo -S {}'.format(pwd, "docker exec -it jupyterhub useradd --create-home " + nid), shell=True)

call('echo {} | sudo -S {}'.format(pwd, "docker exec --user admin jupyterhub python add_user.py"), shell=True)

for nid in nids:
    call('echo {} | sudo -S {}'.format(pwd, "docker exec --user " + nid + " jupyterhub pip install --user pandas"), shell=True)
    call('echo {} | sudo -S {}'.format(pwd, "docker exec --user " + nid + " jupyterhub python set_nbgrader.py"), shell=True)
