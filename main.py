import os
import argparse
from cryptography.fernet import Fernet

# Check if tqdm is available
try:
    from tqdm import tqdm
    tqdm_available = True
except ImportError:
    tqdm_available = False

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
    total_files = sum([len(files) for _, _, files in os.walk(folder_path)])

    if tqdm_available:
        with tqdm(total=total_files, desc='Encrypting') as pbar:
            for root, _, files in os.walk(folder_path):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    encrypt_file(file_path, key)
                    pbar.update(1)
    else:
        print(f"Encrypting files in {folder_path}...")

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
    output_path = os.path.splitext(file_path)[0]
    with open(output_path, "wb") as file:
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

    with open(output, "w") as script_file:
        script_file.write(script)

key = generate_key()
parser = argparse.ArgumentParser(description='Encrypt a folder and optionally generate a decryption script.')
parser.add_argument('input', type=str, help='Folder to encrypt')
parser.add_argument('--no-script', action='store_true', help='Do not generate the decryption script')
parser.add_argument('output', type=str, nargs='?', default='decrypt.py', help='Output Python file (default: decrypt.py)')
args = parser.parse_args()
folder_to_encrypt = args.input

folder_to_encrypt = os.path.abspath(folder_to_encrypt)
encrypt_folder(folder_to_encrypt, key)

if args.no_script:
    print(f"Folder encrypted successfully. Key: {key.decode()}")
else:
    generate_decrypt_script(folder_to_encrypt, key, os.path.abspath(args.output))
    print("Folder encrypted successfully and decryption script generated.")
