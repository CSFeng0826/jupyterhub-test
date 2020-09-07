# importing linrary 
import os 
import subprocess 
import sys 
import getpass 
import pandas as pd
  
df = pd.read_csv("account.csv", encoding='utf-8')

nids = df.username.to_list()
passwds = df.passwd.to_list()

pwd='chishong656123'

for count in range(0, len(nids)):
    cmd = "bash -c \"echo -e '" + passwds[count] + "\\n" + passwds[count] + "' | passwd " + nids[count] + "\""
    subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)
