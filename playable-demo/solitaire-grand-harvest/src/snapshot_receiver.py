import base64, http.server, os
D=os.path.dirname(os.path.abspath(__file__))
class H(http.server.BaseHTTPRequestHandler):
    def _cors(self): self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Headers','*')
    def do_OPTIONS(self): self.send_response(204); self._cors(); self.end_headers()
    def do_POST(self):
        n=int(self.headers.get('Content-Length',0)); body=self.rfile.read(n).decode()
        name=os.path.basename(self.path.strip('/')) or 'shot.png'
        data=body.split(',',1)[1] if body.startswith('data:') else body
        open(os.path.join(D,name),'wb').write(base64.b64decode(data))
        self.send_response(200); self._cors(); self.end_headers(); self.wfile.write(b'ok')
    def log_message(self,*a): pass
http.server.HTTPServer(('127.0.0.1',8766),H).serve_forever()
