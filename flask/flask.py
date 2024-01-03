from flask import Flask

app = Flask('app')

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/lizard')
def hello_world():
  return 'lizard'

app.run(host='0.0.0.0', port=8080)
