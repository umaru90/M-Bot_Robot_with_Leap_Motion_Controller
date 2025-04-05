import leap
import time
import sys

class MyListener(leap.Listener):
    def __init__(self):
        super().__init__()
        self.last_command = "stop"
        self.command_cooldown = 0
        
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
                print("PERINTAH: STOP", flush=True)
                self.last_command = "stop"
            return
            
        # Ambil tangan pertama yang terdeteksi
        hand = event.hands[0]
        hand_type = "left" if str(hand.type) == "HandType.Left" else "right"
        
        # Dapatkan posisi tangan
        x, y, z = hand.palm.position.x, hand.palm.position.y, hand.palm.position.z
        
        # Tentukan perintah berdasarkan posisi tangan
        command = self.determine_command(x, y, z)
        
        # Hanya tampilkan perintah jika berbeda dari perintah sebelumnya
        if command != self.last_command:
            print(f"PERINTAH: {command.upper()}", flush=True)
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


def main():
    my_listener = MyListener()

    connection = leap.Connection()
    connection.add_listener(my_listener)

    print("Program kontrol navigasi dimulai. Gunakan gerakan tangan untuk mengendalikan.")
    print("- Tangan ke depan: MAJU")
    print("- Tangan ke belakang: MUNDUR")
    print("- Tangan ke kiri: KIRI")
    print("- Tangan ke kanan: KANAN")
    print("- Tangan di tengah/tidak ada tangan: STOP")
    print("Tekan Ctrl+C untuk keluar.")
    print("\nOutput perintah:")

    running = True

    try:
        with connection.open():
            connection.set_tracking_mode(leap.TrackingMode.Desktop)
            while running:
                time.sleep(0.1)  # Kurangi interval sleep untuk respons lebih cepat
    except KeyboardInterrupt:
        print("\nProgram dihentikan.")
    finally:
        connection.remove_listener(my_listener)


if __name__ == "__main__":
    main()
