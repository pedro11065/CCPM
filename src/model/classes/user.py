from src.model.services.readEnv import *
from src.config.colors import *
from flask import jsonify
class User:

    @staticmethod
    def login(data):

        env = readEnv()

        ENV_EMAIL= env.get("EMAIL").lower()
        ENV_PASSWORD=str(env.get("PASSWORD"))


        user_email = data.get('username')
        user_password = data.get('password')

        if user_email == ENV_EMAIL and user_password == ENV_PASSWORD:

            print(cyan("[back-end]: ") + "User ok!")

            return jsonify({
                'ok': True,
                'message': "Login successful!"
            }), 200
        
        else:

            print(red("[ERROR]: ") + "Invalid credentials.")
            return jsonify({
                'ok': False,
                'error': 'Invalid user or password.'
            }), 401
