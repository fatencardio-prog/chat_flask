from flask import Flask, render_template
from flask_socketio import SocketIO, send, join_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"

socketio = SocketIO(app)

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
    password = data.get("room")  # ici, "room" = mot de passe

    if not password or password not in ROOMS:
        return

    room_name = ROOMS[password]
    join_room(room_name)
    send(f"{pseudo} a rejoint le salon {room_name}.", room=room_name)

@socketio.on("chat_message")
def handle_chat_message(data):
    msg = data.get("msg")
    room_name = data.get("room")
    if not msg or not room_name:
        return
    send(msg, room=room_name)

# Pour Render / Gunicorn
if __name__ != "__main__":
    application = app