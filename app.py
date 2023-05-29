from flask import Flask
from flask import request
from base64 import b64decode
from audiofun import pitch_shift, save
from flask_cors import CORS
from flask import send_file
import soundfile as sf
import librosa

app = Flask(__name__)

CORS(app, support_credentials=True)

@app.route("/", methods=["GET"])
def hello():
    return "\u0422\u0415\u0411\u0415\u0020\u0421\u042e\u0414\u0410\u0020\u041d\u0415\u041b\u042c\u0417\u042f\u0021\u0021\u0021"


@app.route("/new_sound.wav", methods=["GET"])
def return_sound():
    return send_file("new_sound.wav", mimetype="audio/wav", as_attachment=True)


@app.route("/audio/", methods=["POST"])
def prepare_file():
    new_file_name = "new_sound.wav"
    audio: str = request.json["audio"]
    i = audio.find(",") + 1
    ogg = b64decode(audio[i:])
    with open ("input.ogg", "wb") as f:
        f.write(ogg)
         
    audio_data, sr1 = librosa.read("input.ogg")
    
    pitches = []
    if request.json["isActive"]:
        pitches.append(request.json["pitch"])
    if request.json["isActive1"]:
        pitches.append(request.json["pitch1"])

    result = pitch_shift(audio_data, pitches, sr1)
    save(result, new_file_name, sr1)
    
    return {"name": "https://audio-pitch-shift.onrender.com/" + new_file_name}, 200