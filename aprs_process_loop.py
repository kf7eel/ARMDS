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

def process_loop():
    for packet_file in os.listdir(packet_process_folder):
        #print(packet_file)
        with open(packet_process_folder + packet_file) as packet_contents:
            if packet_contents != '':
                packet_content_data = packet_contents.read().strip('\n')
                print(packet_content_data)#.strip('\n'))
                aprs_receive_loop(packet_content_data) #.strip('\n'))
                os.remove(packet_process_folder + packet_file)
                time.sleep(1)
                print('processed')
            else:
                print('blank')
                pass
Path(packet_process_folder).mkdir(parents=True, exist_ok=True)

##while 4<5:
##    for packet_file in os.listdir(packet_recv_folder):
##        #print(packet_file)
##        with open(packet_recv_folder + packet_file) as packet_contents:
##            #if packet_contents != '':
##                packet_content_data = packet_contents.read().strip('\n')
##                print(packet_content_data)#.strip('\n'))
##                aprs_receive_loop(packet_content_data) #.strip('\n'))
##                os.remove(packet_recv_folder + packet_file)
##                time.sleep(0.5)
##                #i += 1
##            #else:
##              #  i = 2

print(armds_intro)

print('APRS Packet Routing and Processing')

while 4 < 5:
    process_loop()
