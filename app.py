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

    # Cấu hình yt-dlp tối ưu và đọc file cookies.txt nếu có trên server
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
    }
    
    # Kiểm tra xem bạn đã đưa file cookies.txt lên server chưa, nếu có thì tự động dùng
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            
            # Phòng hờ cho YouTube hoặc một số nền tảng dùng định dạng stream tách rời
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
    # Render tự động cấp cổng thông qua biến môi trường PORT, nếu chạy dưới máy tính thì mặc định là 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
