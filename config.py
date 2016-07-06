# address of the USB serial port for the IMUs. If you provide a list it will
# try each in turn until one works or the list is exhausted.
serial_port = [ '/dev/tty.usbserial-FTR9ZM99', 'COM5:', 'COM7:' ]

# IP/hostname to bind the TiA server (empty string means use all local interfaces)
tia_server_ip      = ''

# port number that the TiA server will run on (change this if it clashes with
# the TOBI signal server!)
tia_server_port    = 9000

# indices of the 2 IMUs to use for relative tilt calculations:
#   IMU 1 = sensor closest to the SHAKE
#   IMU 5 = sensor furthest from the SHAKE (end of the cable)
relative_imus      = [1, 3]

# enable/disable sending basic tilt output for each IMU (-90..+90 degrees)
basic_tilt_outputs = True
