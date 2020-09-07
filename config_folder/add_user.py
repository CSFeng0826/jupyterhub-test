# importing linrary 
import os 
import subprocess 
import sys 
import getpass 
  
subprocess.call('echo {} | sudo -S {}'.format('chishong656123', "bash -c \"echo -e 'test\\ntest' | passwd roo\""), shell=True)
