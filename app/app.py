from flask import Flask
import os
app = Flask(__name__)
@app.get('/')
def hello():
    return f"Hello from {os.getenv('HOSTNAME','container')}!"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT','5000')))
PY
