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

        # Ambil jari-jari dari tangan
        thumb = hand.thumb
        index = hand.index
        middle = hand.middle
        ring = hand.ring
        pinky = hand.pinky

        # Hitung jumlah jari yang terentang
        extended_fingers = 0
        if thumb.is_extended:
            extended_fingers += 1
        if index.is_extended:
            extended_fingers += 1
        if middle.is_extended:
            extended_fingers += 1
        if ring.is_extended:
            extended_fingers += 1
        if pinky.is_extended:
            extended_fingers += 1

        # Tentukan perintah berdasarkan jumlah jari
        if extended_fingers == 5:
            command = "maju"
        elif extended_fingers == 4:
            command = "mundur"
        elif extended_fingers == 2:  # 2 jari terentang -> kiri
            command = "kiri"
        elif extended_fingers == 3:  # 3 jari terentang -> kanan
            command = "kanan"
        else:
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

    print("Program kontrol navigasi dimulai. Gunakan gerakan tangan untuk mengendalikan.")
    print("- 5 jari terentang: MAJU")
    print("- 4 jari terentang: MUNDUR")
    print("- 2 jari terentang: KIRI")
    print("- 3 jari terentang: KANAN")
    print("- Jari dikepal: STOP")
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