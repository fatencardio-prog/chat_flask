from flask import Flask, render_template
from flask_socketio import SocketIO, send, join_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"

socketio = SocketIO(app)

# Salons autorisés : code (tel que tapé) -> même nom
ROOMS = {
    "150659": "150659",   # ami 1
    "101263": "101263",   # ami 2
}

@app.route("/")
def index():
    return render_template("chat.html")

@socketio.on("join")
def on_join(data):
    pseudo = data.get("pseudo", "Anonyme")
    code = data.get("room")

    # Vérifier que le code correspond à un salon autorisé
    if not code or code not in ROOMS:
        return

    room_name = ROOMS[code]
    join_room(room_name)
    send(f"{pseudo} a rejoint le salon.", room=room_name)

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