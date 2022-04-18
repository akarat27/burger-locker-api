import sys
import base64
import json

#from Crypto.Cipher import AES
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

def encrypt(message: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(message)

def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token) 

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('Please input the message encrypted')
    else:    
        hex_message = sys.argv[1]
        key = "TLUKyqJD58LnXv286GeYVwQIHgnbeHUK_Xs9lA93FGA="  #key = Fernet.generate_key()
       
        try:
            token = bytes.fromhex(hex_message)
            decypted_message = decrypt(token,key).decode()
            print('Message decrypted : {}'.format(decypted_message))
        except ValueError:
            print('Message decrypted : {}'.format('InvalidToken'))
        except InvalidToken:
            print('Message decrypted : {}'.format('InvalidToken'))
        else:    
            print('Message decrypted : {}'.format('InvalidToken'))