import leap
import time
import sys
import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_HOST = "192.168.1.13"  # Ganti sesuai IP Raspberry Pi kamu
MQTT_PORT = 1883
MQTT_TOPIC = "leapmotion/perintah"

# Setup MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
mqtt_client.loop_start()

class MyListener(leap.Listener):
    def __init__(self):
        super().__init__()
        self.last_command = "stop"
        self.command_cooldown = 0
        
    def on_tracking_event(self, event):
        if self.command_cooldown > 0:
            self.command_cooldown -= 1
            return
            
        if len(event.hands) == 0:
            command = "stop"
        else:
            command = "stop"
            for hand in event.hands:
                thumb = hand.thumb
                index = hand.index
                middle = hand.middle
                ring = hand.ring
                pinky = hand.pinky
                
                thumb_extended = thumb.is_extended
                index_extended = index.is_extended
                middle_extended = middle.is_extended
                ring_extended = ring.is_extended
                pinky_extended = pinky.is_extended
                
                extended_fingers = sum([thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended])
                
                if extended_fingers == 5:
                    command = "maju"
                elif thumb_extended and not index_extended and not middle_extended and not ring_extended and not pinky_extended:
                    command = "mundur"
                elif thumb_extended and index_extended and not middle_extended and not ring_extended and not pinky_extended:
                    command = "kiri"
                elif thumb_extended and index_extended and middle_extended and not ring_extended and not pinky_extended:
                    command = "kanan"
                elif extended_fingers == 0:
                    command = "stop"

        if command != self.last_command:
            print(f"PERINTAH: {command.upper()}", flush=True)
            self.last_command = command
            self.command_cooldown = 10
            mqtt_client.publish(MQTT_TOPIC, command)  # Kirim via MQTT

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

    try:
        with connection.open():
            connection.set_tracking_mode(leap.TrackingMode.Desktop)
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nProgram dihentikan.")
    finally:
        connection.remove_listener(my_listener)
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    main()