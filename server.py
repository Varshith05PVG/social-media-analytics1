from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import requests
import json
import threading
from datetime import datetime
from cv_analyzer import CVAnalyzer
from web_mining import WebMiner
from fusion_model import FusionModel

app = Flask(__name__, template_folder='templates')
CORS(app)

# Initialize analyzers
cv_analyzer = CVAnalyzer()
web_miner = WebMiner()
fusion_model = FusionModel()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/proxy-image')
def proxy_image():
    """Proxy images to avoid CORS issues"""
    image_url = request.args.get('url')
    if not image_url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        from urllib.parse import urlparse
        allowed_domains = ['instagram.com', 'facebook.com', 'twitter.com', 'tiktok.com', 'via.placeholder.com']
        domain = urlparse(image_url).netloc

        if not any(allowed_domain in domain for allowed_domain in allowed_domains):
            return jsonify({'error': 'Domain not allowed'}), 403

        response = requests.get(image_url, timeout=10, stream=True)
        return Response(
            response.content,
            content_type=response.headers.get('content-type', 'image/jpeg'),
            headers={'Access-Control-Allow-Origin': '*'}
        )
    except Exception:
        default_response = requests.get('https://via.placeholder.com/150/6366f1/ffffff?text=Error', timeout=5)
        return Response(
            default_response.content,
            content_type='image/jpeg',
            headers={'Access-Control-Allow-Origin': '*'}
        )


@app.route('/api/analyze', methods=['POST'])
def analyze_profile():
    data = request.get_json(silent=True) or {}
    profile_url = (data.get('url') or '').strip()
    platform = data.get('platform', 'instagram')

    if not profile_url:
        return jsonify({'error': 'URL is required'}), 400

    results = {
        'url': profile_url,
        'platform': platform,
        'timestamp': datetime.now().isoformat(),
        'cv_analysis': None,
        'web_mining': None,
        'fusion_result': None,
        'profile_info': None,
        'pipeline': []
    }

    try:
        results['pipeline'].append({
            'step': 'Fetching profile data',
            'status': 'processing',
            'timestamp': datetime.now().isoformat()
        })

        username = profile_url.rstrip('/').split('/')[-1]
        profile_info = fetch_profile_data(username, platform)
        results['pipeline'][-1]['status'] = 'completed'
        results['profile_info'] = profile_info

        results['pipeline'].append({
            'step': 'Analyzing profile picture (CV)',
            'status': 'processing',
            'timestamp': datetime.now().isoformat()
        })
        cv_results = cv_analyzer.analyze(profile_info)
        results['cv_analysis'] = cv_results
        results['pipeline'][-1]['status'] = 'completed'

        results['pipeline'].append({
            'step': 'Mining web signals',
            'status': 'processing',
            'timestamp': datetime.now().isoformat()
        })
        web_results = web_miner.analyze(profile_info)
        results['web_mining'] = web_results
        results['pipeline'][-1]['status'] = 'completed'

        results['pipeline'].append({
            'step': 'Fusing CV + Web signals',
            'status': 'processing',
            'timestamp': datetime.now().isoformat()
        })
        fusion_results = fusion_model.fuse(cv_results, web_results, profile_info)
        results['fusion_result'] = fusion_results
        results['pipeline'][-1]['status'] = 'completed'

        return jsonify(results), 200

    except Exception as e:
        results['error'] = str(e)
        return jsonify(results), 500

def fetch_profile_data(username, platform):
    """Fetch profile data from various platforms"""
    try:
        if platform == 'instagram':
            api_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
            headers = {
                "x-ig-app-id": "936619743392459",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            print(f"Fetching Instagram data for: {username}")
            print(f"API URL: {api_url}")
            
            response = requests.get(api_url, headers=headers, timeout=10)
            print(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"API Error: {response.text}")
                raise Exception(f"API returned status {response.status_code}")
            
            user_data = response.json()['data']['user']
            print(f"Successfully fetched data for: {user_data['username']}")
            print(f"Profile pic URL: {user_data.get('profile_pic_url_hd', 'Not found')}")
            
            return {
                'username': user_data['username'],
                'full_name': user_data['full_name'],
                'biography': user_data['biography'],
                'followers': user_data['edge_followed_by']['count'],
                'following': user_data['edge_follow']['count'],
                'profile_pic_url': user_data.get('profile_pic_url_hd') or user_data.get('profile_pic_url') or 'https://via.placeholder.com/150/6366f1/ffffff?text=Instagram',
                'is_verified': user_data['is_verified'],
                'is_business': user_data.get('is_business_account', False),
                'platform': 'instagram',
                'api_success': True
            }
    except Exception as e:
        # Return demo data if API fails
        return {
            'username': username,
            'full_name': 'Demo User',
            'biography': 'Demo bio for testing purposes',
            'followers': 5000,
            'following': 1200,
            'profile_pic_url': f'https://via.placeholder.com/150/6366f1/ffffff?text={username[:10]}',
            'is_verified': False,
            'is_business': False,
            'platform': platform,
            'demo': True,
            'api_success': False
        }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
