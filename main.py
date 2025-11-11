from src import create_app
import subprocess
from flask_cors import CORS

app = create_app();
CORS(app) 
app.app_context().push()



#script_path = 'app.py'
#subprocess.Popen(['start', 'cmd', '/K', f'python {script_path}'], shell=True)

app.run(debug=True) 