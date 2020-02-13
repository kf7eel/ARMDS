#!/usr/bin/python3.7

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

# Contains all functions for program
# APRS receive script and required for APRS interactive script.

# This is a split from the shark-py-sms project to allow an APRS only setup.
# This is to accomodate users who do not use DMR but wish to still have an interactive
# messaging setup. This should work with any APRS compatable radio, even bridged DMR systems.
# https://github.com/kf7eel/shark-py-sms


# Feel free to modify and improve.

# Import modules
# DMR SMS
from config import *
from user_commands import *
from system_commands import *
#from dmr_to_aprs_map import *
#from user_functions import *
import user_functions
import system_commands
import re, binascii, time, os, datetime, smtplib, random
import email, poplib
from email.header import decode_header
# APRS
import aprslib, logging
from pathlib import Path

#import csv

# APRS Functions


global AIS, aprs_message_packet, post_path

aprs_message_packet = None

AIS_send = aprslib.IS(aprs_callsign, passwd=aprs_passcode,host='rotate.aprs2.net', port=14580)

AIS = aprslib.IS(aprs_callsign, passwd=aprs_passcode, host=aprs_is_host, port=aprs_is_port)


# YAAC TCP send function
def yaac_aprs_tcp_send(yaac_msg_source, yaac_msg_dest, yaac_message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = yaac_host #socket.gethostname()                           
    port = yaac_port
# connection to hostname on the port.
    s.connect((host, port))                               
#msg = 'KF7EEL>KF7EEL-7:testing again...{27'+'\r'
    yaac_msg = yaac_msg_source + '>APRS::' + yaac_msg_dest.ljust(9) + ':' + yaac_message + '{' + str(len(yaac_message)) + time.strftime('%s') + '\r'
# Working packet!
# msg = 'KF7EEL-15>APRS::KF7EEL-7 :test 23{23'+'\r'                              
    s.send(msg.encode('ascii'))
    s.close()



def aprs_ack():
    global AIS, AIS_send
    print('Send ACK')
    time.sleep(1)
    if use_yaac == 0:
        print('Connecting to APRS-IS')
        AIS_send.connect()
        time.sleep(1)
        print('Sending...')
        from_space = parse_packet['from']
        AIS_send.sendall(aprs_callsign + '>APRS,TCPIP*:' + ':' + from_space.ljust(9) + ':ack'+parse_packet['msgNo'])
        print(aprs_callsign + '>APRS,TCPIP*:' + ':' + from_space.ljust(9) + ':ack'+parse_packet['msgNo'])
        time.sleep(1)
        AIS_send.close()
        #time.sleep(1)
    if use_yaac == 1:
        print('todo')
def reply_aprs_no_ack(message):
    global AIS, AIS_send
    print('Replying with message, no ACK requested: ' + message)
    time.sleep(1)
    aprs_reply_to = parse_packet['from']
    if use_yaac == 0:
        print('Connecting to APRS-IS')
        AIS_send.connect()
        time.sleep(1)
        print('Sending...')
        from_space = parse_packet['from']
        AIS_send.sendall(aprs_callsign + '>APRS,TCPIP*:' + ':' + aprs_reply_to.ljust(9) + ': ' + message) #+ '{' + str(random.randint(1,99)) + str(random.randint(1,9))) #str(len(message)) + time.strftime('%s'))
        print(aprs_callsign + '>APRS,TCPIP*:' + ':' + aprs_reply_to.ljust(9) + ': ' + message) #+ '{' + str(random.randint(1,99)) + str(random.randint(1,9)))
        time.sleep(1)
        AIS_send.close()
        #time.sleep(1)
    if use_yaac == 1:
        print('todo')

    
def reply_aprs(message):
    global AIS, AIS_send
    print('Replying with message: ' + message)
    time.sleep(1)
    aprs_reply_to = parse_packet['from']
    if use_yaac == 0:
        print('Connecting to APRS-IS')
        AIS_send.connect()
        time.sleep(1)
        print('Sending...')
        from_space = parse_packet['from']
        AIS_send.sendall(aprs_callsign + '>APRS,TCPIP*:' + ':' + aprs_reply_to.ljust(9) + ': ' + message + '{' + str(random.randint(1,99)) + str(random.randint(1,9))) #str(len(message)) + time.strftime('%s'))
        print(aprs_callsign + '>APRS,TCPIP*:' + ':' + aprs_reply_to.ljust(9) + ': ' + message + '{' + str(random.randint(1,99)) + str(random.randint(1,9)))
        time.sleep(1)
        AIS_send.close()
        #time.sleep(1)
    if use_yaac == 1:
        print('todo')

def aprs_send_msg(aprs_to, aprs_message_text):
    global aprs_message_packet
    #print(aprs_to)
    #print(aprs_message_text.strip('\n'))
    #b_msg_num = len(aprs_message_text)
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
    AIS_send.connect()
    time.sleep(1)
    print('Sending...')
    AIS_send.sendall(aprs_message_packet)
    print(aprs_message_packet)
    #time.sleep(1)
    AIS_send.close()
   
   
def aprs_location():
    AIS_send.connect()
    location_packet = aprs_callsign + '>APRS,TCPIP*:' + '=' + latitude + '/' + longitude + aprs_symbol + aprs_symbol_table + 'A=' + altitude + ' ' + aprs_comment
    print('Sending location packet.')
    print(location_packet)
    AIS_send.sendall(location_packet)
    time.sleep(5)
    AIS_send.close()    
def aprs_beacon_1():
    AIS_send.connect()
    beacon_1_packet = aprs_callsign + '>APRS,TCPIP*:' + '=' + latitude + '/' + longitude + aprs_symbol + aprs_symbol_table + 'A=' + altitude + ' ' + aprs_beacon_1_comment
    print('Sending beacon 1 packet.')
    print(beacon_1_packet)
    AIS_send.sendall(beacon_1_packet)
    time.sleep(5)
    AIS_send.close()

def aprs_beacon_2():
    AIS_send.connect()
    beacon_2_packet = aprs_callsign + '>APRS,TCPIP*:' + '=' + latitude + '/' + longitude + aprs_symbol + aprs_symbol_table + 'A=' + altitude + ' ' + aprs_beacon_2_comment
    print('Sending beacon 1 packet.')
    print(beacon_2_packet)
    AIS_send.sendall(beacon_2_packet)
    time.sleep(5)
    AIS_send.close()

def aprs_receive_loop(packet):
    global parse_packet, aprs_message_packet, AIS_send
    pak_str = packet.decode('utf-8',errors='ignore').strip()
        # Parse packet into dictionary
    parse_packet = aprslib.parse(pak_str)

    ### TDS Definitions ###################
    aprs_call = parse_packet['from']
    call = parse_packet['from']
    call = re.sub("-.", "", aprs_call)
    post_path = post_data_dir + call + '/'
    post_id = time.strftime('%m%d%y%H%M') + str(random.randint(1,9))
    post_path_no_call = post_data_dir
    post_file = post_path + post_id + '.md'
    #########################################
 #   print('Bulletin from: ' + parse_packet['from'] + ' Message: ' + parse_packet['message_text'])

            #if parse_packet['format'] == 'bulletin':
    #if 'bulletin' in parse_packet['format']:
        #print('Bulletin Received...')
        #print('Bulletin from: ' + parse_packet['from'] + ' Message: ' + parse_packet['message_text'])
        #tg_sms_send('Bulletin from: ' + parse_packet['from'] + ' Message: ' + parse_packet['message_text'])
        #time.sleep(3)
    if 'message' == parse_packet['format']:# and parse_packet['response'] != 'ack': #and aprs_callsign == parse_packet['addresse']:
       
        #if 'ack' == parse_packet['response']:
         #   print('Received ACK addressed to: ' + parse_packet['addresse'])
            #else:
             #   print('Message from: ' + parse_packet['from'] + ' To: ' + parse_packet['addresse'] + ' Message: ' + parse_packet['message'])
              
        if aprs_callsign == parse_packet['addresse'] and 'message_text' in parse_packet:

            try:
                        try:
                            if 'E-' in parse_packet['message_text']:
                  # Filter @ out os SMS, creat another if statement at this level for APRS implimentation.
                                if '@' in parse_packet['message_text']:
                                        print("Perparing email...")
                                        for i in parse_packet['message_text'].split():
                                            if i.startswith("E-"):
                                            #print(i)
                                                to_email = i.replace("E-", "")
                                                print("Recipient: " + to_email)
                                                email_body = parse_packet['message_text']
                                                print("Message: " + email_body)
                                                print("Sending email via SMTP")
                                                email_send(to_email, email_body)
                                                aprs_ack()
                        
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
                        if '!!' == parse_packet['message_text']:
                            reply_aprs('Unknown')

                        #else:
                         #   aprs_ack()
                          #  print('Command not found')
                           # reply_aprs('Command not found or recognized')
######################---TDS---#############################

                        #if 1 == use_tds:
                         #   print('TDS enabled')
                          #  print(parse_packet['message_text'])

                        if 'B-' in parse_packet['message_text'] and 'T-' in parse_packet['message_text']:
                            aprs_ack()
                            if 'I-' in parse_packet['message_text']:
                                    aprs_blog_post_custom_id = re.sub(".*I-", "", parse_packet['message_text'])
                                    print('Custom ID: ' + aprs_blog_post_custom_id)
                                    post_id = aprs_blog_post_custom_id
                                #if 'I-' not in parse_packet['message_text']:
                            aprs_blog_post_text = re.sub("T-.*|B-", "", parse_packet['message_text'])
                            aprs_blog_post_title = re.sub(".*T|T-|-|I-.*", "", parse_packet['message_text']) + ' - '
                            print(aprs_blog_post_text)
                            print('"'+aprs_blog_post_title+'"')
                            print("APRS Blog Post: " + aprs_blog_post_text + " - From: " + call)
                            dict_data = post_id + ' : ' + aprs_blog_post_text + '\n'
                            #######Post Template#################################################################################################
                            post = '''\
Title: ''' + aprs_blog_post_title + call + time.strftime(' - %m/%d/%Y - %H:%M:%S PST') + '''
Date: ''' + time.strftime('%Y-%m-%d %H:%M:%S') + '''
Category: ''' + 'APRS Blog' + '''
Tags: ''' + aprs_call + '''
Authors: ''' + call + '''

------

''' + aprs_blog_post_text + '''
------

------
###### Post ID: ''' + post_id + '''
###### Raw APRS packet: *''' + parse_packet['raw'] + ''' *

[Track on APRS.fi](https://aprs.fi/info/a/''' + aprs_call + ''') | QRZ here | QRZCQ | [Callook](https://callook.info/''' + call + ''')
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
                            reply_aprs('Posted. ID: ' + post_id)

                        if 'B-' in parse_packet['message_text'] and 'T-' not in parse_packet['message_text']:
                                    aprs_ack()
                                    if 'I-' in parse_packet['message_text']:
                                        post_id = re.sub("T-.*|I-|.*I-|B-", "", parse_packet['message_text'])
                                        print('Custom post ID: ' + post_id)
                                    aprs_blog_post_text = aprs_blog_post_custom_id = re.sub("T-.*|I-.*|B-", "", parse_packet['message_text'])
                                    print("APRS Blog Post: " + aprs_blog_post_text + " - From: " + call)
                                    dict_data = post_id + ' : ' + aprs_blog_post_text + '\n'

                            #######Post Template#################################################################################################
                                    post = '''\
Title: Post from ''' + call + time.strftime(' - %m/%d/%Y - %H:%M:%S PST') + '''
Date: ''' + time.strftime('%Y-%m-%d %H:%M:%S') + '''
Category: ''' + 'APRS Blog' + '''
Tags: ''' + aprs_call + '''
Authors: ''' + call + '''

------

''' + aprs_blog_post_text + '''
------

------

###### Post ID: ''' + post_id + '''
###### Raw APRS packet: *''' + parse_packet['raw'] + ''' *

[Track on APRS.fi](https://aprs.fi/info/a/''' + aprs_call + ''') | QRZ here | QRZCQ | [Callook](https://callook.info/''' + call + ''')
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
                                    reply_aprs('Posted. ID: ' + post_id)
                        if 'BLOG DEL' in parse_packet['message_text']:
                                aprs_ack()
                                aprs_blog_post_delete = re.sub("BLOG DEL ", "", parse_packet['message_text'])
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
                                        reply_aprs('Deleted post ID: ' + aprs_blog_post_delete)
                                except:
                                    print('unable to delete')
                                    reply_aprs('Unable to delete post: ' + aprs_blog_post_delete)
                        if 'BLOG ' in parse_packet['message_text']:
                                aprs_ack()
                                aprs_blog_post_retrieve_cmd = re.sub("BLOG ", "", parse_packet['message_text'])
                                #print(aprs_blog_post_retrieve_cmd)
                                aprs_blog_post_retrieve_id_cmd = re.sub(".*ID ", "", aprs_blog_post_retrieve_cmd)
                                #print(aprs_blog_post_retrieve_id_cmd)
                                aprs_blog_post_retrieve_call_cmd = str(re.sub("ID.*| ", "", aprs_blog_post_retrieve_cmd)).upper()
                                #print(aprs_blog_post_retrieve_call_cmd)
                                post_path_retrieve = post_path_no_call + aprs_blog_post_retrieve_call_cmd + '/'
                                #print(post_path_retrieve)
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
                                            reply_aprs('No post found for ID: ' + post_id)
                                        else:
                                            print('Sending APRS packet...')
                                            # add no ack message pack to announce incoming message
                                            reply_aprs_no_ack('Post from ' + aprs_blog_post_retrieve_call_cmd + ' ID: ' + aprs_blog_post_retrieve_id_cmd)
                                            reply_aprs(d.get(aprs_blog_post_retrieve_id_cmd).strip('\n'))
                                except:
                                    print('Post or author not found')
                                    reply_aprs('Post not found')

                        if 'BLOGNUKE ME' in parse_packet['message_text']:
                                aprs_ack()
                                if aprs_call in parse_packet['message_text']:
                                    os.system('rm -R ' + post_path)
                                    print('Deleted all data for: ' + call)
                                    reply_aprs('Deleted all data for: ' + call)
                                else:
                                    print('Your current callsign w/ SSID must be in message to confirm')
                                    reply_aprs('Must include current callsign and SSID')

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
    body = str(email_body + '\n' + 'Insert reply directions here')

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
    except:
        print('Sending email failed')
        reply_aprs('Sending Failed')
