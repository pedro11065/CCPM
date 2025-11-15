from src.model.services.readEnv import *

class User:

    def load(data):

        env = readEnv()

        ENV_EMAIL=env.get("EMAIL")
        ENV_PASSWORD=env.get("PASSWORD")

        