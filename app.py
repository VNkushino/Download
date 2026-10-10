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
        return jsonify({'success': False, 'message': 'Vui lòng nhập đường dẫn video!'}), 400

    # Cấu hình yt-dlp tối ưu để lấy link trực tiếp cho nhiều nền tảng
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        # Thêm một số thiết lập giả lập trình duyệt để tránh bị TikTok/Instagram chặn
        'extractor_args': {
            'tiktok': {'webpage_download': True}
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # yt-dlp tự động nhận diện link của YouTube, TikTok, Facebook, IG, X...
            info = yt_dlp.YoutubeDL({'quiet': True}).extract_info(url, download=False)
            
            # Lấy link video trực tiếp
            video_url = info.get('url')
            
            # Nếu là YouTube, đôi khi cần lấy qua định dạng kết hợp, ta xử lý phòng hờ:
            if not video_url and 'formats' in info:
                for f in info['formats']:
                    if f.get('url') and f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        video_url = f['url']
                        break

            title = info.get('title', 'Video Download')

            if not video_url:
                return jsonify({'success': False, 'message': 'Không thể bóc tách link trực tiếp từ nền tảng này!'}), 400

            return jsonify({
                'success': True,
                'title': title,
                'download_url': video_url
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: Không thể tải video này. Chi tiết: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
