from flask import Flask, render_template, session
from flask_socketio import SocketIO, send, join_room
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
# Session côté serveur pour stocker pseudo/room
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

socketio = SocketIO(app, manage_session=False)

@app.route("/")
def index():
    return render_template("chat.html")

@socketio.on("join")
def on_join(data):
    pseudo = data.get("pseudo", "Anonyme")
    room = data.get("room")

    if not room:
        return

    session["pseudo"] = pseudo
    session["room"] = room

    join_room(room)
    send(f"{pseudo} a rejoint le salon.", room=room)

@socketio.on("message")
def handle_message(msg):
    room = session.get("room")
    if not room:
        return
    send(msg, room=room)

# Pour Render / Gunicorn
if __name__ != "__main__":
    application = app