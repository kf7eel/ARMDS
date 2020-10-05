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

# https://linux.us.org/kf7eel/ARMDS

#Dummy packet generator to manipulate ARMDS
import random
from config import aprs_callsign, packet_recv_folder
from core import dummy_packet

dummy_pkt = dummy_packet().msg_send_no_ack(aprs_callsign, input('Enter command: '))

with open(packet_recv_folder + str(random.randint(1000, 9999)) + '.packet', "w") as packet_write_file:
    print(dummy_pkt)
    packet_write_file.write(dummy_pkt)
