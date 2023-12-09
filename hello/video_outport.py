# To be used on raspberry pi

import io
import picamera
import socket
import struct
import time
#import RPi.GPIO as GPIO

# GPIO configuration for motor control
motor1_pwm_pin = 17
motor1_dir_pin1 = 27
motor1_dir_pin2 = 22

motor2_pwm_pin = 18
motor2_dir_pin1 = 23
motor2_dir_pin2 = 24

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.steup(motor1_pwm_pin, GPIO.OUT)
GPIO.setup(motor1_dir_pin1, GPIO.OUT)
GPIO.setup(motor1_dir_pin2, GPIO.OUT)

GPIO.steup(motor2_pwm_pin, GPIO.OUT)
GPIO.setup(motor2_dir_pin1, GPIO.OUT)
GPIO.setup(motor2_dir_pin2, GPIO.OUT)

# PWM setup
motor1_pwm = GPIO.PWM(motor1_pwm_pin, 100)
motor2_pwm = GPIO.PWM(motor2_pwm_pin, 100)

# defines send_command as a variable where 
def send_command(connection, command):
    connection.sendall(command.encode())

def steer_left():
    GPIO.output(motor1_dir_pin1, GPIO.HIGH)
    GPIO.output(motor1_dir_pin2, GPIO.LOW)
    motor1_pwm.start(50) # Adjust PWM duty cycle to function properly
    
    GPIO.output(motor2_dir_pin1, GPIO.HIGH)
    GPIO.output(motor2_dir_pin2, GPIO.LOW)
    motor2_pwm.start(50) # Adjust PWM duty cycle to function properly
    
def steer_right():
    GPIO.output(motor1_dir_pin1, GPIO.LOW)
    GPIO.output(motor1_dir_pin2, GPIO.HIGH)
    motor1_pwm.start(50) # Adjust PWM duty cycle to function properly
    
    GPIO.output(motor2_dir_pin1, GPIO.LOW)
    GPIO.output(motor2_dir_pin2, GPIO.HIGH)
    motor2_pwm.start(50) # Adjust PWM duty cycle to function properly

def forwards():
    GPIO.output(motor1_dir_pin1, GPIO.HIGH)
    GPIO.output(motor1_dir_pin2, GPIO.LOW)
    motor1_pwm.start(50) # Adjust PWM duty cycle to function properly
    
    GPIO.output(motor2_dir_pin1, GPIO.LOW)
    GPIO.output(motor2_dir_pin2, GPIO.HIGH)
    motor2_pwm.start(50) # Adjust PWM duty cycle to function properly
    
def backwards():
    GPIO.output(motor1_dir_pin1, GPIO.HIGH)
    GPIO.output(motor1_dir_pin2, GPIO.LOW)
    motor1_pwm.start(50) # Adjust PWM duty cycle to function properly
    
    GPIO.output(motor2_dir_pin1, GPIO.LOW)
    GPIO.output(motor2_dir_pin2, GPIO.HIGH)
    motor2_pwm.start(50) # Adjust PWM duty cycle to function properly
    
def stop_motors():
    motor1_pwm.stop()
    motor2_pwm.stop()
    
    
# Create a socket and bind to the specified address and port
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')

try:
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        
        # Start a preview and warm up the camera for 2 seconds
        camera.start_preview()
        time.sleep(2)
        
        # Capture and stream the video indefinitely
        stream = io.BytesIO()
        for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            stream.seek(0)
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            stream.seek(0)
            connection.write(stream.read())
            stream.seek(0)
            stream.truncate()
            
            # Receive command from client
            command = connection.readline().decode().strip()
            
            # Perform actions based on the recieved command
            if command == "FORWARDS":
                forwards()
                send_command(connection, "Moving forwards")
            elif command == "BACKWARDS":
                backwards()
                send_command(connection, "Moving backwards")
            elif command == "STEER_LEFT":
                steer_left()
                send_command(connection, "Steering left")
            elif command == "STEER_RIGHT":
                steer_right()
                send_command(connection, "Steering right")
            elif command == "STOP_MOTORS":
                stop_motors()
                send_command(connection, "Motors stopped")
            elif command == "EXIT":
                send_command(connection, "Exiting...")
                break
            
finally:
    connection.close()
    server_socket.close()
    GPIO.cleanup()