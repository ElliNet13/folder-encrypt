import os
import argparse
from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def encrypt_file(file_path, key):
    fernet = Fernet(key)
    with open(file_path, "rb") as file:
        original_data = file.read()
    encrypted_data = fernet.encrypt(original_data)
    with open(file_path + ".encrypted", "wb") as file:
        file.write(encrypted_data)
    os.remove(file_path)

def encrypt_folder(folder_path, key):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            encrypt_file(file_path, key)

def generate_decrypt_script(folder_to_encrypt, key, output):
    script = f"""
import os
from cryptography.fernet import Fernet

def decrypt_file(file_path, key):
    fernet = Fernet(key)
    with open(file_path, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    with open(file_path[:-10], "wb") as file:
        file.write(decrypted_data)
    os.remove(file_path)

def decrypt_folder(folder_path, key):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            decrypt_file(file_path, key)

key = {repr(key.decode())}
folder_to_decrypt = {repr(folder_to_encrypt)}
decrypt_folder(folder_to_decrypt, key)
print('Decryption complete!')
"""

    with open(ouput, "w") as script_file:
        script_file.write(script)

key = generate_key()
parser = argparse.ArgumentParser(description='Encrypt a folder and generate a decryption script.')
parser.add_argument('input', type=str, help='Folder to encrypt')
parser.add_argument('output', type=str, nargs='?', default='decrypt.py', help='Output Python file (default: decrypt.py)')
args = parser.parse_args()
folder_to_encrypt = args.input


folder_to_encrypt = os.path.abspath(folder_to_encrypt)
encrypt_folder(folder_to_encrypt, key)
generate_decrypt_script(folder_to_encrypt, key, args.output)

print("Folder encrypted successfully.")