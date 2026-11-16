from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import subprocess
import os

class BotHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/start-unfollow':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            users = data.get('users', [])

            # บันทึกรายชื่อลง target_users.txt อัตโนมัติ
            with open('target_users.txt', 'w', encoding='utf-8') as f:
                for user in users:
                    f.write(f"{user}\n")

            print(f"🚀 ได้รับรายชื่อเป้าหมาย {len(users)} บัญชี กำลังเริ่มรันบอทและจำลองการกด Enter...")

            # สั่งรัน unfollow_bot.py และส่งตัวอักษร Enter (\n) เข้าไปผ่าน stdin อัตโนมัติ
            process = subprocess.Popen(
                ['python3', 'unfollow_bot.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # ส่งคำสั่งกด Enter ให้ Python ทันทีโดยไม่ต้องรอกดที่คีย์บอร์ด
            try:
                process.stdin.write("\n")
                process.stdin.flush()
            except Exception as e:
                print(f"⚠️ ส่งสัญญาณ Enter ไม่สำเร็จ: {e}")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'started', 'count': len(users)}).encode('utf-8'))

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8000), BotHandler)
    print("🌐 เปิดเว็บเซิร์ฟเวอร์ที่: http://127.0.0.1:8000")
    server.serve_forever()