from openai import OpenAI
from os.path import join, dirname
from dotenv import load_dotenv
import os
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#VARIAVEIS NO .ENV
base_url = os.getenv("base_url")
api_key  = os.getenv("api_key")

client = OpenAI(base_url=base_url, api_key=api_key)

modelos = client.models.list()



for modelo in modelos.data:
    print (modelo.id)