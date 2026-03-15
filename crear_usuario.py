from app.core.security import hash_password

password = "123456"

hash_generado = hash_password(password)

print("Hash generado:")
print(hash_generado)