#!/usr/bin/python3

###############################################################################
#   Copyright (C) 2020 Eric Craw, KF7EEL <kf7eel@qsl.net>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
##
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
###############################################################################

# Modified 09-26-2020, by Eric, KF7EEL

# Required for sending packets
# APRS receive script and required for APRS interactive script.

import os
from core import *

#global AIS

##print(aprs_callsign)
##print(aprs_passcode)
##print(aprs_is_send_host)
##print(aprs_is_send_port)
send_AIS = aprslib.IS(aprs_callsign, passwd=aprs_passcode,host=aprs_is_send_host, port=aprs_is_send_port)
#send_AIS.set_filter(aprs_filter)

print(armds_intro)

send_AIS.connect()

print('APRS-IS Packet Upload')
print('Initialized. Waiting to send packets.')
#Start loop, execute every second
Path(packet_send_folder).mkdir(parents=True, exist_ok=True)
while 4<5:
    time.sleep(1)
    #Loop through packet file driectroy to read, send, and delete packets
    for packet_file in os.listdir(packet_send_folder):
        #print(packet_file)
        with open(packet_send_folder + packet_file) as packet_contents:
            upload_packet = packet_contents.read().strip('\n')
            print(upload_packet)
            send_AIS.sendall(upload_packet)
            os.remove(packet_send_folder + packet_file)
            time.sleep(0.25)


