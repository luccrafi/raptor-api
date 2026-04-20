from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({'status': 'Raptor API online'})

@app.route('/get-links', methods=['GET'])
def get_links():
    url = request.args.get('url', '').strip()
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info.get('formats', []):
                if f.get('url') and f.get('ext') in ['mp4', 'webm']:
                    formats.append({
                        'quality': f.get('format_note', f.get('height', 'unknown')),
                        'ext': f.get('ext'),
                        'url': f.get('url'),
                        'filesize': f.get('filesize'),
                    })
            return jsonify({
                'title': info.get('title', 'Video'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'formats': formats[-5:],
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
