import network
import dht
from machine import ADC, Pin , PWM
import time
import urequests
# Setup PWM on GPIO pin 15 (change as needed)
servo = PWM(Pin(15))
   
# Initialize sensors and actuators
adc = ADC(Pin(26))
sensor = dht.DHT11(Pin(1))
mot = Pin(2, Pin.OUT)
mot1 = Pin(14, Pin.OUT)

# Set the frequency to 50Hz (common for servos)
servo.freq(50)

# Function to set the servo angle
def set_angle(angle):
    if angle < 0 or angle > 180:
        raise ValueError("Angle must be between 0 and 180 degrees")
   
    # Calculate pulse width (in microseconds) for the given angle
    pulse_width = int((angle / 180.0 * 2) + 1) * 1000
   
    # Convert pulse width to duty cycle (0-65535)
    duty_cycle = int(pulse_width / 20000 * 65535)
   
    # Set the duty cycle
    servo.duty_u16(duty_cycle)

# Function to move the servo to a specified angle and then stop
def move_and_hold(angle, hold_time):
    try:
        # Move servo to the specified angle
        set_angle(angle)
        print(f"Moved to {angle} degrees")
       
        # Hold the position for the specified amount of time
        time.sleep(hold_time)
       
        # After holding time, stop sending PWM signals to effectively stop the motor
        servo.duty_u16(0)
        print(f"Servo stopped after holding at {angle} degrees for {hold_time} seconds")
       
    except KeyboardInterrupt:
        # Clean up on Ctrl+C
        servo.duty_u16(0)  # Turn off PWM
        print("Servo stopped")


# Wi-Fi credentials
ssid = 'LBRCE-RAKBH'
password = ''

# Connect to Wi-Fi
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    time.sleep(1)
    print("Connecting to Wi-Fi...")

print('Connection successful')
print(station.ifconfig())

# Function to read water level
def read_water_level():
    analog_value = adc.read_u16()
    voltage = analog_value * 3.5 / 65535
    return voltage

# Function to read sensors and control actuators
def read_sensors():
    try:
        sensor.measure()
        temp = sensor.temperature()
        humidity = sensor.humidity()

        if temp is not None and humidity is not None:
            print("Temperature: {}°C Humidity: {}%".format(temp, humidity))
        else:
            print("Failed to read DHT sensor data")

    except OSError as e:
        print('Error reading DHT sensor:', e)

    try:
        water_level = read_water_level()
        print("Water Level Voltage:", water_level)
    except OSError as e:
        print('Error reading ADC:', e)
    if(temp>24):
        cooler="ON"
        mot1.value(1)
    else:
        if(humidity>30):
            cooler="ON"
            mot1.value(1)
        else:
            cooler="OFF"
            mot1.value(0)
    if(water_level<2.8):
        motor="ON"
        move_and_hold(90, 5)
        time.sleep(1)  # Wait 2 seconds before moving again
        move_and_hold(0, 5) # Move to 180 degrees and hold for 5 seconds
        time.sleep(1)
    else:
        motor="OFF"
        servo.duty_u16(0)

    # Sending data to the server
    try:
        url = "http://10.10.20.141:8888/update"
        data = {
            'data1': temp,
            'data2': humidity,
            'data3': water_level,
            'data4': motor,
            'data5': cooler
        }
        response = urequests.post(url, json=data)
        print("Server response code:", response.status_code)
        print("Server response text:", response.text)
       
    except Exception as e:
        print('Error sending data to server:', e)

while True:
    try:
        read_sensors()
        time.sleep(1)  # Adjust delay as needed
    except Exception as e:
        print('Error in main loop:', e)
        time.sleep(1)
 
