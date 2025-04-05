import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_HOST = "192.168.1.13"  # IP Raspberry Pi (bisa 'localhost' jika broker juga di sini)
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "robot/control"

# Define on_connect event Handler
def on_connect(mosq, obj, flags, rc):
    print("[PI] Terhubung ke broker.")
    mqttc.subscribe(MQTT_TOPIC, 0)

# Define on_subscribe event Handler
def on_subscribe(mosq, obj, mid, granted_qos):
    print("[PI] Berlangganan ke topik:", MQTT_TOPIC)

# Define on_message event Handler
def on_message(mosq, obj, msg):
    command = msg.payload.decode()
    print(f"[PI] Perintah diterima: {command.upper()}")

    # Contoh: Tambahkan aksi berdasarkan perintah
    if command == "maju":
        print("[PI] Robot maju")
    elif command == "mundur":
        print("[PI] Robot mundur")
    elif command == "kiri":
        print("[PI] Robot belok kiri")
    elif command == "kanan":
        print("[PI] Robot belok kanan")
    elif command == "stop":
        print("[PI] Robot berhenti")

# Initiate MQTT Client
mqttc = mqtt.Client()

# Register Event Handlers
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe

# Connect with MQTT Broker
mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

# Start the loop
mqttc.loop_forever()
