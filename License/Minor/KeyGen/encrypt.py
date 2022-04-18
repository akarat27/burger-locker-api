import sys
import base64
import json
import subprocess

#from Crypto.Cipher import AES
from cryptography.fernet import Fernet

def encrypt(message: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(message)

def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token) 

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('Please input the message option is uuid')
    else:    
        message = sys.argv[1]
        if message == "uuid":
            hwid = str(subprocess.check_output('wmic csproduct get uuid')).split('\\r\\n')[1].strip('\\r').strip()
            message = hwid
            key = "TLUKyqJD58LnXv286GeYVwQIHgnbeHUK_Xs9lA93FGA=" #Fernet.generate_key()
            print('Secret key  : {}'.format(key))       #print('Secret key  : {}'.format(key.decode()))   #decode from byte object b'xxx'
            print('Message key : {}'.format(message))
            encrypted_message = encrypt(message.encode(),key)
            #print('Message encrypted : {}'.format(encrypted_message))
            print('Message encrypted in hex : {}'.format(encrypted_message.hex()))
            #print('Message encrypted in bytes : {}'.format(bytes.fromhex(encrypted_message.hex())))
            token = encrypted_message
            decypted_message = decrypt(token,key).decode()
            print('Message decrypted : {}'.format(decypted_message))

            dict_data = {
                # "key": key, # key.decode(),
                "uuid": message,
                "encrypted": encrypted_message.hex(),
            }
            
            json_object = json.dumps(dict_data, indent = 4)

            with open("keygen.json","w") as outfile:
                outfile.write(json_object) 
        else:        
            print('Please input the message option is uuid')