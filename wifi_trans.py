import network
import socket
import time
import machine
import rp2
import sys

# Wi-Fi credentials
ssid = 'CMU-WLAN'
password = '301415926'

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        # Check if boot select button is pressed to allow exit.
        if rp2.bootsel_button() == 1:
            sys.exit()
        print("Waiting for Wi-Fi connection...")
        time.sleep(0.5)
    ip = wlan.ifconfig()[0]
    print("Connected on", ip)
    return ip

def measure_temperature():
    adc = machine.ADC(4)
    ADC_voltage = adc.read_u16() * (3.3 / 65535)  # Using 65535 (2^16 - 1) for precision.
    temperature_celsius = 27 - (ADC_voltage - 0.706) / 0.001721
    temperature_fahrenheit = 32 + (1.8 * temperature_celsius)
    return temperature_celsius, temperature_fahrenheit

def send_temperature_data(server_ip, temperature_c, temperature_f, port=80):
    # Create URL-encoded data
    data = "temp_c={}&temp_f={}".format(temperature_c, temperature_f)
    path = "/temperature"  # Adjust this path to match your server’s expected endpoint.
    # Construct an HTTP POST request manually
    request = (
        "POST {} HTTP/1.1\r\n"
        "Host: {}\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        "Content-Length: {}\r\n"
        "\r\n"
        "{}"
    ).format(path, server_ip, len(data), data)
    try:
        s = socket.socket()
        s.connect((server_ip, port))
        s.send(request.encode())
        response = s.recv(1024)
        print("Server response:", response)
        s.close()
    except Exception as e:
        print("Error sending data:", e)

# Connect to Wi-Fi
connect_wifi()

# Set your server IP (change this to your computer's or website's IP address)
server_ip = "192.168.31.124"  # Replace with the actual IP address

# Main loop: measure and send temperature every second
while True:
    temp_c, temp_f = measure_temperature()
    print("Temperature: {:.2f}°C, {:.2f}°F".format(temp_c, temp_f))
    send_temperature_data(server_ip, temp_c, temp_f)
    time.sleep(1)