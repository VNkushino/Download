from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)  # Cho phép mọi trang web gọi đến server này

@app.route('/')
def home():
    return "Server download Facebook đang hoạt động bình thường!"

@app.route('/get-download-link', methods=['POST'])
def get_download_link():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Không tìm thấy dữ liệu JSON'}), 400
        
    fb_url = data.get('url')

    if not fb_url:
        return jsonify({'success': False, 'message': 'Vui lòng nhập đường dẫn Facebook'}), 400

    # Cấu hình yt-dlp để trích xuất link video
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(fb_url, download=False)
            video_url = info.get('url')
            title = info.get('title', 'Facebook Video')

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
