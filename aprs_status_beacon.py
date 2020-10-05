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

# ARMDS beacon/status packet upload script by Eric, KF7EEL 

# https://github.com/kf7eel/ARMDS

# Feel free to modify and improve.
from core import *
from config import *
import time
from automated_packets import *

# "APRS - unknown software, 
##loc_1_packet = aprs_callsign + '>APRS,TCPIP*:' + '=' + latitude + '/' + longitude + aprs_symbol + aprs_symbol_table + 'A=' + altitude + ' ' + aprs_1_comment
##
##loc_2_packet = aprs_callsign + '>APRS,TCPIP*:' + '=' + latitude + '/' + longitude + aprs_symbol + aprs_symbol_table + 'A=' + altitude + ' ' + aprs_2_comment
##
##loc_3_packet = aprs_callsign + '>APRS,TCPIP*:' + '=' + latitude + '/' + longitude + aprs_symbol + aprs_symbol_table + 'A=' + altitude + ' ' + aprs_3_comment
##
##loc_4_packet = aprs_callsign + '>APRS,TCPIP*:' + '=' + latitude + '/' + longitude + aprs_symbol + aprs_symbol_table + 'A=' + altitude + ' ' + aprs_4_comment
##
##status_1_packet = aprs_callsign + '>APRS,TCPIP*:' + '>' + aprs_status_text_1
##
##status_2_packet = aprs_callsign + '>APRS,TCPIP*:' + '>' + aprs_status_text_2
##
##status_3_packet = aprs_callsign + '>APRS,TCPIP*:' + '>' + aprs_status_text_3

def rand_status():
    return random.randint(1,6)

def rand_comment():
    return random.randint(1,5)
    
##def send_mult_packets(packet_1, packet_2):
##    print('Sending the following packets: ')
##    #packet_write(loc_packet)
##    #packet_write(status_packet)
##    print(packet_1)
##    print(packet_2)

print(armds_intro)

print('APRS Beacon Packets')
while 4 < 5:
    #print(packet.send_my_position(comments[rand_comment()]))
    packet_write(packet.send_my_position(comments[rand_comment()]))
    time.sleep(2)
    #print(packet.send_my_status(status[rand_status()]))
    packet_write(packet.send_my_status(status[rand_status()]))
    time.sleep(beacon_status_interval)

