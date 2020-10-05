#!/usr/bin/python3

###############################################################################
#   Copyright (C) 2019 Eric Craw, KF7EEL <kf7eel@qsl.net>
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

# Packet class

# Feel free to modify and improve.

from config import *
#from core import *
import aprslib, random

#parse_packet = aprslib.parse(packet)

#parse_packet = aprslib.parse('KF7EEL-2>APDR15,TCPIP*,qAC,T2FINLAND::ARMDS    :PING{49')
# For some reason, this must be here.
parse_packet = aprslib.parse('FROMCALL>APDR15,TCPIP*,qAC,T2FINLAND::TOCALL   :message')

class aprs_packet_construct: #(to_call):
    global aprs_callsign, latitude, longitude, aprs_symbol, aprs_symbol_table, parse_packet
    '''Format various APRS packets'''
    def __init__(self):
        self.aprs_callsign = aprs_callsign
        self.to_call = str(parse_packet['from']).ljust(9)
        self.message_no = '{' + str(random.randint(1,99)) + str(random.randint(1,9))
        # Dummy path will not be uploaded
        self.my_path_dummy = '>ARMDS,DUMMY*:'
        self.my_path_tcp_ip = '>APRS,TCPIP*:'
        self.packet_type_message = ':'
        self.packet_type_status = '>'
        self.message_capable = '='
        self.my_altitude = 'A=' + altitude
        self.symbol = aprs_symbol + aprs_symbol_table
        self.message_ack = ':ack'# + parse_packet['msgNo']
        self.type_bln = 'BLN'
        #common Paths
        self.path_tcp_ip = self.aprs_callsign + self.my_path_tcp_ip
        self.path_dummy = self.aprs_callsign + self.my_path_dummy
        #print(self.to_call)
        
    def msg_ack(self, ack_no):
        packet = self.packet_type_message + self.to_call + self.message_ack + ack_no
        return packet
    def msg_reply(self, message):
        packet = self.packet_type_message + self.to_call + ':' + message[0:67] + self.message_no
        return packet
    def msg_reply_no_ack(self, message):
        packet = self.packet_type_message + self.to_call + ':' + message[0:73]
        return packet
    def msg_send(self, to_call, message):
        packet =  self.packet_type_message + str(to_call).ljust(9) + ':' + message[0:67] + self.message_no
        return packet
    def msg_send_no_ack(self, to_call, message):
        packet = self.packet_type_message + str(to_call).ljust(9) + ':' + message[0:73]
        return packet
    def send_my_status(self, status):
        packet = self.packet_type_status + status[0:55]
        return packet
    def send_bln(self, bulliten_no, message):
        packet = self.packet_type_message + str(self.type_bln + bulliten_no).ljust(9) + ':' + message[0:67]
        return packet           
    def send_my_position(self, comment):
        packet = self.message_capable + latitude + '/' + longitude + self.symbol + self.my_altitude + ' ' + comment[0:43]
        return packet
    def send_position(self, lat, lon, comment, altitude = '', symbol = 'I/'):
        self.altitude = 'A=' + str(altitude)
        self.symbol = symbol
        if self.altitude == 'A=':
            self.altitude = self.altitude.strip('A=')
        packet = self.message_capable + lat + '/' + lon + self.symbol + self.altitude + ' ' + comment[0:43]
        return packet
##       def send_object(self, to_call, lat, lon, comment):
    
class tcp_ip(aprs_packet_construct):
    def msg_ack(self, ack_no):
        packet = self.path_tcp_ip + aprs_packet_construct.msg_ack(self, ack_no)
        return packet
    def msg_reply(self, message):
        packet = self.path_tcp_ip + aprs_packet_construct.msg_reply(self, message)
        return packet
    def msg_reply_no_ack(self, message):
        packet = self.path_tcp_ip + aprs_packet_construct.msg_reply_no_ack(self, message)
        return packet
    def msg_send(self, to_call, message):
        packet =  self.path_tcp_ip + aprs_packet_construct.msg_send(self, to_call, message)
        return packet
    def msg_send_no_ack(self, to_call, message):
        packet = self.path_tcp_ip + aprs_packet_construct.msg_send_no_ack(self, to_call, message)
        return packet
    def send_my_status(self, status):
        packet = self.path_tcp_ip + aprs_packet_construct.send_my_status(self, status)
        return packet
    def send_bln(self, bulliten_no, message):
        packet = self.path_tcp_ip + aprs_packet_construct.send_bln(self, bulliten_no, message)
        return packet           
    def send_my_position(self, comment):
        packet = self.path_tcp_ip + aprs_packet_construct.send_my_position(self, comment)
        return packet
    def send_position(self, lat, lon, comment, altitude = '', symbol = 'I/'):
        packet = self.path_tcp_ip + aprs_packet_construct.send_position(self, lat, lon, comment, altitude, symbol)
        return packet
class dummy_packet(aprs_packet_construct):
    def msg_send_no_ack(self, to_call, message):
        packet =  self.path_dummy + aprs_packet_construct.msg_send(self, to_call, message)
        return packet

#pkt = tcp_ip()

#print(pkt.msg_send('TEST', 'blob'))
#print(to_call('gh'))

