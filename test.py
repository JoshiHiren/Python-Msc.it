import os

from dotenv import load_dotenv

load_dotenv()

secret_key=os.gitenv("SECRET_KEY")
print(secret_key)