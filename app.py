from flask import Flask, jsonify
import socket
import os

app = Flask(__name__)

# Get hostname (to identify which server is handling the request)
HOSTNAME = socket.gethostname()

@app.route('/')
def home():
    """Home endpoint returning load balancer app info"""
    return jsonify({
        'status': 'running',
        'app': 'Load Balancer App',
        'server': HOSTNAME,
        'message': 'Welcome to the Load Balancer Application'
    }), 200

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'server': HOSTNAME
    }), 200

@app.route('/info')
def info():
    """Get server information"""
    return jsonify({
        'hostname': HOSTNAME,
        'pid': os.getpid(),
        'status': 'operational'
    }), 200

@app.route('/api/version')
def version():
    """API version endpoint"""
    return jsonify({
        'api_version': '1.0',
        'app_name': 'load-balancer-app',
        'server': HOSTNAME
    }), 200

if __name__ == '__main__':
    # Run Flask on 0.0.0.0 so it's accessible from outside the container
    app.run(host='0.0.0.0', port=80, debug=False)
