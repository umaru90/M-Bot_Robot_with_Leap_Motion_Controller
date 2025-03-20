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
        
        command = "stop"  # Default command
        
        # Periksa setiap tangan yang terdeteksi
        for hand in event.hands:
            # Ambil jari-jari dari tangan
            thumb = hand.thumb
            index = hand.index
            middle = hand.middle
            ring = hand.ring
            pinky = hand.pinky
            
            # Cek status extended untuk setiap jari
            thumb_extended = thumb.is_extended
            index_extended = index.is_extended
            middle_extended = middle.is_extended
            ring_extended = ring.is_extended
            pinky_extended = pinky.is_extended
            
            # Hitung jumlah jari yang terentang
            extended_fingers = sum([thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended])
            
            # Tentukan perintah berdasarkan pola jari
            if extended_fingers == 5:
                command = "maju"
            elif thumb_extended and not index_extended and not middle_extended and not ring_extended and not pinky_extended:
                command = "mundur"
            elif thumb_extended and index_extended and not middle_extended and not ring_extended and not pinky_extended:
                command = "kiri"
            elif thumb_extended and not index_extended and middle_extended and not ring_extended and not pinky_extended:
                command = "kanan"
            elif extended_fingers == 0:
                command = "stop"
        
        # Hanya tampilkan perintah jika berbeda dari perintah sebelumnya
        if command != self.last_command:
            print(f"PERINTAH: {command.upper()}", flush=True)
            self.last_command = command
            self.command_cooldown = 10  # Tunggu beberapa frame sebelum perintah baru

def main():
    my_listener = MyListener()

    connection = leap.Connection()
    connection.add_listener(my_listener)

    print("Program kontrol navigasi dengan pola jari dimulai.")
    print("\nPetunjuk perintah:")
    print("- Semua jari terentang (5 jari): MAJU")
    print("- Hanya jempol terentang: MUNDUR")
    print("- Jempol dan telunjuk terentang: KIRI")
    print("- Jempol dan jari tengah terentang: KANAN")
    print("- Tangan dikepal (tidak ada jari terentang): STOP")
    print("\nTekan Ctrl+C untuk keluar.")
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