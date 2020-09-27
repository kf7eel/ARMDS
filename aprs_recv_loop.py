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
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
###############################################################################

# Version "1", by Eric, KF7EEL

# Interactive APRS script. 
# This is a split from the shark-py-sms project to allow an APRS only setup.
# This is to accomodate users who do not use DMR but wish to still have an interactive
# messaging setup. This should work with any APRS compatable radio, even bridged DMR systems.
# https://github.com/kf7eel/shark-py-sms

# Feel free to modify and improve.

from core import *

global AIS

def aprs_packet_receive_write(packet):
    pak_str = packet.decode('utf-8',errors='ignore').strip()
        # Parse packet into dictionary
    parse_packet = aprslib.parse(pak_str)
    if 'message' == parse_packet['format']:
        if aprs_callsign == parse_packet['addresse'] and 'message_text' in parse_packet:
            with open(packet_recv_folder + str(random.randint(1000, 9999)) + '.packet', "w") as packet_write_file:
                print(pak_str)
                packet_write_file.write(pak_str)
    else:
        print('Packet from: ' + parse_packet['from'] + ' Format: ' + parse_packet['format'] + ' - ' + time.strftime('%H:%M:%S'))

    

AIS = aprslib.IS(aprs_callsign, host=aprs_is_host, passwd=aprs_passcode, port=aprs_is_port)
Path(packet_recv_folder).mkdir(parents=True, exist_ok=True)

#AIS = aprslib.IS('N0CALL', host='rotate.aprs.net', passwd='-1', port=10152)

# Sends filter settings to APRS servver
AIS.set_filter(aprs_filter)
# Connect to APRS-IS
AIS.connect()

print('APRS Receive')
print('Initializing... Waiting for packets.')
AIS.consumer(aprs_packet_receive_write, raw=True)


