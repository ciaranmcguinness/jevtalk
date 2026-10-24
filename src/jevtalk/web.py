from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from .core import get_keys, run

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

keys = get_keys()

sio = SocketIO(app)

conversations = {}

@app.route('/')
def index():
    return render_template('index.html')

# Handle user messages
@sio.on('message')
def handle_message(data):
    f = (lambda x: send(x,to=request.sid))
    conversations[request.sid] = conversations.get(request.sid, [])
    conversations[request.sid].append({"role":"user","content":str(data)})
    conversations[request.sid] = run(conversations[request.sid], f, keys)
    emit("done",to=request.sid)

# Handle disconnects
@sio.on('disconnect')
def handle_disconnect():
    conversations.pop(request.sid, None)

def run_web():
    sio.run(app)