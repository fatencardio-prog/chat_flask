import os
import json
from datetime import datetime

from flask import Flask, render_template
from flask_socketio import SocketIO, send, join_room, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"

socketio = SocketIO(app)

# Dossier pour stocker les historiques
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Salons autorisés : code (tel que tapé) -> même nom
ROOMS = {
    "150659": "150659",   # ami 1
    "101263": "101263",   # ami 2
}


def get_history_file(room_code):
    return os.path.join(DATA_DIR, f"{room_code}.json")


def load_history(room_code):
    path = get_history_file(room_code)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def append_message(room_code, msg):
    path = get_history_file(room_code)
    history = load_history(room_code)
    history.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "text": msg,
    })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


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

    # Charger l'historique pour ce salon et l'envoyer juste à ce client
    history = load_history(code)
    emit("history", history)  # uniquement au client qui vient de se connecter

    # Message de "X a rejoint le salon."
    join_msg = f"{pseudo} a rejoint le salon."
    append_message(code, join_msg)
    send(join_msg, room=room_name)


@socketio.on("chat_message")
def handle_chat_message(data):
    msg = data.get("msg")
    room_code = data.get("room")
    if not msg or not room_code:
        return

    # Sauvegarder dans l'historique du salon (par code)
    append_message(room_code, msg)

    # Envoyer à tous les clients du salon (room = nom)
    room_name = ROOMS.get(room_code, room_code)
    send(msg, room=room_name)


# Pour Render / Gunicorn (Render démarre "app:application")
if __name__ != "__main__":
    application = app

# Pour exécuter en local avec `python app.py`
if __name__ == "__main__":
    socketio.run(app, debug=True)