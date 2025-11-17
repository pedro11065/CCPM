import os, dotenv

def readEnv(env_path=".env", override=True):

    dotenv.load_dotenv(dotenv_path=str(env_path), override=override)
    parsed = dotenv.dotenv_values(dotenv_path=str(env_path))
    result = {k: os.environ.get(k, v) for k, v in parsed.items() if k is not None}

    return result