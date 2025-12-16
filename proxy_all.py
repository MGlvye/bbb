# proxy.py 终极版 - 支持 IAM + IoTDA + 任意华为云服务
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

class Proxy(BaseHTTPRequestHandler):
    def do_GET(self): self.handle_request()
    def do_POST(self): self.handle_request()
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Expose-Headers', 'x-subject-token')
        self.end_headers()

    def handle_request(self):
        # 1. IAM 接口（Token 和 Project）
        if self.path.startswith('/v3/'):
            target = "https://iam.myhuaweicloud.com" + self.path
            if '?' in self.path:
                target += '?' + self.path.split('?', 1)[1]

        # 2. IoTDA 接口（通过 header 传真实 URL）
        elif self.path == '/proxy-iotda':
            target = self.headers.get('Target-Url')
            if not target:
                self.send_error(400, "Missing Target-Url header")
                return

        else:
            self.send_error(404)
            return

        # 转发请求
        resp = requests.request(
            method=self.command,
            url=target,
            data=self.rfile.read(int(self.headers.get('Content-Length', 0))) if self.command == 'POST' else None,
            headers={k: v for k, v in self.headers.items() if k.lower() != 'host'}
        )

        # 返回响应
        self.send_response(resp.status_code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Expose-Headers', 'x-subject-token')
        if 'x-subject-token' in resp.headers:
            self.send_header('x-subject-token', resp.headers['x-subject-token'])
        self.end_headers()
        self.wfile.write(resp.content)

print("华为云全接口代理已启动 → http://localhost:8000")
HTTPServer(('localhost', 8000), Proxy).serve_forever()