import socket,json,time,os,shutil

# ตั้งค่า IP และ Port ของเซิร์ฟเวอร์
HOST = '127.0.0.1'  # หรือกำหนด IP ของเซิร์ฟเวอร์
PORT = 65432  # ต้องตรงกับที่เซิร์ฟเวอร์ใช้
record_path = r"record.env"
show_path = r"show.env"
# สร้าง TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

print(f"Connected to server {HOST}:{PORT}")

def split_data(tcp_data):
    # print("TCP_data: ", tcp_data)
    star_part = tcp_data.split('**')  # แยกข้อมูลด้วย '**'
    # print("star_part: ",star_part)
    for idx, part in enumerate(star_part):
        tab_part = part.split()  # แยกข้อมูลในแต่ละส่วนด้วยช่องว่าง
        count = get_count_from_env(record_path)
        invoice_master = get_invoice_master(record_path)
        total_master = get_total_master(record_path)

        if(tab_part[0] == 'NoRead' ):
            if count == 0:
                error_msg = f"Cannot read frist pallet"
            else:
                error_msg = f"Cannot read after {get_box_number(record_path)}/{total_master}" #6
            msg_color = 'white' #8
            msg_bg = 'red' #9
            out_status = 'ng' #10
        elif tab_part[2] == 'P/N':
            
            invoice_number = tab_part[1]
            pallet_number = tab_part[3]
            pallet_total = tab_part[4]
            model = tab_part[9]
            print(count)
            if count == 0:
                error_msg = f"Read success {pallet_number}/{pallet_total} and set {invoice_number} to be master" #6
                msg_color = 'white' #8
                msg_bg = 'green' #9
                out_status = 'ok' #10
                record_env(tab_part,invoice_number,pallet_total,count,model,pallet_number)
            elif(invoice_number == invoice_master and count < total_master):
                print("check_env: ",check_env(invoice_number, pallet_number,record_path))
                if(check_env(invoice_number, pallet_number,record_path)): #ถ้าไม่มีใน record.env
                    error_msg = f"Read success {pallet_number}/{pallet_total}" #6
                    msg_color = 'white' #8
                    msg_bg = 'green' #9
                    out_status = 'ok' #10
                    record_env(tab_part,invoice_number,pallet_total,count,model,pallet_number)
                else:
                    error_msg = f"Duplicated {pallet_number}/{pallet_total}" #6
                    msg_color = 'black' #8
                    msg_bg = 'yellow' #9
                    out_status = 'nm' #10
            break
        elif(idx == len(star_part) - 1):
            print("last")
            if count == 0:
                error_msg = f"Cannot read frist pallet"
            else:
                error_msg = f"Cannot read after {get_box_number(record_path)}/{total_master}" #6
            msg_color = 'white' #8
            msg_bg = 'red' #9
            out_status = 'ng' #10
    # print("error_msg: ",error_msg)
    count = get_count_from_env(record_path)
    total_master = get_total_master(record_path)
    if count <=0:
        invoice_master = ''
        total_master_show = ''
        total_master = 0
        count_show = ''
        model = ''
        model_show = ''
        box_number = 0
        box_number_show = ''
        if error_msg == "Loading sucess!":
            error_msg = ''
            msg_bg = 'white'
    else:
        invoice_master = get_invoice_master(record_path)
        total_master_show = get_total_master(record_path)
        box_number_show = get_box_number(record_path)
        count_show = f"{count}/{total_master}"
        model_show = get_model(record_path)
    print("count: ",count)
    if(count >= total_master and count != 0):
        record_to_store(record_path)
        # time.sleep(0.1)
        # if not (record_to_db(record_path)):
        #     record_to_store(record_path)
        #     error_msg = "cannot save to database,Save at storage" #6
        #     msg_color = 'white' #8
        #     msg_bg = 'yellow' #9
        # else:
        error_msg = "Loading sucess!" #6
        msg_color = 'white' #8
        msg_bg = 'green' #9
        delete_from_env(record_path)
        time.sleep(0.2)
    conv_status = 'run'
    save_to_show(invoice_master,total_master_show,count_show,model_show,box_number_show,error_msg,conv_status,msg_color,msg_bg,show_path)
    print(out_status)
    return out_status

def get_count_from_env(path):
    try:
        with open(path, "r") as file:
            count_in_env = sum(1 for _ in file)  # นับจำนวนบรรทัดในไฟล์
            # print("count_in_env: ",count_in_env)
        return count_in_env
    except FileNotFoundError:
        return 0  # ถ้าไฟล์ไม่มีอยู่ให้คืนค่า 0

def get_invoice_master(path):
    # print("call: get_invoice_master()")
    try:
        with open(path, "r") as file:
            # อ่านบรรทัดทั้งหมดแล้วเลือกบรรทัดสุดท้าย
            lines = file.readlines()
            if lines:
                last_line = lines[-1].strip()  # ดึงบรรทัดสุดท้าย
                # แยกข้อมูลด้วย ' | ' แล้วแปลงเป็น dictionary
                record_data = dict(item.split("=") for item in last_line.split(" | "))
                # ตรวจสอบและแปลง Invoice_Master ถ้ามีค่า
                invoice_master = record_data.get("Invoice_Master", "").strip()
                if invoice_master:
                    # แยกค่าจากสตริงถ้ามีการแสดงเป็นลิสต์
                    invoice_master = invoice_master.strip('[]').split(',')
                # print("invoice_master", invoice_master[0])
                return invoice_master[0] if invoice_master else ''
            else:
                return ''  # ถ้าไฟล์ว่าง
    except FileNotFoundError:
        return ''  # ถ้าไฟล์ไม่มี ให้คืนค่าเริ่มต้น
    except Exception as e:
        print(f"Error: {e}")
        return ''  # ในกรณีที่เกิดข้อผิดพลาดอื่นๆ

def get_total_master(path):
    # print("call: get_total_master()")
    try:
        with open(record_path, "r") as file:
            # อ่านบรรทัดทั้งหมดแล้วเลือกบรรทัดสุดท้าย
            lines = file.readlines()
            if lines:
                last_line = lines[-1].strip()  # ดึงบรรทัดสุดท้าย
                # แยกข้อมูลด้วย ' | ' แล้วแปลงเป็น dictionary
                record_data = dict(item.split("=") for item in last_line.split(" | "))
                # ใช้ eval() เพื่อแปลงเป็น list หรือ dictionary
                total_master = int(record_data.get("Total_Master", "[]").strip())
                return total_master
            else:
                return 0  # ถ้าไฟล์ว่าง
    except FileNotFoundError:
        return 0  # ถ้าไฟล์ไม่มี ให้คืนค่าเริ่มต้น
    except Exception as e:
        print(f"Error: {e}")
        return 0  # ในกรณีที่เกิดข้อผิดพลาดอื่นๆ

def get_model(path):
    # print("call: get_model()")
    try:
        with open(path, "r") as file:
            # อ่านบรรทัดทั้งหมดแล้วเลือกบรรทัดสุดท้าย
            lines = file.readlines()
            if lines:
                last_line = lines[-1].strip()  # ดึงบรรทัดสุดท้าย
                # แยกข้อมูลด้วย ' | ' แล้วแปลงเป็น dictionary
                record_data = dict(item.split("=") for item in last_line.split(" | "))
                # ตรวจสอบและแปลง Invoice_Master ถ้ามีค่า
                model = record_data.get("Model", "").strip()
                if model:
                    # แยกค่าจากสตริงถ้ามีการแสดงเป็นลิสต์
                    model = model.strip('[]').split(',')
                print("model", model[0])
                return model[0] if model else ''
            else:
                return ''  # ถ้าไฟล์ว่าง
    except FileNotFoundError:
        return ''  # ถ้าไฟล์ไม่มี ให้คืนค่าเริ่มต้น
    except Exception as e:
        print(f"Error: {e}")
        return ''  # ในกรณีที่เกิดข้อผิดพลาดอื่นๆ

def get_box_number(path):
    # print("call: get_box_number()")
    try:
        with open(record_path, "r") as file:
            # อ่านบรรทัดทั้งหมดแล้วเลือกบรรทัดสุดท้าย
            lines = file.readlines()
            if lines:
                last_line = lines[-1].strip()  # ดึงบรรทัดสุดท้าย
                # แยกข้อมูลด้วย ' | ' แล้วแปลงเป็น dictionary
                record_data = dict(item.split("=") for item in last_line.split(" | "))
                # ใช้ eval() เพื่อแปลงเป็น list หรือ dictionary
                box_number = int(record_data.get("Box_number", "[]").strip())
                return box_number
            else:
                return 0  # ถ้าไฟล์ว่าง
    except FileNotFoundError:
        return 0  # ถ้าไฟล์ไม่มี ให้คืนค่าเริ่มต้น
    except Exception as e:
        print(f"Error: {e}")
        return 0  # ในกรณีที่เกิดข้อผิดพลาดอื่นๆ

def get_status_msg_from_file(file_path):
    try:
        # เปิดไฟล์และอ่านบรรทัดสุดท้าย
        with open(file_path, 'r') as file:
            lines = file.readlines()
            last_line = lines[-1].strip()  # เอาบรรทัดสุดท้ายและลบช่องว่างที่ไม่จำเป็น

        # แปลงข้อมูล JSON ในบรรทัดสุดท้ายเป็น Python dictionary
        data = json.loads(last_line)

        # ดึงค่า 'Status_msg'
        status_msg = data.get("Status_msg", '')

        return status_msg

    except Exception as e:
        print(f"Error reading file: {e}")
        return ''

def get_msg_bg_from_file(file_path):
    try:
        # เปิดไฟล์และอ่านบรรทัดสุดท้าย
        with open(file_path, 'r') as file:
            lines = file.readlines()
            last_line = lines[-1].strip()  # เอาบรรทัดสุดท้ายและลบช่องว่างที่ไม่จำเป็น

        # แปลงข้อมูล JSON ในบรรทัดสุดท้ายเป็น Python dictionary
        data = json.loads(last_line)

        # ดึงค่า 'msg_bg'
        msg_bg = data.get("msg_bg", 'red')

        return msg_bg

    except Exception as e:
        return f"Error reading file: {e}"

def record_env(barcode,invoice_number,box_total,count,model,box_number):
    # print("call: record_env()")
    record_data = {
        "Out_qrcode":barcode,
        "Invoice_Master":invoice_number,
        "Total_Master":box_total,
        "Count":count,
        "Model":model,
        "Box_number":box_number,
    }
    # print("record_data: ",record_data)
        # แปลง record_data เป็นข้อความ 1 บรรทัดโดยใช้ ' | ' เป็นตัวคั่น
    record_line = " | ".join(f"{key}={value}" for key, value in record_data.items())
    if not os.path.exists(record_path):
        print(f"File {record_path} does not exist. Creating a new file.")
    # บันทึกข้อมูลลงไฟล์
    try:
        with open(record_path, "a") as file:
            file.write(record_line + "\n")
            file.flush()
            print(f"Data successfully written to {record_path}")
    except Exception as e:
        print(f"Error writing to file: {e}")
        return False
    return True

def save_to_show(invoice_master_value,total_master_show,count_show,model_value,box_number_show,error_msg,conv_msg,msg_color,msg_bg,show_path):
    # print("call: save_to_show()")
    json_show = {
        "Invoice_Master": invoice_master_value,
        "Total_Master": total_master_show,
        "Count": count_show,
        "Model": model_value,  # model ไม่ถูกใช้งานในโค้ดเดิม
        "Box_number": box_number_show,
        "Status_msg": error_msg,
        "Status_conveyor": conv_msg,
        "msg_color": msg_color,   # เพิ่ม msg_color
        "msg_bg": msg_bg,         # เพิ่ม msg_bg
    }
    json_data = json.dumps(json_show)
    # กำหนด path ของไฟล์
    if not is_data_exists(show_path, json_data):
        with open(show_path, 'w') as f:
            f.write(json_data)
        print("Data saved to show.env")
    else:
        print("Data already exists, not saving again")

def is_data_exists(file_path, data):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            file_data = f.read()
            # เปรียบเทียบข้อมูลในไฟล์กับข้อมูลใหม่
            return file_data == data
    return False

def check_env(invoice_number, box_number,record_path):
    # print("call: check_env()")
    try:
        with open(record_path, "r") as file:
            for line in file:
                # แปลงข้อมูลเป็น dictionary
                record_data = dict(item.split("=") for item in line.strip().split(" | "))

                # แปลงค่าจาก string ให้เป็น list (ถ้าข้อมูลมีหลายตัวอักษรให้ใช้ .split())
                record_invoice = record_data.get("Invoice_Master", "").strip()
                record_box = record_data.get("Box_number", "").strip()
                # เปรียบเทียบค่า
                if str(record_invoice) == str(invoice_number) and int(record_box) == int(box_number):
                    return False #False  # พบข้อมูลที่ตรงกัน

        return True  # ไม่พบข้อมูลที่ตรงกัน
    except FileNotFoundError:
        return False  # หากไฟล์ไม่มีอยู่ ให้คืนค่า False

def delete_from_env(record_path):
    # print("call: delete_from_env")
    try:
        # เปิดไฟล์ในโหมด "w" (write) เพื่อเขียนทับข้อมูลเป็นค่าว่าง
        with open(record_path, "w") as file:
            pass  # ไม่ต้องเขียนอะไรลงไป (ทำให้ไฟล์ว่างเปล่า)
        # return True
    except Exception as e:
        print(f"Error: {e}")

def record_to_store(path):
    # print("call: record_to_store()")
    invoice_master = get_invoice_master(path)
    try:
    # สร้างชื่อไฟล์ใหม่
        destination_folder = r"store"
        os.makedirs(destination_folder, exist_ok=True)  # สร้างโฟลเดอร์ถ้ายังไม่มี
        destination_path = os.path.join(destination_folder, f"{invoice_master}_store.env")

        # ตรวจสอบว่าไฟล์ต้นทางมีอยู่หรือไม่
        if not os.path.exists(path):
            print(f"Error: Source file '{path}' does not exist.")
            return

        # คัดลอกข้อมูลจาก record.env ไปยังไฟล์ใหม่
        shutil.copy(record_path, destination_path)
        print(f"File '{destination_path}' created successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:  # ถ้าไม่ได้รับข้อมูล แสดงว่าเซิร์ฟเวอร์ปิดการเชื่อมต่อ
                break
            msg = data.decode()
            out_status = split_data(msg)
            client_socket.sendall(out_status.encode('utf-8')) #sent data to server
            # print(f"Received from server: {msg}")
    except KeyboardInterrupt:
        print("\nDisconnected from server.")  # เมื่อกด Ctrl + C จะแสดงข้อความนี้
    finally:
        client_socket.close()
        print("Connection closed")

if __name__ == "__main__":
    main()
