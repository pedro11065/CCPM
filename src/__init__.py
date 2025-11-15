from flask import Flask

def create_app():
    app = Flask(__name__, static_folder='view/static', template_folder='view/templates')
    #app.config['SECRET_KEY'] = 'chave_secreta_nome' #Responsável por encriptar os cookies e session data (Ainda não utilizado).

    from .controller.index import index
    from .controller.api.debit import debit

    #app.register_blueprint(index, url_prefix='/home')
    app.register_blueprint(index, url_prefix='/')
    app.register_blueprint(debit, url_prefix='/api')
    #app.register_blueprint(index, url_prefix='')



    return app;


