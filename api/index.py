"""API 入口：八字 / 奇门 / 紫微 统一路由"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# 确保能找到同级模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bazi import calculate_bazi
from qimen import calculate_qimen
from ziwei import calculate_ziwei


ROUTES = {
    '/api/bazi': calculate_bazi,
    '/api/qimen': calculate_qimen,
    '/api/ziwei': calculate_ziwei,
    '/api/bazi.py': calculate_bazi,
    '/api/qimen.py': calculate_qimen,
    '/api/ziwei.py': calculate_ziwei,
}


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self._cors_headers()
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()

    def _handle(self):
        path = self.path.split('?')[0].rstrip('/')
        func = ROUTES.get(path)

        if not func:
            self._json_response(404, {'error': f'Not found: {path}'})
            return

        try:
            length = int(self.headers.get('content-length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            result = func(body)
            self._json_response(200, result)
        except Exception as e:
            self._json_response(400, {'error': str(e)})

    def _json_response(self, status, data):
        self._cors_headers()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
