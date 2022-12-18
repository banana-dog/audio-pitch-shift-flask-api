from flask import Flask
from flask import request
from base64 import b64decode
import os
from audiofun import pitch_shift, read_file, high_pass, save
import numpy as np
from flask_cors import CORS
from flask import send_file

app = Flask(__name__)

CORS(app, support_credentials=True)
@app.route("/", methods=["GET"])
def hello():
    return "!!"
    with open("index.html", "r") as f:
        return f.read()


@app.route("/new_sound.wav", methods=["GET"])
def return_sound():
    return send_file(
         "new_sound.wav", 
         mimetype="audio/wav", 
         as_attachment=True)


@app.route("/audio/", methods=["POST"])
def world():
    file_name = "sound.ogg"
    new_file_name = "new_sound.wav"
    audio: str = request.json["audio"]
    i = audio.find(",") + 1
    ogg = b64decode(audio[i:])
    with open(file_name, "wb") as f:
        f.write(ogg)
    cmd = f"ffmpeg -y -i {file_name} -map 0 -map -0:s? -c:v copy -ac 2 -ar 44100 -vn {new_file_name}"

    os.system(cmd)
    data = high_pass(read_file(new_file_name))

    pitches = []
    if request.json["isActive"]:
        pitches.append(pitch_shift(data, request.json["pitch"]))
    if request.json["isActive1"]:
        pitches.append(pitch_shift(data, request.json["pitch1"]))

    pitches= [np.pad(p, (0, data.shape[0] - p.shape[0])).astype("int16") for p in pitches]
    save(sum(pitches), new_file_name)
    return {"name": "https://localhost:5000/" + new_file_name}, 200


if __name__ == "__main__":
    context = ('/etc/secrets/server.crt', '/etc/secrets/server.key')
    app.run(host = '0.0.0.0', ssl_context=context)
