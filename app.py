import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from deep_translator import GoogleTranslator
from gtts import gTTS
import base64
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# Ensure CORS is allowed so your phone's browser can connect securely
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('send_message')
def handle_message(data):
    text = data['text']
    sender_lang = data['lang'] # 'tl' (Tagalog) or 'ne' (Nepali)
    
    # Determine the target language
    target_lang = 'ne' if sender_lang == 'tl' else 'tl'
    
    try:
        # 1. Translate the text
        translated = GoogleTranslator(source=sender_lang, target=target_lang).translate(text)
        
        # 2. Generate Audio (Text-to-Speech)
        tts = gTTS(text=translated, lang=target_lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        audio_base64 = base64.b64encode(fp.getvalue()).decode('utf-8')
        
        # 3. Broadcast to all connected users
        emit('receive_message', {
            'original': text,
            'translated': translated,
            'sender_lang': sender_lang,
            'target_lang': target_lang,
            'audio_data': audio_base64
        }, broadcast=True)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)