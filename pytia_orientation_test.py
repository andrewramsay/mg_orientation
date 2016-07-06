import time, sys, itertools

from pyshake import *
import pytia
from pytia import TiAServer, TiAConnectionHandler, TiASignalConfig

import config

def basic_callback(sig_id):
    sd = sig_id[0]
    imudata = sd.sk7_imus()
    # do a very basic angle calculation based on x-axis accelerometer
    tilts = [imu.acc[0] for imu in imudata]
    return map(lambda x: int((x / 1000.0) * 90.0), tilts)

def relative_callback(sig_id):
    sd = sig_id[0]
    imudata = sd.sk7_imus()
    
    # calculate relative angle between the two selected IMUs
    tilts = [imudata[i].acc[0] for i in config.relative_imus]

    # return integer value in the range 1-64, where:
    #   32  = flat
    #   1 = max supination
    #   64 = max pronation
    relative_tilt = tilts[1] - tilts[0]

    # raw value will be in range -1000 -- 1000, so scale that to fit output range
    # (not exactly but should be close enough)
    scaled_tilt = int( (-relative_tilt + 1000) * (32 / 1000.0) )
    # make sure it's positive
    scaled_tilt = abs(scaled_tilt)
    # clamp to the exact range required
    scaled_tilt = min(64, scaled_tilt)
    scaled_tilt = max(1, scaled_tilt)
    
    # print('Relative / Scaled: %.3f %d' % (relative_tilt, scaled_tilt))

    return [scaled_tilt]

def open_port(address):
    sd = ShakeDevice(SHAKE_SK7)
    print('Attempting to open port "%s"' % address)
    if len(sys.argv) >= 2:
        address = sys.argv[1]
        try:
            address = int(address)
            print('Using integer port number %d' % address)
        except ValueError:
            pass

    print('Connecting to address "' + str(address) + '"')
    if not sd.connect(address):
        print('Failed to connect to ' + str(address) + '"')
        return None
    print('Connected to address "' + str(address) + '"')
    return sd

if __name__ == "__main__":
    sd = None
    if isinstance(config.serial_port, list):
        print('Got a list of ports, checking each one...')
        for port in config.serial_port:
            sd = open_port(port)
            if sd != None:
                break
    else:
        sd = open_port(config.serial_port)

    if sd == None:
        print('Failed to open a serial port')
        sys.exit(-1)

    # create a TiAServer on the specified address
    server = TiAServer((config.tia_server_ip, config.tia_server_port), TiAConnectionHandler)

    signals = []
    relative_signal = TiASignalConfig(channels=1, sample_rate=100, blocksize=1, \
                            callback=relative_callback, id=(sd,), is_master=True, \
                            sigtype=pytia.TIA_SIG_USER_1)
    signals.append(relative_signal)

    if config.basic_tilt_outputs:
        # basic tilt signal for all IMUs
        basic_signal = TiASignalConfig(channels=5, sample_rate=100, blocksize=1, \
                                callback=basic_callback, id=(sd,), is_master=False, \
                                sigtype=pytia.TIA_SIG_USER_2)
        signals.append(basic_signal)

    # start the server with the list of signals to use
    server.start(signals)

    print('[Ctrl-C to exit]')
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('Closing connection...')

    sd.close()
