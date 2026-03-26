from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"  # à changer si tu veux
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template("chat.html")

@socketio.on("message")
def handle_message(msg):
    print("Message reçu :", msg)
    send(msg, broadcast=True)

# IMPORTANT : ne pas utiliser socketio.run ici pour Railway
if __name__ != "__main__":
    # expose socketio pour Gunicorn
    application = app