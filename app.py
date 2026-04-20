from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

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
        'extractor_args': {
            'youtube': {
                'player_client': ['ios'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.ios.youtube/19.16.3 (iPhone16,2; U; CPU iOS 17_4_1 like Mac OS X;)',
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info.get('formats', []):
                if f.get('url') and f.get('ext') in ['mp4', 'm4a']:
                    formats.append({
                        'quality': f.get('format_note') or str(f.get('height', '')) or 'unknown',
                        'ext': f.get('ext'),
                        'url': f.get('url'),
                        'filesize': f.get('filesize') or f.get('filesize_approx'),
                    })
            return jsonify({
                'title': info.get('title', 'Video'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'formats': formats[-6:],
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
