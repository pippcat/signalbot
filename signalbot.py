#!/usr/bin/env python
# coding: UTF-8

import argparse # cli argument parser
import json # for json handling
import configparser # for config file
import shutil # for copying files
import datetime # for decoding timestamps
import time # for timestamp formating / modification
import smtplib # for sending mails
import mimetypes # for sending mails
import email # for sending and reveiving mails
import imapclient # for sending mails
import sys # for file access
reload(sys) # because of unicode fuckup
sys.setdefaultencoding('utf-8') # this as well
from clockwork import clockwork # for sending SMS using www.clockworksms.com
import fileinput # for mime detection and renaming
import mimetypes # for mime detection and renaming
import os # for mime detection and renaming
import sys # for mime detection and renaming
from subprocess import Popen, PIPE # for mime detection and renaming

config = configparser.ConfigParser()
config.optionxform = lambda option: option # otherwise its lowercase only
config.read(os.path.dirname(__file__) + '/config.ini')
debug = config['SWITCHES'].getboolean('debug')
getsignalmessages = config['SWITCHES'].getboolean('getsignalmessages')
sendmail = config['SWITCHES'].getboolean('sendmail')
sendsms = config['SWITCHES'].getboolean('sendsms')
emptydb = config['SWITCHES'].getboolean('emptydb')
getmail = config['SWITCHES'].getboolean('getmail')
signalnumber = config['SIGNAL']['signalnumber']
signalgroupid = config['SIGNAL']['signalgroupid']
signal_cli_path = config['SIGNAL']['signal_cli_path']
signalmsgdb = config['SIGNAL']['signalmsgdb']
attachmentpath = config['SIGNAL']['attachmentpath']
mailfrom = config['MAIL']['mailfrom']
mailsubject = config['MAIL']['mailsubject']
addr_list = config['MAIL']['addr_list']
smtpserver = config['MAIL']['smtpserver']
imapserver = config['MAIL']['imapserver']
mailuser = config['MAIL']['mailuser']
mailpassword = config['MAIL']['mailpassword']
max_attachmentsize = config['MAIL']['max_attachmentsize']
sms_receivers = config['SMS']['sms_receivers']
clockworkapikey = config['SMS']['clockworkapikey']
version = config['OTHER']['version']
contacts = config.items("CONTACTS")

# cli arg parser and help message:
parser=argparse.ArgumentParser(
    description='''Signalbot is a Python script which can send Signal messages via Email and/or SMS (using www.clockworksms.com API).
    It's relying on signal-cli (https://github.com/AsamK/signal-cli) to fetch the actual messages.
    Configuration is done in config.ini and should be self explanatory.''',
    epilog="""""")
parser.add_argument("--sendmail", action="store_true", help="override config and send mail")
parser.add_argument("--notsendmail", action="store_true", help="override config and do not send mail")
parser.add_argument("--fetch", action="store_true", help="override config and fetch new signal messages")
parser.add_argument("--notfetch", action="store_true", help="override config and do not fetch new signal messages")
parser.add_argument("--sms",  action="store_true", help="override config and send SMS")
parser.add_argument("--notsms", action="store_true", help="override config and do not send SMS")
parser.add_argument("--debug", action="store_true", help="override config and switch on debug mode")
parser.add_argument("--notdebug", action="store_true", help="override config and switch off debug mode")
parser.add_argument("--emptydb", action="store_true", help="override config and delete message database after processing")
parser.add_argument("--notemptydb", action="store_true", help="override config and keep message database after processing")
parser.add_argument("--getmail", action="store_true", help="override config and send email responses to group")
parser.add_argument("--notgetmail", action="store_true", help="override config and do not send email responses to group")
args=parser.parse_args()
# override config if asked to do so:
if args.sendmail: sendmail = True
if args.notsendmail: sendmail = False
if args.sms: sendsms = True
if args.notsms: sendsms = False
if args.fetch: getsignalmessages = True
if args.notfetch: getsignalmessages = False
if args.debug: debug = True
if args.notdebug: debug = False
if args.emptydb: emptydb = True
if args.notemptydb: emptydb = False
if args.getmail: getmail = True
if args.notgetmail: getmail = False

# main program:
def main():
    if debug: print("DEBUG - main(): called")
    print("Signalbot v" + version + ", Timestamp: " + str(datetime.datetime.now()))
    print("Switch settings: Debug = " + str(debug) + ", getsignalmessages = " + str(getsignalmessages) + ", sendmail = " + str(sendmail) + ", sendsms = " + str(sendsms) + ", emptydb = " + str(emptydb) + ", getmail = " + str(getmail))
    # get new signal messages:
    if getsignalmessages == True:
        print("Signalbot is checking for new messages")
        os.system(signal_cli_path + ' -u ' + signalnumber + ' receive --json > ' + os.path.dirname(__file__) + '/out')

    # parse signal messages from file into msg dict:
    print("Signalbot is parsing new messages")
    msg = messagehandler(signalmsgdb)

    # formatting msg dict:
    i = 0
    newmessage = False
    for i in range(len(msg)): # is there a better way to do this?
        if 'sender_' + str(i) in msg:
            newmessage = True
            sender = msg['sender_' + str(i)]
            timestamp = msg['time_' + str(i)]
            message = msg['message_' + str(i)]
            sendername = msg['sendername_' + str(i)]
            mailtext = "New Signal message from " + str(sendername) + " (" +str(sender) + "), sent " + str(timestamp) + ":\n" + message + "\n\n"
            print("## Message " + str(i) + ":")
            print(message)
            print("## end of message")
            if 'attachment_' + str(i) in msg:
                attachment = msg['attachment_' + str(i)]
            else:
                attachment = ""

            # send sms if activated:
            if sendsms == True:
                smssender(sendername, time, message)

            # send mail if activated:
            if sendmail == True:
                print("Signalbot is sending emails")
                sendemail(from_addr    = mailfrom,
                      addr_list = addr_list,
                      subject      = mailsubject,
                      message      = mailtext.encode("utf-8"),
                      attachment   = attachment,
                      timestamp    = timestamp,
                      login        = mailuser,
                      password     = mailpassword,
                      server       = smtpserver)

            # deleting attachment if necessary:
            if attachment != "":
                print(attachment)
                os.remove(attachment)
    if newmessage == False: print("No new messages - exiting.")
    # deleting content of signal message db
    if emptydb == True:
        f = open(os.path.dirname(__file__) + '/out', 'w')
        f.close()

    # check for responses via mail:
    if getmail == True:
        getresponse()
    if debug: print("DEBUG - main(): finished")

# Signal stores files without extension, we change that using the following function
def addfileextension(attachmentpath, attachmentname):
    if debug: print("DEBUG - addfileextension(): called")
    shutil.copyfile(attachmentpath + attachmentname, attachmentname)
    while True:
        try:
            output2, _ = Popen(['file', '-bi', attachmentname], stdout=PIPE).communicate()
            output = output2.decode('utf-8')
            mime = output.split(';', 1)[0].lower().strip()
            if debug: print("DEBUG - addfileextension - detected MIME: " + output)
            # it doesn't recognize AAC which is standard for voice messages. Therefore:
            if mime ==  "audio/x-hx-aac-adts":
                ext = os.path.extsep + 'aac'
            else:
                ext = mimetypes.guess_extension(mime, strict=False)
                if ext is None:
                    ext = os.path.extsep + 'undefined'
            if debug: print("DEBUG - addfileextension() - file extension: " + ext)
            filename = attachmentname + ext
            if debug: print("DEBUG - addfileextension() - filename: " + filename)
            os.rename(attachmentname, filename)
            break
        except OSError:
            # file not found
            print("addfileextension() error: file not found!")
            break
    if debug: print("DEBUG - addfileextension(): finished, returning string: " + str(filename))
    return(filename)

# scans the message db, gets useful informations and stores them in a dictionary
def messagehandler(file):
    if debug: print("DEBUG - messagehandler(): called")
    i = 0 # counter
    message = {'error' : "none"} # return dict
    with open(os.path.dirname(__file__) + '/out') as f:
        for line in f:
            while True:
                try:
                    jfile = json.loads(line)
                    break
                except ValueError:
                    if debug: print("DEBUG - messagehandler(): not yet a complete JSON value")
                    # Not yet a complete JSON value
                    line += next(f)

            # we got one dict for each message if there is a message inside:
            if debug: print("DEBUG - messagehandler() - dataMessage: " + str(jfile['envelope']['dataMessage']))
            # check if there is some informations inside
            if jfile['envelope']['dataMessage'] == None or (jfile['envelope']['dataMessage']['message'] == '' and jfile['envelope']['dataMessage']['attachments'] == None):
                if debug: print("DEBUG - messagehandler(): empty message")
                message['error_' + str(i)] = "empty message"
            else:
                # check if we are parsing messages from the right group:
                if jfile['envelope']['dataMessage']['groupInfo']['groupId'] == signalgroupid:
                    i += 1
                    if debug: print("DEBUG - messagehandler() - Message " + str(i) +" - JSON: " + str(jfile)) #debug

                    # all information nested in envelopes, example:
                    # {u'envelope': {u'callMessage': None, u'relay': None, u'timestamp': 1516112508515L, u'sourceDevice': 3, u'syncMessage': None, u'source': u'+4915773820452', u'isReceipt': False, u'dataMessage': {u'expiresInSeconds': 0, u'timestamp': 1516112508515L, u'message': u'Hier, ein Bild!', u'groupInfo': None, u'attachments': [{u'contentType': u'image/jpeg', u'id': 6987400019698322768L, u'size': 488025}]}}}

                    # timestamp includes milliseconds, we have to strip them:
                    jtime = datetime.datetime.utcfromtimestamp(float(str(jfile['envelope']['timestamp'])[0:-3]))
                    message['time_' + str(i)] = jtime
                    if debug: print("DEBUG - messagehandler() - Message " + str(i) +" - Time sent: " + str(jtime))

                    jsender = jfile['envelope']['source']

                    # contacts lookup:
                    message['sender_' + str(i)] = jsender
                    # check if number is known:
                    message['sendername_' + str(i)] = "unkown"
                    for j, k in contacts:
                        if k == jsender: message['sendername_' + str(i)] = j
                    if debug: print("DEBUG - messagehandler() - Message " + str(i) +" - sender name: " + str(contacts[0][result]))

                    jmessage = jfile['envelope']['dataMessage']['message']#.decode('cp1252').encode("utf-8")
                    if debug: print("DEBUG - messagehandler() - Message " + str(i) +" - Message: " + u''.join(jmessage).encode('utf-8')) # emoji encoding is complicated
                    message['message_' + str(i)] = jmessage
                    # insert info if message is empty:
                    if message['message_' + str(i)] == '':
                        message['message_' + str(i)] = "### nothing to display, message was empty ###"

                    if jfile['envelope']['dataMessage']['attachments']:
                        jattachmentlist = jfile['envelope']['dataMessage']['attachments']
                        jattachment = jattachmentlist[0]
                        if debug: print("DEBUG - messagehandler() - Message " + str(i) +" - Attachment name: " + str(jattachment['id']))
                        # check for size limit before proceeding:
                        attachmentsize = float(jattachment['size']) / 1000.0 / 1000.0
                        if attachmentsize < float(max_attachmentsize):
                            jattachmentfile = addfileextension(attachmentpath, str(jattachment['id']))
                            if jattachmentfile:
                                # check if MIME type was unknown to addfileextension():
                                if jattachmentfile[len(jattachmentfile)-9:] == 'undefined':
                                    if debug: print("DEBUG - messagehandler() - Message " + str(i) +" - Attachment: unknown file extension, skipping!")
                                    message['error_' + str(i)] = "unknown file extension, skipping!"
                                else:
                                    message['attachment_' + str(i)] = jattachmentfile
                        else:
                            jattachmentfile = addfileextension(attachmentpath, str(jattachment['id']))
                            if debug: print("DEBUG - messagehandler(): Attachment bigger than maximum size of " + max_attachmentsize + "MB, skipping!")
                            message['message_' + str(i)] += "\n##########\nAttention: Maximum attachment size of " + max_attachmentsize + "MB exceeded. The attachment " + jattachmentfile + " with size " + str(attachmentsize) + "MB wasn't sent!"
                    else:
                        if debug: print("DEBUG - messagehandler() - Message " + str(i) +" - Attachment: none")
                        jattachmentfile = '0'

                else:
                    print("Signalbot did not find new messages to send, aborting!")
        else:
            if debug: print("DEBUG - messagehandler(): no entry in message database")
            message['error_' + str(i)] = "no entry in database"
        if debug: print("DEBUG - messagehandler() - finished, returning dictionary: " + str(message))
    return message

# function handles sending of emails
def sendemail(from_addr, addr_list, subject, message, attachment, timestamp, login, password, server):
    if debug: print("DEBUG - sendemail(): called")
    msg = email.MIMEMultipart.MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = addr_list
    msg["Subject"] = subject
    # formating timestamp for mail header:
    msg["Date"] = email.utils.formatdate(time.mktime(timestamp.timetuple()))
    # attaching the actual message:
    msg.attach(email.MIMEText.MIMEText(message, 'plain', 'utf-8'))
    if attachment != "": # only if we really have an attachment..
        # .. try to find out MIME type and process it properly
        ctype, encoding = mimetypes.guess_type(attachment)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"

        maintype, subtype = ctype.split("/", 1)

        if maintype == "text":
            fp = open(attachment)
            # Note: we should handle calculating the charset
            attachm = email.MIMEText.MIMEText(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == "image":
            fp = open(attachment, "rb")
            attachm = email.MIMEImage.MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == "audio":
            fp = open(attachment, "rb")
            attachm = email.MIMEAudio.MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(attachment, "rb")
            attachm = email.MIMEBase.MIMEBase(maintype, subtype)
            attachm.set_payload(fp.read())
            fp.close()
            email.encoders.encode_base64(attachm)
        attachm.add_header("Content-Disposition", "attachment", filename=attachment)
        msg.attach(attachm)

    # sending the mail:
    server = smtplib.SMTP(server)
    server.starttls()
    server.login(login,password)
    server.sendmail(from_addr, addr_list.split(','), msg.as_string())
    server.quit()
    if debug: print("DEBUG - sendemail(): finished")

# Sending SMS:
def smssender(sendername, time, message):
    print("Signalbot is sending SMS")
    sms_rec_list = str(sms_receivers).split(",")
    api = clockwork.API(clockworkapikey)
    smsmsg = sendername + ", " + unicode(time) + ": " + message
    for s in sms_rec_list:
        message = clockwork.SMS(
            to = s,
            message = smsmsg)
            #message = sendername.encode('utf-8') + ", " + str(time) + ": " + message.encode('utf-8'))
        response = api.send(message)
        if response.success:
            print (response.id)
        else:
            print (response.error_code)
            print (response.error_message)

# looking for mail responses to send to group:
def getresponse():
    print("Signalbot is looking for mail responses")
    server = imapclient.IMAPClient(imapserver, ssl=True)
    try:
        server.login(mailuser, mailpassword)
    except c.Error, e:
        print 'Could not log in:', e
        sys.exit(1)

    # maybe implement to choose other folder?
    select_info = server.select_folder('INBOX')
    #print('%d messages in INBOX' % select_info[b'EXISTS'])
    msgdict = server.fetch('1:*', ['BODY.PEEK[]'])
    signal = ""
    for message_id, message in msgdict.items():
        e = email.message_from_string(message['BODY[]'])
        nicetime = dt_parse(e['Date'])
        sender = email.Header.decode_header(e['From'])
        signal += "At " + str(nicetime) + " " + sender[0][0]
        if len(sender) == 2: # don't lose important information!
            signal += " " + sender[1][0]
        signal += " wrote:\n"
        payload = e.get_payload()
        if isinstance(payload, list):
            for i in payload:
                ctype = i.get_content_type()
                if ctype == "text/plain":
                    signal += i.get_payload()
                if ctype in ['image/jpeg', 'image/png', 'image/gif']:
                    attachmentfile = i.get_filename()
                    print("attachment stored to " + attachmentfile)
                    open(attachmentfile, 'wb').write(i.get_payload(decode=True))
        else:
            signal += payload
        signal += "\n\n"
    #os.system(signal_cli_path + ' -u ' + signalnumber + ' send -m "' + signal.encode('utf-8') + '" -g ' + signalgroupid) # + ' -a /home/pi/bin/signalbot_testing/lueftung.png')
    print("Found new mails. The following message will be sent to group:\n")
    print(signal.encode('utf-8'))

# this is a ugly workaround to convert timestamps in python > 3.2, see https://stackoverflow.com/questions/26165659/python-timezone-z-directive-for-datetime-strptime-not-available#26177579
def dt_parse(t):
    ret = datetime.datetime.strptime(t[0:24],'%a, %d %b %Y %H:%M:%S') #e.g: Fri, 26 Jan 2018 12:36:52 +0100
    if t[26]=='+':
        ret-=datetime.timedelta(hours=int(t[27:29]),minutes=int(t[29:]))
    elif t[26]=='-':
        ret+=datetime.timedelta(hours=int(t[27:29]),minutes=int(t[29:]))
    return ret

if __name__ == '__main__':
    main()
