from flask import Flask

app = Flask(__name__)

@app.route('/debug')
def debug():
    return "Flask is alive!"

@app.route('/')
def home():
    return "Flask is running"




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)