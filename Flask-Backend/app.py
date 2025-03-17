from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

#Assuming 2 words per second
def estimate_audio_length(text, words_per_second=2):
    words = text.split()
    return len(words) / words_per_second

#Triming the content if it exceeds more than  60 seconds
def trim_text(text, max_duration=60, words_per_second=2, placeholder="..."):
    words = text.split()
    max_words = max_duration * words_per_second

    if len(words) <= max_words:
        return text

    keep_words = max_words // 2  # Half of the words to keep from each side
    return ' '.join(words[:keep_words]) + f" {placeholder} " + ' '.join(words[-keep_words:])



#Api for the content length
@app.route('/validate-audio-length', methods=['POST'])
def validate_audio():
    data = request.json
    text = data['text']
    audio_length = data.get('audio_length', estimate_audio_length(text))

    if audio_length > 60:
        text = trim_text(text)

    return jsonify({'validated_text': text, 'audio_length': audio_length})

if __name__ == '__main__':
    app.run(debug=True)
