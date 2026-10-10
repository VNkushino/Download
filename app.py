from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)  # Cho phép mọi trang web gọi đến server này

@app.route('/get-download-link', methods=['POST'])
def get_download_link():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'success': False, 'message': 'Vui lòng nhập đường dẫn video'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            
            if not video_url and 'formats' in info:
                for f in info['formats']:
                    if f.get('url') and f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        video_url = f['url']
                        break

            title = info.get('title', 'Video Download')

            if not video_url:
                return jsonify({'success': False, 'message': 'Không thể bóc tách link trực tiếp từ video này!'}), 400

            return jsonify({
                'success': True,
                'title': title,
                'download_url': video_url
            })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi khi lấy link: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)