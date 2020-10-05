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

# Modified: 09-26-2020

# System Functions.
# This is a split from the shark-py-sms project to allow an APRS only setup.
# This is to accomodate users who do not use DMR but wish to still have an interactive
# messaging setup. This should work with any APRS compatable radio, even bridged DMR systems.
# https://github.com/kf7eel/shark-py-sms

# Feel free to modify and improve.

# Simple commands that do not require filtering

class Initialize:
    def __init__(self):
        import time, os #, core
        from core import write_packet

##def initialize():
##    import time, os
# Send user system uptime

def uptime():
    import time, os, core
    from core import reply_aprs_no_ack
    print('Getting uptime...')
    uptime = os.popen('uptime').read()
    reply_aprs_no_ack(str(uptime))

# Replies to user by sending what was received
def echo():
    import time, os, core, parse_packet
    from core import reply_aprs_no_ack
    reply_aprs_no_ack(parse_packet['message_text'])
    print("Echoing SMS")
# Return current time
def time():
    import time, os, core
    from core import reply_aprs_no_ack
    print('Getting time...')
    current_time = time.strftime('%H:%M %A %B %d, %Y - Timezone: %z')
    reply_aprs_no_ack(current_time)

def ping():
    from core import reply_aprs_no_ack
    import time, os, core, maidenhead
    print("Received ping...")
    time.sleep(0.5)
    print("Pong")
    reply_aprs_no_ack('Pong '+time.strftime('%H:%M:%S - %m/%d/%Y'))

##def maidenhead():
##    #from core import reply_aprs
##    import time, os, core
##    loc_data = db.get_location(parse_packet['from'])
##    reply_aprs(mh.to_maiden(loc_data[0][1], loc_data[0][2]))
##    print(mh.to_maiden(loc_data[0][1], loc_data[0][2]))

def command_help():
    from core import reply_aprs_no_ack
    import time, os, core
##    print('\n' + "--------------------------------------" + '\n')
##    print('Here are the available commands: ')
##    print('\n')
##    print('HELP - prints current message')
##    print('ECHO - replies eniter message back to user')
##    print('TIME - current local time')
##    print('UPTIME - uptime of host system')
##    print('PING - replies with pong')
##    print('ID - returns your DMR ID')
##    print('If "TO-" and "@" are in message, will send email to address.')
##    print('\n' + "--------------------------------------" + '\n')
    reply_aprs_no_ack('See https://armds.net for help and information.')
        

