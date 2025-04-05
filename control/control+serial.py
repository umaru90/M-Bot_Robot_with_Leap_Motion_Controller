import leap
import time
import sys
import serial
import serial.tools.list_ports


class MyListener(leap.Listener):
    def __init__(self, serial_connection):
        super().__init__()
        self.last_command = "stop"
        self.command_cooldown = 0
        self.serial_conn = serial_connection
        
    def on_connection_event(self, event):
        # Tidak menampilkan pesan koneksi
        pass

    def on_device_event(self, event):
        # Tidak menampilkan informasi perangkat
        pass

    def on_tracking_event(self, event):
        # Kurangi cooldown jika ada
        if self.command_cooldown > 0:
            self.command_cooldown -= 1
            return
            
        # Jika tidak ada tangan terdeteksi, berikan perintah stop
        if len(event.hands) == 0:
            if self.last_command != "stop":
                self.send_command("stop")
                self.last_command = "stop"
            return
            
        # Ambil tangan pertama yang terdeteksi
        hand = event.hands[0]
        hand_type = "left" if str(hand.type) == "HandType.Left" else "right"
        
        # Dapatkan posisi tangan
        x, y, z = hand.palm.position.x, hand.palm.position.y, hand.palm.position.z
        
        # Tentukan perintah berdasarkan posisi tangan
        command = self.determine_command(x, y, z)
        
        # Hanya tampilkan dan kirim perintah jika berbeda dari perintah sebelumnya
        if command != self.last_command:
            self.send_command(command)
            self.last_command = command
            self.command_cooldown = 10  # Tunggu beberapa frame sebelum perintah baru
    
    def determine_command(self, x, y, z):
        """Menentukan perintah berdasarkan posisi tangan."""
        # Nilai threshold untuk menentukan gerakan
        threshold_x = 50
        threshold_z = 50
        threshold_y = 50
        
        # Jika tangan berada di posisi netral (dekat dengan origin)
        if abs(x) < threshold_x and abs(z) < threshold_z and y < threshold_y:
            return "stop"
        
        # Jika tangan berada jauh ke depan
        if z < -threshold_z:
            return "maju"
        
        # Jika tangan berada jauh ke belakang
        if z > threshold_z:
            return "mundur"
        
        # Jika tangan berada jauh ke kanan
        if x > threshold_x:
            return "kanan"
        
        # Jika tangan berada jauh ke kiri
        if x < -threshold_x:
            return "kiri"
        
        # Default ke stop jika tidak ada kondisi yang terpenuhi
        return "stop"
    
    def send_command(self, command):
        """Mengirimkan perintah ke mikrokontroler via Serial."""
        command_codes = {
            "maju": "F",    # Forward
            "mundur": "B",  # Backward
            "kiri": "L",    # Left
            "kanan": "R",   # Right
            "stop": "S"     # Stop
        }
        
        code = command_codes.get(command, "S")  # Default ke Stop jika perintah tidak dikenali
        
        try:
            # Kirim kode perintah ke mikrokontroler
            self.serial_conn.write(code.encode())
            print(f"PERINTAH: {command.upper()} (kode: {code})", flush=True)
        except Exception as e:
            print(f"ERROR: Gagal mengirim perintah ke mikrokontroler: {e}", flush=True)


def list_serial_ports():
    """Menampilkan daftar port serial yang tersedia."""
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("Tidak ada port serial yang terdeteksi.")
        return []
    
    print("Port serial yang tersedia:")
    for i, port in enumerate(ports):
        print(f"{i+1}. {port.device} - {port.description}")
    
    return [port.device for port in ports]


def setup_serial_connection(port=None, baud_rate=9600):
    """Membuat koneksi serial ke mikrokontroler."""
    available_ports = list_serial_ports()
    
    if not available_ports:
        print("Tidak dapat melanjutkan tanpa port serial.")
        return None
    
    # Jika port tidak ditentukan, minta pengguna untuk memilih
    if port is None:
        selection = input("Pilih nomor port (1, 2, dst) atau tekan Enter untuk port pertama: ")
        
        if selection.strip() == "":
            port = available_ports[0]
        else:
            try:
                index = int(selection) - 1
                if 0 <= index < len(available_ports):
                    port = available_ports[index]
                else:
                    print("Pilihan tidak valid. Menggunakan port pertama.")
                    port = available_ports[0]
            except ValueError:
                print("Input tidak valid. Menggunakan port pertama.")
                port = available_ports[0]
    
    try:
        # Buat koneksi serial
        serial_conn = serial.Serial(port, baud_rate, timeout=1)
        print(f"Berhasil terhubung ke {port} dengan baud rate {baud_rate}")
        return serial_conn
    except Exception as e:
        print(f"ERROR: Gagal terhubung ke port serial {port}: {e}")
        return None


def main():
    # Setup koneksi serial
    serial_conn = setup_serial_connection()
    if not serial_conn:
        print("Program dihentikan karena tidak ada koneksi serial.")
        return
    
    # Berikan waktu mikrokontroler untuk melakukan reset setelah koneksi serial dibuat
    print("Menunggu mikrokontroler siap...")
    time.sleep(2)
    
    my_listener = MyListener(serial_conn)
    connection = leap.Connection()
    connection.add_listener(my_listener)

    print("\nProgram kontrol navigasi dimulai. Gunakan gerakan tangan untuk mengendalikan.")
    print("- Tangan ke depan: MAJU (F)")
    print("- Tangan ke belakang: MUNDUR (B)")
    print("- Tangan ke kiri: KIRI (L)")
    print("- Tangan ke kanan: KANAN (R)")
    print("- Tangan di tengah/tidak ada tangan: STOP (S)")
    print("Perintah dikirim ke mikrokontroler melalui koneksi serial.")
    print("Tekan Ctrl+C untuk keluar.")
    print("\nOutput perintah:")

    running = True

    try:
        with connection.open():
            connection.set_tracking_mode(leap.TrackingMode.Desktop)
            while running:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nProgram dihentikan.")
    finally:
        connection.remove_listener(my_listener)
        if serial_conn and serial_conn.is_open:
            # Kirim perintah stop saat program berakhir
            serial_conn.write("S".encode())
            serial_conn.close()
            print("Koneksi serial ditutup.")


if __name__ == "__main__":
    main()
