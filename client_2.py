import socket

# ตั้งค่า IP และ Port ของเซิร์ฟเวอร์
HOST = '127.0.0.1'  # หรือกำหนด IP ของเซิร์ฟเวอร์
PORT = 65432  # ต้องตรงกับที่เซิร์ฟเวอร์ใช้

# สร้าง TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

print(f"Connected to server {HOST}:{PORT}")

def split_data(tcp_data):
    return 'ok'

try:
    while True:
        data = client_socket.recv(1024)
        if not data:  # ถ้าไม่ได้รับข้อมูล แสดงว่าเซิร์ฟเวอร์ปิดการเชื่อมต่อ
            break
        msg = data.decode()
        if 'ok' in msg.lower():
            status = 'ok'
            print(f"Received from server: {status}")
        elif 'ng' in msg.lower():
            status = 'ng'
            print(f"Received from server: {status}")
        elif 'nm' in msg.lower():
            status = 'nm'
            print(f"Received from server: {status}")
        
except KeyboardInterrupt:
    print("\nDisconnected from server.")  # เมื่อกด Ctrl + C จะแสดงข้อความนี้
finally:
    client_socket.close()
    print("Connection closed")
