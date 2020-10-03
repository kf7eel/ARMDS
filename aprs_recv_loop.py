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
    if 'messagecapable' in parse_packet: #== True:
        if db.exists(parse_packet['from']) == True:
            db.modify_location(parse_packet['from'], parse_packet['latitude'], parse_packet['longitude'], time.strftime('%H:%M:%S'))
        if db.exists(parse_packet['from']) == False:
            db.add_location(parse_packet['from'], parse_packet['latitude'], parse_packet['longitude'], time.strftime('%H:%M:%S'))
        
    elif 'message' == parse_packet['format']:
        if aprs_callsign == parse_packet['addresse'] and 'message_text' in parse_packet:
            with open(packet_recv_folder + str(random.randint(1000, 9999)) + '.packet', "w") as packet_write_file:
                print(pak_str)
                packet_write_file.write(pak_str)
                #os.system('mv ' + packet_write_file + ' ' + packet_process_folder)
        #os.system('mv ' + packet_write_file + ' ' + packet_process_folder)
            #shutil.move(packet_recv_folder + '*', packet_process_folder)


    # Note to self, try mv in for loop, after you get off work
        
##        try:
##            os.system('mv ' + packet_recv_folder + '*.packet ' + packet_process_folder)
##        except:
##            print('excepted, no files?')

    else:
        print('Packet from: ' + parse_packet['from'] + ' Format: ' + parse_packet['format'] + ' - ' + time.strftime('%H:%M:%S'))
    try:
        for pckt in os.listdir(packet_recv_folder):
            print(pckt)
            #os.system('mv ' + packet_recv_folder + pckt + ' ' + packet_process_folder)
            shutil.copyfile(packet_recv_folder + pckt, packet_process_folder + pckt)
            os.remove(packet_recv_folder + pckt)
            #print('packet moved')
    except:
            print('error with moving')

    #shutil.move(packet_recv_folder + '*', packet_process_folder)
AIS = aprslib.IS(aprs_callsign, host=aprs_is_host, passwd=aprs_passcode, port=aprs_is_port)
Path(packet_recv_folder).mkdir(parents=True, exist_ok=True)

#AIS = aprslib.IS('N0CALL', host='rotate.aprs.net', passwd='-1', port=10152)

# Sends filter settings to APRS server
print(armds_intro)

try:
    db.initialize_db()
    db.add_location('N0CALL', '0', '0', 'First Entry')
except:
    print('Error, DB may already exist')

AIS.set_filter(aprs_filter)
# Connect to APRS-IS
AIS.connect()

print('APRS-IS Packet Receiver')
print('Initializing... Waiting for packets.')
n = 0
AIS.consumer(aprs_packet_receive_write, raw=True)


