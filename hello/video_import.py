import io
import cv2
import socket
import struct
import numpy as np

def send_command(connection, command):
    connection.sendall(command.encode())

# Create a socket and connect to the raspberry pi
client_socket = socket.socket()
client_socket.connect(('raspberry_pi_ip_address', 8000)) # fill in withh rpi static IP

connection = client_socket.makefile('rb')

try:
    while True:
        # Read the length of the image as a 32-bit unsigned int.
        image_len = struct.unpacc('<L', connection.read(struct.calcsize('<L')))[0]
        
        # Contruct a stream to hold the imadge data and read the image data
        image_stream = io.BytesIO(connection.read(image_len))
        
        # Convert the image stream to a numpy array
        image_array = np.frombuffer(image_stream.getvalue(), dtype=np.uint8)
        
        # decode the numpy array to an OpenCV image
        image = cv2.imdecode(image_array, 1)
        
        # Display the image
        cv2.imshow('Video Stream', image)
        # Waits for a key press to start streaming
        cv2.waitKey(1)
        
        # Send command to the rpi
        command = input("Enter command: ")
        send_command(connection, command)
        
        # Check for an exit command
        if command == "EXIT":
            print("Exiting...")
            break

finally:
    connection.close()
    client_socket.close()