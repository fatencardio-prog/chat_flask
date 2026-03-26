from flask import Flask, render_template, session
from flask_socketio import SocketIO, send, join_room
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

socketio = SocketIO(app, manage_session=False)

# Salons autorisés : mot de passe -> nom du salon
ROOMS = {
    "150659": "tollis",   # ami 1
    "101263": "louati",   # ami 2
}

@app.route("/")
def index():
    return render_template("chat.html")

@socketio.on("join")
def on_join(data):
    pseudo = data.get("pseudo", "Anonyme")
    password = data.get("room")  # ici on considère que "room" est le mot de passe

    # Vérifier que le mot de passe correspond à un salon autorisé
    if not password or password not in ROOMS:
        # on pourrait envoyer un message d'erreur au client plus tard
        return

    room_name = ROOMS[password]

    session["pseudo"] = pseudo
    session["room"] = room_name

    join_room(room_name)
    send(f"{pseudo} a rejoint le salon {room_name}.", room=room_name)

@socketio.on("message")
def handle_message(msg):
    room_name = session.get("room")
    if not room_name:
        return
    send(msg, room=room_name)

# Pour Render / Gunicorn
if __name__ != "__main__":
    application = app