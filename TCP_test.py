import socket,time

# ตั้งค่า IP และ Port ของเซิร์ฟเวอร์
HOST = '127.0.0.1'  # หรือกำหนด IP ของเซิร์ฟเวอร์
PORT = 65432  # ต้องตรงกับที่เซิร์ฟเวอร์ใช้

# สร้าง TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

print(f"Connected to server {HOST}:{PORT}")

try:
    start, end = 1,5000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        for i in range(start, end + 1):
                message = (f"7H54 TMSC64695 P/N {i} {end} CHENNAI,INDIA MADE IN THAILAND 20250215 100847").format(i=i, end=end)
                msg_2 = (f"ZMBSD0020_002_01        TMSC64623     1       5      SELANGOR,MALAYSIA     60        17PS-M058-G3W    09-0029048     7475002589**7H54 TMSC64697 P/N {i} {end} CHENNAI,INDIA MADE IN THAILAND 20250215 100847**ZMBSD0020_002_01        TMSC64623     1       5      SELANGOR,MALAYSIA     60        17PS-M058-G3W    09-0029048     7475002589").format(i=i, end=end)
                # client_socket.sendall(message.encode('utf-8'))
                
                client_socket.sendall(msg_2.encode('utf-8'))
                time.sleep(0.5)
                client_socket.sendall("NoRead".encode('utf-8'))
                print(f"Sent: {message}")
                time.sleep(0.5)
finally:
    client_socket.close()
    print("Connection closed")