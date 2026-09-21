import http.server
import socketserver
import urllib.parse
import sqlite3
from datetime import datetime

# Inisialisasi Database SQLite Sederhana
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS laporan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            instansi TEXT NOT NULL,
            judul TEXT NOT NULL,
            tanggal TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class WebKemenagHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # 1. Halaman Utama untuk Anak Magang (Form Pengumpulan)
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'r', encoding='utf-8') as f:
                html = f.read()
            self.wfile.write(html.encode('utf-8'))

        # 2. Halaman Khusus Admin (Daftar Pengumpul & Cetak)
        elif self.path == '/admin':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM laporan ORDER BY id DESC")
            data_laporan = cursor.fetchall()
            conn.close()

            # Buat baris tabel
            tabel_html = ""
            for row in data_laporan:
                tabel_html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"

            # Render Tampilan Admin dengan Tombol Cetak
            admin_page = f'''
            <!DOCTYPE html>
            <html lang="id">
            <head>
                <meta charset="UTF-8">
                <title>Panel Admin - Laporan Magang Kemenag</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    @media print {{ .no-print {{ display: none; }} }}
                </style>
            </head>
            <body class="container py-4">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h3>Panel Admin - Rekap Pengumpulan Laporan</h3>
                    <button onclick="window.print()" class="btn btn-primary no-print">Cetak / Export PDF</button>
                </div>
                <table class="table table-bordered table-striped">
                    <thead class="table-dark">
                        <tr>
                            <th>No</th>
                            <th>Nama Peserta</th>
                            <th>Asal Kampus / Sekolah</th>
                            <th>Judul Laporan</th>
                            <th>Waktu Pengumpulan</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tabel_html if tabel_html else '<tr><td colspan="5" class="text-center">Belum ada laporan masuk</td></tr>'}
                    </tbody>
                </table>
                <a href="/" class="btn btn-secondary no-print">Kembali ke Form</a>
            </body>
            </html>
            '''
            self.wfile.write(admin_page.encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        # Proses Simpan Data dari Anak Magang
        if self.path == '/simpan':
            length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(length).decode('utf-8')
            data_form = urllib.parse.parse_qs(post_data)

            nama = data_form['nama'][0]
            instansi = data_form['instansi'][0]
            judul = data_form['judul'][0]
            waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO laporan (nama, instansi, judul, tanggal) VALUES (?, ?, ?, ?)",
                           (nama, instansi, judul, waktu_sekarang))
            conn.commit()
            conn.close()

            # Redirect balik ke halaman utama
            self.send_response(303)
            self.send_header('Location', '/?status=sukses')
            self.end_headers()

PORT = 8000
with socketserver.TCPServer(("0.0.0.0", PORT), WebKemenagHandler) as httpd:
    print(f"Server berjalan di port {PORT}")
    httpd.serve_forever()