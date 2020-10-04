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

# https://linux.us.org/kf7eel/ARMDS

# Contains all functions for program
# APRS receive script and required for APRS interactive script.

# This is a split from the shark-py-sms project to allow an APRS only setup.
# This is to accomodate users who do not use DMR but wish to still have an interactive
# messaging setup. This should work with any APRS compatable radio, even bridged DMR systems.

# APRS is a registered trademark Bob Bruninga, WB4APR

# Feel free to modify and improve.

# Import modules
from config import *
from user_commands import *
from system_commands import *
import user_functions
import system_commands
import re, binascii, time, os, datetime, smtplib, random
import email, poplib
from email.header import decode_header
# APRS
import aprslib, logging
from pathlib import Path

#SQLite
import sqlite3
from contextlib import closing
# APRS Functions

armds_version = 'v1.101 '

armds_intro = '''
------------------------------------------------------------------------------
|                                                                            |
|         .o.       ooooooooo.   ooo        ooooo oooooooooo.    .oooooo..o  |
|        .888.      `888   `Y88. `88.       .888' `888'   `Y8b  d8P'    `Y8  |
|       .8"888.      888   .d88'  888b     d'888   888      888 Y88bo.       |
|      .8' `888.     888ooo88P'   8 Y88. .P  888   888      888  `"Y8888o.   |
|     .88ooo8888.    888`88b.     8  `888'   888   888      888      `"Y88b  |
|    .8'     `888.   888  `88b.   8    Y     888   888     d88' oo     .d8P  |
|   o88o     o8888o o888o  o888o o8o        o888o o888bood8P'   8""88888P'   |
|                                                                            |
|                                                                            |
| Amateur Radio Micro Data Service - https://armds.net - ''' + armds_version + ''' - by KF7EEL |
|                                                                            |
|   Project status, bug reporting, issues and more can be found at:          |
|   https://git.linux.us.org/kf7eel/ARMDS                                    |
|                                                                            |
|   See this script in action at https://armds.net                           |
|                                                                            |
------------------------------------------------------------------------------

Callsign: ''' + aprs_callsign + ''' - APRS-IS: ''' + aprs_is_send_host + ''' - Port: ''' + str(aprs_is_send_port) + '''

'''

class location_db:
    '''Used for storing and retrieving location information'''
    db_file = "station_locations.db"
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    #rows = cursor.execute("SELECT callsign, lat, lon, time FROM locations WHERE callsign = ?",(callsign,),).fetchall()
    def initialize_db(self):
        '''Set up DB'''
        with self.connection:
            self.cursor.execute("CREATE TABLE locations (callsign TEXT, lat INTERGER, lon INTEGER, time TEXT)")
            self.cursor.execute("PRAGMA journal_mode=WAL;")
            print('Initialize DB')
    def add_location(self, callsign, lat, lon, time):
        '''Add loction to db'''
        with self.connection:
            self.cursor.execute("INSERT INTO locations VALUES (?, ?, ?, ?)", (str(callsign), lat, lon, time))
            print('Added location for ' + callsign) # + ' - ' + time.strftime('%H:%M:%S'))
    def get_location(self, callsign):
        '''return list of tuples with location'''
        with self.connection:
            rows = self.cursor.execute("SELECT callsign, lat, lon, time FROM locations WHERE callsign = ?",(callsign,),).fetchall()
            return rows
    def modify_location(self, callsign, lat, lon, time):
        '''modify location'''
        with self.connection:
            self.cursor.execute("UPDATE locations SET lat = ? WHERE callsign = ?",(lat, callsign))
            self.cursor.execute("UPDATE locations SET lon = ? WHERE callsign = ?",(lon, callsign))
            self.cursor.execute("UPDATE locations SET time = ? WHERE callsign = ?",(time, callsign))
            print('Modified ' + callsign + ' location')
    def view_table(self):
        '''view entire db'''
        self.cursor.execute("SELECT * FROM locations")
        print(self.cursor.fetchall())
    def exists(self, callsign):
        '''see if callsign exists'''
        rows = self.cursor.execute("SELECT callsign FROM locations WHERE callsign = ?",(callsign,),).fetchall()
        #print(rows)
        if rows == []:
                return False
        else:
                return True



global AIS, aprs_message_packet, post_path

aprs_message_packet = None

AIS = aprslib.IS('N0CALL', passwd='-1', host='rotate.aprs.net', port=10152)

# YAAC TCP send function
def yaac_aprs_tcp_send(yaac_msg_source, yaac_msg_dest, yaac_message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = yaac_host #socket.gethostname()                           
    port = yaac_port
# connection to hostname on the port.
    s.connect((host, port))                               
    yaac_msg = yaac_msg_source + '>APRS::' + yaac_msg_dest.ljust(9) + ':' + yaac_message + '{' + str(len(yaac_message)) + time.strftime('%s') + '\r'
                       
    s.send(msg.encode('ascii'))
    s.close()


def packet_write(packet_data):
    with open(packet_send_folder + str(random.randint(1000, 9999)) + '.packet', "w") as packet_write_file:
        packet_write_file.write(packet_data)


def aprs_ack():
    global AIS, AIS_send
    print('Send ACK')
    time.sleep(1)
    if use_yaac == 0:
        if 'msgNo' in parse_packet:
            #print('Connecting to APRS-IS')
            from_space = parse_packet['from']
            packet_write(aprs_callsign + '>APRS,TCPIP*:' + ':' + from_space.ljust(9) + ':ack'+parse_packet['msgNo'])
            print(aprs_callsign + '>APRS,TCPIP*:' + ':' + from_space.ljust(9) + ':ack'+parse_packet['msgNo'])
        else:
            print('No ACK required, not sending ACK.')
            
    if use_yaac == 1:
        print('todo')
def reply_aprs_no_ack(message):
    global AIS, AIS_send
    print('Replying with message, no ACK requested: ' + message)
    time.sleep(1)
    aprs_reply_to = parse_packet['from']
    if use_yaac == 0:
        from_space = parse_packet['from']
        packet_write(aprs_callsign + '>APRS,TCPIP*:' + ':' + aprs_reply_to.ljust(9) + ':' + message)
        print(aprs_callsign + '>APRS,TCPIP*:' + ':' + aprs_reply_to.ljust(9) + ':' + message) #+ '{' + str(random.randint(1,99)) + str(random.randint(1,9)))
    if use_yaac == 1:
        print('todo')

    
def reply_aprs(message):
    global AIS, AIS_send
    print('Replying with message: ' + message)
    time.sleep(1)
    aprs_reply_to = parse_packet['from']
    if use_yaac == 0:
        from_space = parse_packet['from']
        packet_write(aprs_callsign + '>APRS,TCPIP*:' + ':' + aprs_reply_to.ljust(9) + ':' + message + '{' + str(random.randint(1,99)) + str(random.randint(1,9)))
        print(aprs_callsign + '>APRS,TCPIP*:' + ':' + aprs_reply_to.ljust(9) + ':' + message + '{' + str(random.randint(1,99)) + str(random.randint(1,9)))
    if use_yaac == 1:
        print('todo')

def aprs_send_msg(aprs_to, aprs_message_text):
    global aprs_message_packet
    # Generate message number by adding character count to number and dding current time in seconds. Dirty, but works.
    aprs_message_number = str(len(aprs_message_text)) + time.strftime('%s')
    if len(aprs_to) < 9: 
        aprs_to_spaces = aprs_to.ljust(9)
    if len(aprs_to) == 9:
        aprs_to_spaces = aprs_to
    else:
        print('greater than 9')
        aprs_to_spaces = aprs_to.ljust(9)
    aprs_message_packet = aprs_callsign + '>APRS,TCPIP*:' + ':' + aprs_to_spaces +':'+ aprs_message_text + '{' + aprs_message_number
    #print(aprs_to_spaces)
    print('Connecting to APRS-IS')
    time.sleep(1)
    print('Sending...')
    packet_write(aprs_message_packet)
    print(aprs_message_packet)

def aprs_receive_loop(packet):
    global parse_packet, aprs_message_packet, AIS_send
    #pak_str = packet.decode('utf-8',errors='ignore').strip()
        # Parse packet into dictionary
    print(packet)
    parse_packet = aprslib.parse(packet)

    ### TDS Definitions ###################
    aprs_call = parse_packet['from']
    #call = parse_packet['from']
    call = re.sub("-.*", "", aprs_call)
    post_path = post_data_dir + call + '/'
    post_id = datetime.datetime.utcnow().strftime('%m%d%y%H%M') + str(random.randint(1,9))
    post_path_no_call = post_data_dir
    post_file = post_path + post_id + '.md'
    aprs_blog_post_hashtag = ''
    aprs_blog_post_hashtag_markdown = ''
    tiny_page_name = re.sub("@TP| .*", "", parse_packet['message_text'])
    tiny_page_content = re.sub(".*@C", "", parse_packet['message_text'])
    tiny_page_data = tiny_page_name.upper() + ' : ' + tiny_page_content + '\n'
                    
    #########################################
 #   print('Bulletin from: ' + parse_packet['from'] + ' Message: ' + parse_packet['message_text'])

            #if parse_packet['format'] == 'bulletin':
    #if 'bulletin' in parse_packet['format']:
        #print('Bulletin Received...')
        #print('Bulletin from: ' + parse_packet['from'] + ' Message: ' + parse_packet['message_text'])
        #tg_sms_send('Bulletin from: ' + parse_packet['from'] + ' Message: ' + parse_packet['message_text'])
        #time.sleep(3)
  #  if 'message' == parse_packet['format']:# and parse_packet['response'] != 'ack': #and aprs_callsign == parse_packet['addresse']:
       
        #if 'ack' == parse_packet['response']:
         #   print('Received ACK addressed to: ' + parse_packet['addresse'])
            #else:
             #   print('Message from: ' + parse_packet['from'] + ' To: ' + parse_packet['addresse'] + ' Message: ' + parse_packet['message'])
              
   #     if aprs_callsign == parse_packet['addresse'] and 'message_text' in parse_packet:

    try:
                try:
                    if 'E-' in parse_packet['message_text']:
          # Filter @ out os SMS, creat another if statement at this level for APRS implimentation.
                        if '@' in parse_packet['message_text']:
                                print("Perparing email...")
                                aprs_ack()
                                for i in parse_packet['message_text'].split():
                                    if i.startswith("E-"):
                                    #print(i)
                                        to_email = re.sub("E-| .*", "", parse_packet['message_text'])
                                        print("Recipient: " + to_email)
                                        email_body = re.sub("E-" + to_email, "", parse_packet['message_text'])
                                        print("Message: " + email_body)
                                        print("Sending email via SMTP")
                                        email_send(to_email, email_body)
                
                                    else:
                                        print("E- in message, no @, not sending email")
                except:
                    aprs_ack()
                    print('E-Mail error, check config')
                    reply_aprs('Error: Unable to send E-Mail.')
                      
        # Look for command in dictionary, user defined
                else:
                    try:
                        for key in cmd_list:
                            if key == parse_packet['message_text']:
                                print('User defined command: ')
                                print(cmd_list[key])
                                aprs_ack()
                                cmd_list[key]()
                                return
                    except:
                        print('User command failed, exception raised.')
                        reply_aprs('USR CMD failed. Exception raised.')

                #if aprs_callsign == parse_packet['addresse']:
                 #   print('APRS message addressed to hotspot callsign')
                  #  print('APRS message: ' + parse_packet['message_text'] + ' From: ' + parse_packet['from'])
                   # aprs_ack()
            #    # Send message to DMR SMS
            #        print(time.strftime('%H:%M:%S - %m/%d/%Y'))
            #        # send to network or modem defined in config
            #        shark.do_send_sms('1', '2', '9', aprs_tg_network_reply,'APRS MSG from: ' + parse_packet['from'] + '. ' + parse_packet['message_text'])
            #        print('5 second reset')
            #        time.sleep(5)
                #AIS.connect()
                #dmr_sms_aprs_reply = 'APRS MSG from: ' + parse_packet['from'] + '. ' + parse_packet['message_text']
                #reply_sms(dmr_sms_aprs_reply)
                    #time.sleep(1)

                if '!' == parse_packet['message_text']:
                    reply_aprs('Unknown')

                else:
                    try:
                        for sys_key in sys_cmd_list:
                            if sys_key == parse_packet['message_text']:
                                print('System command: ')
                                print(sys_cmd_list[sys_key])
                                aprs_ack()
                                sys_cmd_list[sys_key]()
                                print(parse_packet['raw'])
                                return
                    except:
                        print('System Command failed, exception raised.')
                        reply_aprs('SYS CMD failed. Exception raised.')



######################---TDS---#############################

                #if 1 == use_tds:
                 #   print('TDS enabled')
                  #  print(parse_packet['message_text'])

                if '@P' in parse_packet['message_text']: # and 'T-' in parse_packet['message_text']:
                    try:
                        aprs_ack()
                    except:
                        pass
                    aprs_blog_post_title = 'Post from '
                    aprs_blog_post_hastag = ''
                    aprs_blog_post_hashtag_markdown = ''
                    aprs_blog_post_text = aprs_blog_post_custom_id = re.sub("@T.*|@I.*|@P", "", parse_packet['message_text'])
                    if '@I' in parse_packet['message_text']:
                            aprs_blog_post_custom_id = re.sub(".*@I", "", parse_packet['message_text'])
                            print('Custom ID: ' + aprs_blog_post_custom_id)
                            post_id = aprs_blog_post_custom_id
                        #if 'I-' not in parse_packet['message_text']:
                    if '#' in parse_packet['message_text']:
                        aprs_blog_post_hastag = re.sub(".* #| .*", "", parse_packet['message_text'])
                        aprs_blog_post_hashtag_markdown = ' *Hashtag: [#' + aprs_blog_post_hastag + '](' + aprs_blog_tag_logation + aprs_blog_post_hastag + '.html)*'
                        print('Hashtags: ' + aprs_blog_post_hastag)
                    if '@T' in parse_packet['message_text']:
                        aprs_blog_post_title = re.sub(".*T|@T|-|@I.*", "", parse_packet['message_text']) + ' - '
                        aprs_blog_post_text = re.sub("@T.*|@P", "", parse_packet['message_text'])
                    print(aprs_blog_post_text)
                    print(aprs_blog_post_title)
                    print("APRS Blog Post: " + aprs_blog_post_text + " - From: " + call)
                    dict_data = post_id + ' : ' + aprs_blog_post_text + '\n'
                    twtxt_data = str(datetime.datetime.utcnow().isoformat("T") + "Z").ljust(21) + '\t' + aprs_blog_post_text + ' - Post ID: ' + post_id + '\n'
                    #######Post Template#################################################################################################
                    post = '''\
Title: ''' + aprs_blog_post_title + call + datetime.datetime.utcnow().strftime(' - %m/%d/%Y - %H:%M:%S UTC') + '''
Date: ''' + datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + '''
Category: ''' + aprs_blog_category + '''
Tags: ''' + aprs_call + ', ' + aprs_blog_post_hastag + '''
Authors: ''' + call + '''

------

''' + aprs_blog_post_text + '''
------


''' + aprs_blog_post_hashtag_markdown  + '''

------
##### Post ID: ''' + post_id + '''

##### APRS packet received: *''' + parse_packet['raw'] + '''*

[Track on APRS.fi](https://aprs.fi/info/a/''' + aprs_call + ''') | [Follow with TWTXT](https://armds.net/twtxt/''' + call + '.txt'''') | [Look up on Callook](https://callook.info/''' + call + ''')
'''
                    #####################################################################################################################
                                            #print(post)
                    try:
                                                d = {}
                                                with open(post_path + "dict.txt") as f:
                                                    for line in f:
                                                        (key, val) = line.split(' : ', 1)
                                                        #d[int(key)] = val
                                                        d[key] = val
                                                    #print(d)
                                                    print('Added post to internal dict')
                                                    f = open(post_path + "dict.txt","a")
                                                    f.write(str(dict_data))
                                                    f.close()
###########################################################################
                                                d_twt = {}
                                                with open(twtxt_file_location + call + ".txt") as f_twt:
                                                    for line in f_twt:
                                                        (key, val) = line.split('\t', 1)
                                                        #d[int(key)] = val
                                                        d_twt[key] = val
                                                    #print(d)
                                                    print('Added post to twtxt')
                                                    f_twt = open(twtxt_file_location + call + ".txt","a")
                                                    f_twt.write(str(twtxt_data))
                                                    f_twt.close()
###########################################################################

                    except:
                                                Path(post_path).mkdir(parents=True, exist_ok=True)
                                                Path(post_path + 'dict.txt').touch()
                                                print('excepted, created folder with dict file')
                                                d = {}
                                                with open(post_path + "dict.txt") as f:
                                                    for line in f:
                                                        (key, val) = line.split(' : ', 1)
                                                        #d[int(key)] = val
                                                        d[key] = val
                                                    #print(d)
                                                    print('Added post to internal dict')
                                                    f = open(post_path + "dict.txt","a")
                                                    f.write(str(dict_data))
                                                    f.close()
                                                    print('created path and dict file')
################################################################################
###########################################################################
                                                Path(twtxt_file_location).mkdir(parents=True, exist_ok=True)
                                                Path(twtxt_file_location + call + '.txt').touch()
                                                print('excepted, created folder with twtxt file')
                                                d_twt = {}
                                                with open(twtxt_file_location + call + ".txt") as f_twt:
                                                    for line in f_twt:
                                                        (key, val) = line.split('\t', 1)
                                                        #d[int(key)] = val
                                                        d_twt[key] = val
                                                    #print(d)
                                                    print('Added post to twtxt')
                                                    f_twt = open(twtxt_file_location + call + ".txt","a")
                                                    f_twt.write(str(twtxt_data))
                                                    f_twt.close()
###########################################################################
################################################################################

                        
                    #print(add_dict_entry)

                    try:
                            write_post = open(post_path + post_id + '.md', 'w')
                            write_post.write(post)
                            write_post.close()
                    except:
                            Path(post_path).mkdir(parents=True, exist_ok=True)
                            time.sleep(3)
                            write_post = open(post_path + post_id + '.md', 'w')
                            write_post.write(post)
                            write_post.close()
                    reply_aprs_no_ack('Posted. ID: ' + post_id)
#####

#####
                if '@DEL ' in parse_packet['message_text']:
                        try:
                            aprs_ack()
                        except:
                            pass
                        aprs_blog_post_delete = re.sub("@DEL ", "", parse_packet['message_text'])
                        print(aprs_blog_post_delete)
                        os.system('rm ' + post_path + aprs_blog_post_delete + '.md')
                        print('deleted post ID: ' + aprs_blog_post_delete)
                        
                        try:
                            d = {}
                            with open(post_path + "dict.txt") as f:
                                for line in f:
                                    (key, val) = line.split(' : ', 1)
                                #d[int(key)] = val
                                    d[str(key)] = val
                                #print(d)
                                del d[str(aprs_blog_post_delete)]
                                #print('----')
                                #print(d)
                                #print('----')
                                f = open(post_path + "dict.txt","w")
                                f.write('')
                                f.close()
                                f = open(post_path + "dict.txt","a")
                                for k, v in d.items():
                            #for item in v:
                            #print(k,v)
                                    print(k + ' : ' + v + '\n')
                                    f.write(k + ' : ' + v) # + '\n')
                                f.close()
                                print('sucessfully deleted')
##############################################################################
                            d_twt = {}

                            with open(twtxt_file_location + call + ".txt") as f_twt:
                                for line in f_twt:
                                    post_id_from_twtxt = re.sub('.*Post ID: ','',line)
                                    twtxt_time = re.sub('\t.*','',line).strip('\n')
                                    if aprs_blog_post_delete in line:
                                        line = re.sub(twtxt_time, aprs_blog_post_delete, line)
                                    (key, val) = line.split('\t', 1)
                                #d[int(key)] = val
                                    d_twt[str(key)] = val
                                del d_twt[str(aprs_blog_post_delete)]
                                f_twt = open(twtxt_file_location + call + ".txt","w")
                                f_twt.write('')
                                f_twt.close()
                                f_twt = open(twtxt_file_location + call + ".txt","a")
                                for k, v in d_twt.items():
                                    print(k + '\t' + v + '\n')
                                    f_twt.write(k + '\t' + v) # + '\n')
                                f_twt.close()
##############################################################################
                                reply_aprs('Deleted post ID: ' + aprs_blog_post_delete)
                                
                        except:
                            print('unable to delete')
                            reply_aprs('Unable to delete post: ' + aprs_blog_post_delete)
####################################Tiny pages#######################3
                if '@TP' in parse_packet['message_text']: # and 'T-' in parse_packet['message_text']:
                    try:
                        aprs_ack()
                    except:
                        pass
##                    tiny_page_name = re.sub("@TP| .*", "", parse_packet['message_text'])
##                    tiny_page_content = re.sub(".*@C", "", parse_packet['message_text'])
##                    tiny_page_data = tiny_page_name + ' : ' + tiny_page_content + '\n'
                    tiny_page_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
        <meta charset="utf-8" />
        <title>''' + tiny_page_name + '''</title>
</head>
<body>
<table style="border-color: black; margin-left: auto; margin-right: auto;" border="5">
<tbody>
<tr>
<td style="text-align: center;">
<h1><span style="text-decoration: underline;"><strong>''' + tiny_page_name + '''</strong></span></h1>
</td>
</tr>
<tr>
<td style="text-align: center;">
<h4>&nbsp; ''' + tiny_page_content + '''  &nbsp;</h4>
</td>
</tr>
<tr>
<td style="text-align: left;"><span style="text-decoration: underline;"><strong>Author:</strong></span>&nbsp;&nbsp;&nbsp; <em>''' + call + ''' &nbsp;&nbsp;&nbsp;</em></td>
</tr>
<tr>
<td style="text-align: center;">
<h6><em>Site generated by <a href="https://armds.net">ARMDS</a>.</em><br />Amateur Radio Micro Data Service.</h6>
</td>
</tr>
</tbody>
</table>
</body>

'''
                    try:
                                                d = {}
                                                with open(tiny_pages_html_location + "tiny_pages.txt") as f:
                                                    for line in f:
                                                        (key, val) = line.split(' : ', 1)
                                                        #d[int(key)] = val
                                                        d[key] = val
                                                    #print(d)
                                                    print('Added page to tiny page db')
                                                    f = open(tiny_pages_html_location + "tiny_pages.txt","a")
                                                    f.write(str(tiny_page_data))
                                                    f.close()


                    except:
                                                Path(tiny_pages_html_location).mkdir(parents=True, exist_ok=True)
                                                Path(tiny_pages_html_location + 'tiny_pages.txt').touch()
                                                print('excepted, created folder with tiny page file')
                                                d = {}
                                                with open(tiny_pages_html_location + "tiny_pages.txt") as f:
                                                    for line in f:
                                                        (key, val) = line.split(' : ', 1)
                                                        #d[int(key)] = val
                                                        d[key] = val
                                                    #print(d)
                                                    print('Added post to tiny page db')
                                                    f = open(tiny_pages_html_location + "tiny_pages.txt","a")
                                                    f.write(str(tiny_page_data))
                                                    f.close()
                                                    print('created path and page file')
                    try:
                            write_page = open(tiny_pages_html_location + tiny_page_name.lower() + '.html', 'w')
                            write_page.write(tiny_page_html)
                            write_page.close()
                    except:
                            Path(tiny_pages_html_location).mkdir(parents=True, exist_ok=True)
                            time.sleep(3)
                            write_page = open(tiny_pages_html_location + tiny_page_name.lower() + '.html', 'w')
                            write_page.write(tiny_page_html)
                            write_page.close()
                    reply_aprs_no_ack('Created Tiny Page: ' + tiny_page_name)

#####################################################################
                if '@DELTP ' in parse_packet['message_text']:
                        try:
                            aprs_ack()
                        except:
                            pass
                        tiny_page_delete = re.sub("@DELTP ", "", parse_packet['message_text']).upper()
                        print(tiny_page_delete)
                        os.system('rm ' + tiny_pages_html_location + tiny_page_delete.lower() + '.html')
                        print('deleted tiny page: ' + tiny_page_delete)
                        
                        try:
                            d = {}
                            with open(tiny_pages_html_location + "tiny_pages.txt") as f:
                                for line in f:
                                    (key, val) = line.split(' : ', 1)
                                #d[int(key)] = val
                                    d[str(key)] = val
                                #print(d)
                                del d[str(tiny_page_delete)]
                                #print('----')
                                #print(d)
                                #print('----')
                                f = open(tiny_pages_html_location + "tiny_pages.txt","w")
                                f.write('')
                                f.close()
                                f = open(tiny_pages_html_location + "tiny_pages.txt","a")
                                for k, v in d.items():
                            #for item in v:
                            #print(k,v)
                                    print(k + ' : ' + v + '\n')
                                    f.write(k + ' : ' + v) # + '\n')
                                f.close()
                                print('sucessfully deleted')
                                reply_aprs('Deleted page: ' + tiny_page_delete)
                        except:
                            print('unable to delete page')
                            reply_aprs('Unable to delete page: ' + tiny_page_delete)
#####################################################################
                if '@R ' in parse_packet['message_text']:
                        try:
                            aprs_ack()
                        except:
                            pass
                        aprs_blog_post_retrieve_cmd = re.sub("@R ", "", parse_packet['message_text'])
                        #print(aprs_blog_post_retrieve_cmd)
                        aprs_blog_post_retrieve_id_cmd = re.sub(".*ID ", "", aprs_blog_post_retrieve_cmd)
                        #print(aprs_blog_post_retrieve_id_cmd)
                        aprs_blog_post_retrieve_call_cmd = str(re.sub("ID.*| ", "", aprs_blog_post_retrieve_cmd)).upper()
                        #print(aprs_blog_post_retrieve_call_cmd)
                        post_path_retrieve = post_path_no_call + aprs_blog_post_retrieve_call_cmd + '/'
                        #print(post_path_retrieve)
                        tiny_page_name = re.sub("@R ", "", parse_packet['message_text'])
                        #tiny_page_content = re.sub(".*@C", "", parse_packet['message_text'])
                        if 'ID' in parse_packet['message_text']:
                            try:
                                d = {}
                                with open(post_path_retrieve + "dict.txt") as f:
                            #get vaule of key
                                    for line in f:
                                        (key, val) = line.split(' : ', 1)
                                        d[str(key)] = val
                                    print(d.get(aprs_blog_post_retrieve_id_cmd))
                                    if d.get(aprs_blog_post_retrieve_id_cmd) == None:
                                        print('No entries found for that ID')
                                        reply_aprs('No post found for ID: ' + d.get(aprs_blog_post_retrieve_id_cmd).strip('\n'))
                                        
                                    else:
                                        print('Sending APRS packet...')
                                        # add no ack message pack to announce incoming message
                                        reply_aprs_no_ack('Post from ' + aprs_blog_post_retrieve_call_cmd + ' ID: ' + aprs_blog_post_retrieve_id_cmd)
                                        reply_aprs(d.get(aprs_blog_post_retrieve_id_cmd).strip('\n'))
                                        
                            except:
                                print('Post or author not found')
                                reply_aprs('Post not found')
                                                                
                        else:
                            print('Requested: ' + tiny_page_name)
                            try:
                                d = {}
                                with open(tiny_pages_html_location + "tiny_pages.txt") as f:
                                #get vaule of key
                                        for line in f:
                                            (key, val) = line.split(' : ', 1)
                                            d[str(key)] = val
                                        print(d.get(tiny_page_name))
                                        if d.get(tiny_page_name) == None:
                                            print('No Tiny Pages found')
                                            reply_aprs('No Tiny Pages found for: ' + d.get(tiny_page_name).strip('\n'))
                                            
                                        else:
                                            print('Sending APRS packet...')
                                            # add no ack message pack to announce incoming message
                                            reply_aprs_no_ack('Page: ' + tiny_page_name) # + ' - ' + d.get(tiny_page_name))
                                            reply_aprs(d.get(tiny_page_name).strip('\n'))
                                            
                            except:
                                print('Page not found')
                                reply_aprs('Page not found')



                if '@DELETE MY DATA' in parse_packet['message_text']:
                        try:
                            aprs_ack()
                        except:
                            pass
                        if aprs_call in parse_packet['message_text']:
                            os.system('rm -R ' + post_path)
                            os.system('rm ' + twtxt_file_location + call + ".txt")
                            print('Deleted all data for: ' + call)
                            reply_aprs('Deleted all data for: ' + call)
                        else:
                            print('Your current callsign w/ SSID must be in message to confirm')
                            reply_aprs('Must include current callsign and SSID')
                #else:
                #    aprs_ack()
                #    print('Command not found')
                #    reply_aprs('Command not found or recognized')
                #if '!!' == parse_packet['message_text']:
                #    reply_aprs('Unknown')

                else:
                        print('Message, but not to us')
                        if 'message_text' in parse_packet:
                            print(parse_packet['raw'])
                            print('Message from: ' + parse_packet['from'] + ' To: ' + parse_packet['addresse'] + ' Message: ' + parse_packet['message_text'])

                        else:
                            print(parse_packet['raw'])


                    
    except (aprslib.ParseError, aprslib.UnknownFormat) as exp:
        print('Unable to process packet')
        pass


    else:
        print('Packet from: ' + parse_packet['from'] + ' Format: ' + parse_packet['format'] + ' - ' + time.strftime('%H:%M:%S'))
        #print(parse_packet)

# Send email function
def email_send(to_email, email_body):
    sent_from = email_user
    to = [to_email]
    subject = 'APRS Message from ' + str(parse_packet['from'])
    body = str('APRS message from: ' + str(parse_packet['from']) + '.' + email_body + '\n' + '\nThis is an APRS message delivered to you via Amateur Radio Micro Data Service (ARMDS).\n\nYou may send an APRS message by .....')

    email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

    try:
        server = smtplib.SMTP_SSL(email_server, smtp_port)
        server.ehlo()
        server.login(email_user, email_password)
        server.sendmail(sent_from, to, email_text)
        server.close()
        reply_aprs('E-Mail sent to ' + to_email)
    except Exception as e:
        print(e)
        print('Sending email failed')
        reply_aprs('Sending Failed')
