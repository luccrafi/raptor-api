from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({'status': 'Raptor API online'})

def detect_platform(url):
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    if 'facebook.com' in url or 'fb.watch' in url or 'fb.com' in url:
        return 'facebook'
    if 'instagram.com' in url:
        return 'instagram'
    if 'tiktok.com' in url:
        return 'tiktok'
    if 'twitter.com' in url or 'x.com' in url:
        return 'twitter'
    return 'other'

@app.route('/get-links', methods=['GET'])
def get_links():
    url = request.args.get('url', '').strip()
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    platform = detect_platform(url)
    import urllib.parse
    enc = urllib.parse.quote(url, safe='')

    # YouTube and Facebook — redirect to working third-party sites
    if platform == 'youtube':
        return jsonify({
            'title': 'YouTube Video',
            'redirect': True,
            'platform': 'YouTube',
            'links': [
                {'label': 'Download via SSYouTube', 'url': 'https://ssyoutube.com/en/download?url=' + enc},
                {'label': 'Download via SaveFrom', 'url': 'https://en.savefrom.net/#url=' + enc},
                {'label': 'Download via Y2Mate', 'url': 'https://www.y2mate.com/youtube/' + enc},
            ]
        })

    if platform == 'facebook':
        return jsonify({
            'title': 'Facebook Video',
            'redirect': True,
            'platform': 'Facebook',
            'links': [
                {'label': 'Download via SnapSave', 'url': 'https://snapsave.app/?url=' + enc},
                {'label': 'Download via FDown', 'url': 'https://fdown.net/?URLz=' + enc},
                {'label': 'Download via SaveFrom', 'url': 'https://en.savefrom.net/#url=' + enc},
            ]
        })

    # Instagram, TikTok, Twitter — use yt-dlp backend
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info.get('formats', []):
                if f.get('url') and f.get('ext') in ['mp4', 'webm', 'm4a']:
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
                'redirect': False,
                'formats': formats[-6:],
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
