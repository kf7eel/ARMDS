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

# Interactive APRS script. 
# This is a split from the shark-py-sms project to allow an APRS only setup.
# This is to accomodate users who do not use DMR but wish to still have an interactive
# messaging setup. This should work with any APRS compatable radio, even bridged DMR systems.
# https://github.com/kf7eel/shark-py-sms

# Feel free to modify and improve.

from core import *
import shutil
#from sqlite_test import *

global AIS

n = 0

db = location_db()

def aprs_packet_receive_write(packet):
    pak_str = packet.decode('utf-8',errors='ignore').strip()
        # Parse packet into dictionary
    parse_packet = aprslib.parse(pak_str)
    database_call = db.get_location(parse_packet['from'])
    #See if packet fit definition of what we want to keep coordinates for
    if 'longitude' in parse_packet: # and parse_packet['messagecapable'] == True: # == True:
        if db.exists(parse_packet['from']) == True:
            db.modify_location(parse_packet['from'], parse_packet['latitude'], parse_packet['longitude'], datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))
        if db.exists(parse_packet['from']) == False:
            db.add_location(parse_packet['from'], parse_packet['latitude'], parse_packet['longitude'], datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))
 
print(armds_intro)

try:
    db.initialize_db()
    db.add_location('N0CALL', '0', '0', 'First Entry')
except:
    print('Error, DB may already exist')
#AIS = aprslib.IS(aprs_callsign, host=aprs_is_host, passwd=aprs_passcode, port=aprs_is_port)

#AIS.set_filter(aprs_db_filter)
# Connect to APRS-IS
AIS = aprslib.IS('N0CALL', passwd='-1', host='rotate.aprs.net', port=10152)
AIS.connect()

print('APRS-IS Packet Receiver')
print('Initializing... Waiting for packets.')
n = 0
#AIS = aprslib.IS(aprs_callsign, host=aprs_is_host, passwd=aprs_passcode, port=aprs_is_port)

AIS.consumer(aprs_packet_receive_write, raw=True)
