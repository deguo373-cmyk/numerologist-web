"""API 入口：八字 / 奇门 / 紫微 统一路由"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# 添加 api/ 目录到路径，确保能找到同级模块
_api_dir = os.path.dirname(os.path.abspath(__file__))
if _api_dir not in sys.path:
    sys.path.insert(0, _api_dir)

# 延迟导入 - 在函数内部加载，避免模块级导入失败
_bazi = None
_qimen = None
_ziwei = None


def _load_modules():
    global _bazi, _qimen, _ziwei
    if _bazi is None:
        import importlib
        _bazi = importlib.import_module('bazi')
        _qimen = importlib.import_module('qimen')
        _ziwei = importlib.import_module('ziwei')


ROUTES = {
    '/api/bazi': 'bazi',
    '/api/qimen': 'qimen',
    '/api/ziwei': 'ziwei',
    '/api/bazi.py': 'bazi',
    '/api/qimen.py': 'qimen',
    '/api/ziwei.py': 'ziwei',
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
        module_name = ROUTES.get(path)

        if not module_name:
            self._json_response(404, {'error': f'Not found: {path}'})
            return

        try:
            _load_modules()
            mod = {'bazi': _bazi, 'qimen': _qimen, 'ziwei': _ziwei}[module_name]
            func_name = f'calculate_{module_name}'
            func = getattr(mod, func_name)

            length = int(self.headers.get('content-length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            result = func(body)
            self._json_response(200, result)
        except Exception as e:
            self._json_response(500, {'error': str(e)})

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
