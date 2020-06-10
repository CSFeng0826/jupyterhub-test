import os
import crypt

password ="123456" 
encPass = crypt.crypt(password,"22")
os.system("sudo docker exec -it jupyterhub passwd csfeng0826")
