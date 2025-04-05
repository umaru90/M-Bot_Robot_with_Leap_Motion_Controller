import leap
import time
import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_HOST = "192.168.1.13"         # IP Raspberry Pi
MQTT_PORT = 1883
MQTT_TOPIC = "leapmotion/perintah"

class MyListener(leap.Listener):
    def __init__(self, mqtt_client):
        super().__init__()
        self.last_command = "stop"
        self.command_cooldown = 0
        self.mqtt_client = mqtt_client

    def on_tracking_event(self, event):
        if self.command_cooldown > 0:
            self.command_cooldown -= 1
            return

        if len(event.hands) == 0:
            if self.last_command != "stop":
                self.send_command("stop")
                self.last_command = "stop"
            return

        hand = event.hands[0]
        x, y, z = hand.palm.position.x, hand.palm.position.y, hand.palm.position.z
        command = self.determine_command(x, y, z)

        if command != self.last_command:
            self.send_command(command)
            self.last_command = command
            self.command_cooldown = 10

    def determine_command(self, x, y, z):
        threshold_x = 50
        threshold_z = 50
        threshold_y = 50

        if abs(x) < threshold_x and abs(z) < threshold_z and y < threshold_y:
            return "stop"
        if z < -threshold_z:
            return "maju"
        if z > threshold_z:
            return "mundur"
        if x > threshold_x:
            return "kanan"
        if x < -threshold_x:
            return "kiri"
        return "stop"

    def send_command(self, command):
        print(f"[PC] Perintah dikirim: {command.upper()}", flush=True)
        self.mqtt_client.publish(MQTT_TOPIC, command)

def main():
    # Setup MQTT client
    mqtt_client = mqtt.Client()
    mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)

    my_listener = MyListener(mqtt_client)
    connection = leap.Connection()
    connection.add_listener(my_listener)

    print("\nLeap Motion MQTT kontrol aktif.")
    print("Gerakan: MAJU | MUNDUR | KIRI | KANAN | STOP")
    print("Tekan Ctrl+C untuk keluar.")

    try:
        with connection.open():
            connection.set_tracking_mode(leap.TrackingMode.Desktop)
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[PC] Program dihentikan.")
    finally:
        connection.remove_listener(my_listener)
        mqtt_client.disconnect()

if __name__ == "__main__":
    main()
