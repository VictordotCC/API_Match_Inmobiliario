# Añadir al inicio de aes.py
from Crypto.Random import get_random_bytes
import base64

# Generar clave AES-256 (32 bytes)
KEY = get_random_bytes(32)
# Generar IV aleatorio (16 bytes) 
IV = get_random_bytes(16)

# Codificar bytes a string base64
key_str = base64.b64encode(KEY).decode('utf-8')
iv_str = base64.b64encode(IV).decode('utf-8')

print(f'KEY: {key_str}')
print(f'IV: {iv_str}')

