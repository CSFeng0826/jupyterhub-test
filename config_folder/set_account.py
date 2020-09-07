import os
import crypt
from subprocess import call

nids = ['roo']

pwd='chishong656123'

for nid in nids:
    call('echo {} | sudo -S {}'.format(pwd, "docker exec --user admin jupyterhub python add_user.py"), shell=True)

for nid in nids:
    call('echo {} | sudo -S {}'.format(pwd, "docker exec --user " + nid + " jupyterhub pip install --user pandas"), shell=True)
    call('echo {} | sudo -S {}'.format(pwd, "docker exec --user " + nid + " jupyterhub python set_nbgrader.py"), shell=True)
