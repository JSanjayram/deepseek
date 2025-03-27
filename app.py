from flask import Flask, jsonify
import yt_dlp
from functools import lru_cache
import time
import os
import random

app = Flask(__name__)
# Rotate free proxies (unreliable)
proxies = [
    "203.0.113.42:3128", 
    "198.51.100.33:8080"
]

proxy=random.choice(proxies)
# Cache responses for 10 minutes to avoid repeated requests
@lru_cache(maxsize=128)
def get_stream_info(video_id):
    retries = 3
    for attempt in range(retries):
        try:
            ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'proxy': proxy
        'extractor_args': {
            'youtube': {
                'skip': ['dash', 'hls'],
                'player_client': ['android', 'web']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'en-US,en;q=0.5'
        },
    }
    
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    f"https://youtu.be/{video_id}",
                    download=False
                )
                
                # Verify we got a streamable URL
                if not info or not info.get('url'):
                    raise ValueError("No stream URL found")
                    
                return {
                    "url": info['url'],
                    "duration": info.get('duration'),
                    "title": info.get('title')
                }
                
        except Exception as e:
            if attempt == retries - 1:
                raise  # Final attempt failed
            time.sleep(2 ** attempt)  # Exponential backoff

@app.route('/stream/<video_id>')
def stream_endpoint(video_id):
    try:
        result = get_stream_info(video_id)
        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Could not extract stream: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
