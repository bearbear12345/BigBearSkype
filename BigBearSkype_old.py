
## Todo
# Command ban (per user)
# Command ban (per group)
# Command disable
# Adf.ly !adfly .gif.ng.jpeg.whoknow....penusta -> [10:25:22 PM] BearNet: Shortened Link:
# .tolowercase() commands
# rewrite
# !ban list
# youtube
# Don't adfly and adf.ly link
# Disable emoticons ??? "!! "
# Adfly no "."
# Leave group if no perm

#IMPORTS
import hashlib
import os
import random
import re
import string
import sys
import json
import time
import urllib
import Skype4Py
import inspect
import urllib2
import gdata.youtube
import gdata.youtube.service
import socket
sys.path.append('lib') #Add library files
from minecraft_query import MinecraftQuery
import requests

#CONFIG
admin = 'aw9292929296983244'
bot_account = 'bearnetbot'

ADFLY_KEY=""
ADFLY_ID=""
#SETUP
yt_service = gdata.youtube.service.YouTubeService()
bannedList = []
lock = False

"""
METHODS
"""
#YouTube video information
def youtube(v_id, sender, senderDisplay):
    global bot_account
    if sender != bot_account:
        x = ''
        entry = yt_service.GetYouTubeVideoEntry(video_id=v_id)
        x += '-' * 10 + '\n'
        print('YouTube ID: %s' % v_id)
        # Title
        x += 'Title: %s' % entry.media.title.text + "\n"
        # Duration
        duration = int(entry.media.duration.seconds)
        if duration / 60 < 1:
            x += 'Duration: %ss' % int(duration) + '\n'
        elif duration % 60 == 0:
            x += 'Duration: %sm' % str(duration / 60) + '\n'
        else:
            duration_a = duration
            duration = str(duration / 60)
            duration_decimal = str(float(duration)).index('.')
            duration_minutes = str(float(duration))[:duration_decimal]
            duration_seconds = int(duration_a) % 60
            x += 'Duration: ' + str(int(duration_minutes)) + 'm ' + str(int(duration_seconds)) + 's\n'
        # Views
        x += 'Views: %s' % entry.statistics.view_count + '\n'
        # Rating
        if entry.rating is None:
            x += 'Average rating: No Ratings\n'
        else:
            youtube_rating = round(float(entry.rating.average), 2)
            x += 'Average rating: %s/5' % str(youtube_rating) + '\n'
        # URL
        x += 'YouTube URL: http://youtu.be/' + v_id + '\n'
        # Category
        x += 'Video category: %s' % entry.media.category[0].text + '\n'
        # Description
        x += 'Description: \n\n'
        x += entry.media.description.text + '\n'
        x += '-' * 10
        print(x)
        return x

def github(user, repo):
    r = requests.get('https://api.github.com/repos/' + user + '/' + repo)
    if (r.ok):
        repoItem = json.loads(r.text or r.content)
        x = ""
        x += "====GitHub Info====\n"
        x += "Owner: " + repoItem['owner']['login'] + "\n"
        x += "Repository: " + repoItem['name'] + "\n"
        x += "Description: " + repoItem['description'] + "\n"
        x += "Repo Link: " + repoItem['html_url'] + "\n"
        x += "==============="
        return x
    elif r.status_code == 404:
        return "No Such GitHub Repository and/or User"
#adf.ly link generator
def adfly(url):
    try:
        location = "http://api.adf.ly/api.php?key=" + ADFLY_KEY + "&uid=" + ADFLY_ID + "&advert_type=int&domain=adf.ly&url=" + url
        link = urllib.urlopen(location).read()
        return link
    except:
        return url

#Minecraft Server Status Check
"""
Old Code
def get_mc_info(host, port):
    #Set up our socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10.0)
    s.connect((host, port))
    #Send 0xFE: Server list ping
    s.send('\xfe')
    #Send a payload of 0x01 to trigger a new response if the server supports it
    s.send('\x01')
    #Read as much data as we can (max packet size: 241 bytes)
    d = s.recv(256)
    s.close()

    #Check we've got a 0xFF Disconnect
    assert d[0] == '\xff'
    #Remove the packet identity (0xFF) and the short containing the length of the string
    #Decode UCS-2 string
    d = d[3:].decode('utf-16be')
    #Check the first 3 characters of the string are what we expect
    assert d[:3] == u'\xa7\x31\x00'
    #Split
    d = d[3:].split('\x00')
    result = 'Server MOTD: ' + d[2] + "\n"
    result = result + 'Players: ' + d[3] + '/' + d[4]
    return result
""" #Old Code
def get_mc_info(host, port, cmode):
    #github.com/Dinnerbone/mcstatus
    try:
        query = MinecraftQuery(host, port, timeout=10, retries=3)
        server_data = query.get_rules()
    except socket.error as e:
        print("socket exception caught:", e.message)
        return "Server is down or unreachable."
        pass
    #Dict into array
    z = []
    if cmode == 2:
        for k, v in server_data.iteritems():
            z.append(str(k) + ": " + str(v))
    else:
        z_allstring = []
        for k, v in server_data.iteritems():
            z.append(v)
            z_allstring.append(str(v))
    """
    map - 0 - Map name
    motd - 1 - Message of the Day
    hostport - 2 - Port
    numplayers - 3 - Current Players
    gametype - 4 - Game type
    players - 5 - Array of players online
    version - 6 - MC Version
    maxplayers - 7 - Maximum players
    plugins - 8 - Array of plugins
    raw_plugins - 9 - String of plugins
    game_id - 10 - Game ID? Always "MINECRAFT"?
    hostip - 11 - IP
    software - 12 - Server software
    """
#Array into string
    #cmode = 0 - Basic
    if cmode == 0:
        r = "MOTD: " + z_allstring[1] + "\n"
        r = r + "MC Version: " + z_allstring[6] + "\n"
        r = r + "Game Type: " + z_allstring[4] + "\n"
        r = r + "Player Count: " + z_allstring[3] + "/" + z_allstring[7]
    #cmode = 1 - Full
    elif cmode == 1:
        r = "Game ID: " + z_allstring[10] + "\n"
        r = r + "MOTD: " + z_allstring[1] + "\n"
        r = r + "Host IP: " + z_allstring[11] + "\n"
        r = r + "Host Port: " + z_allstring[2] + "\n"
        r = r + "Map: " + z_allstring[0] + "\n"
        r = r + "MC Version: " + z_allstring[6] + "\n"
        r = r + "Game Type: " + z_allstring[4] + "\n"
        r = r + "Player Count: " + z_allstring[3] + "/" + z_allstring[7] + "\n"
        if z_allstring[3] != "0":
            output = ""
            for player in z[5]:
                output = output + player + ", "
            output = output[:-2] #Gets rid of final ", "
            r = r + "Online Players: " + output + "\n"
        if z_allstring[12] == "":
            r += "Server Software: Vanilla\n"
        else:
            r += "Server Software: " + z_allstring[12] + "\n"
            plugin_o = "[No Plugin(s) Installed!]"
            if len(z[8]) != 0:
                plugin_o = ""
                for plugin in z[8]:
                    plugin_o = plugin_o + plugin + ", "
                plugin_o = plugin_o[:-2] #Gets rid of final ", "
            r += "Plugins: " + plugin_o + "\n"
            r += "Raw Plugins: " + z_allstring[9] + "\n"
    #cmode = 2 - RAW
    elif cmode == 2:
        r = ""
        for x in z:
            r += x + "\n"
    return r

#Check if website is Up
def isUP(url):
    url = url.lower()
    socket = urllib.urlopen("http://downforeveryoneorjustme.com/" + url)
    html = socket.read()
    socket.close()
    if "If you can see this page and still think we're down, it's just you." in html:
        return url + " Is UP"
    if "It's just you." in html and "is up." in html:
        return url + " Is UP"
    if "It's not just you!" in html and "looks down from here." in html:
        return url + " Is DOWN" 
    if "Huh? " in html and "doesn't look like a site on the interwho." in html:
        return url + " is not a valid address!"

#Get md5 hash
def md5(word):
    md5 = hashlib.md5(word)
    return md5.hexdigest()

#Update List
def updateList(list):
    global bannedList
    if list == 'banned':
        bannedFile = open('database/banned.txt', 'w')
        for name in bannedList:
            bannedFile.write(name + '\n')
        bannedList.sort()
        bannedFile.close

#Check if bot account is an admin of said group
def getAdmin(chat):
    if chat.MyRole == 'MASTER' or chat.MyRole == 'CREATOR':
        return True
    else:
        return False

#Get chat information
def chatInfo(chat):
    if chat.Topic == '':
        chatName = chat.Name
    else:
        chatName = chat.Topic
    return 'Name: ' + chatName + '\nMembers: ' + str(len(chat.Members)) + '\nMessages: ' + str(len(chat.Messages))

"""
Event Overrides
"""
#Auto Contact Add
def OnUserAuthorizationRequestReceived(user):
    print(user.Handle + "sent a contact request! Accepting...")
    user.IsAuthorized = True
        
#SKYPE4PY API
def OnAttachmentStatus(status):
    if status == Skype4Py.apiAttachAvailable:
        skype.Attach()
        return
    if status == Skype4Py.apiAttachSuccess:
        print('API connected to the Skype process!')
        print('------------------------------------------------------------------------------')
        return
    statusAPI = skype.Convert.AttachmentStatusToText(status)
    print('API ' + statusAPI.lower() + '...')
    skype.CurrentUserStatus = Skype4Py.enums.cusSkypeMe


#COMMANDS
def OnMessageStatus(Message, Status):
    global admin
    global bot_account
    global lock
    global bannedList
    global y
    global y_short
    try:
        y = 'youtube.com/watch?'
        y_short = 'youtu.be/'
        msg = Message.Body
        chat = Message.Chat
        send = chat.SendMessage
        senderDisplay = Message.FromDisplayName
        senderHandle = Message.FromHandle
        message = ''
        chat_not_registered_message = "BearNet Bot is not registered for this chat! Please contact Andrew Wong (aw9292929296983244) for assistance on registering"

        if lock:
            if Status == 'RECEIVED' and senderHandle == 'aw9292929296983244':
                if msg == '!unlock':
                    lock = False
                    skype.CurrentUserStatus = Skype4Py.enums.cusSkypeMe
                    print("BearNet Bot Unlocked!")
                    send('BearNet Bot Unlocked!')
        
        elif lock is False:
            if Status == 'RECEIVED':
###############################################################
 #               print(senderHandle + ":", msg)
 #               #Check for caps spam
 #               letters =
 #               "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
 #               lowercaps = 0
 #               uppercaps = 0
 #               for x in msg.replace(" ",""):
 #                     if x in letters:
 #                       if x.isupper():
 #                           uppercaps += 1
 #                       else:
 #                            lowercaps += 1
 #               if uppercaps > lowercaps:
 #                   msg_temp = msg.lower()
 #                   Message.Body = msg_temp
###############################################################
                if senderHandle in bannedList:
                    if msg.startswith('!shorten ') or msg.startswith('!adfly ') or msg == "!chat" or msg.startswith('!github ') or msg == '!help' or msg == '!info' or msg.startswith('!isup ') or msg.startswith('!mc ') or msg.startswith('!md5 ') or msg.startswith('!youtube ') or msg.startswith('!yt ') or msg.startswith('.'):
                        send(senderHandle + ": You are banned!")

                elif senderHandle not in bannedList:
                    if msg.startswith('!shorten ') or msg.startswith('!adfly '):
                        msg = msg.replace('!shorten ', '', 1)
                        msg = msg.replace('!adfly ', '', 1)
                        send("Shortened Link: " + adfly(msg))

                    elif msg == "!chat":
                        send(chatInfo(chat))

                    elif msg.startswith('!github '):
                        msg = msg.replace('!github ', '', 1)
                        msg = msg.split()
                        if len(msg) == 2:
                            user = msg[0]
                            repo = msg[1]
                            send(github(user,repo))
                        else:
                            send("Incorrect Command Syntax!\nCorrect syntax: !github (user) (repository)")

                    elif msg == '!help':
                        helpFile = open('help.txt','r')
                        for line in helpFile.readlines():
                            message += line
                        send(message)
                        helpFile = None
                        message = None
                        
                    elif msg == '!info':
                        infoFile = open('info.txt','r')
                        for line in infoFile.readlines():
                            message += line
                        send(message)
                        infoFile = None
                        message = None
                        
                    elif msg.startswith('!isup '):
                        url = msg.replace('!isup ', '', 1).replace('http://', '', 1).replace('https://', '', 1)
                        send(isUP(url))
                        url = None
                        
                    elif msg.startswith('!mc '):
                        if chat.Bookmarked or senderHandle == 'aw9292929296983244':
                            mcport = 25565
                            url = msg.replace('!mc ', '', 1)
                            nurl = url.lower().split()
                            cmode = 0
                            if len(nurl) == 2:
                                if nurl[1] == "full":
                                    cmode = 1
                                elif nurl[1] == "raw":
                                    cmode = 2
                            if nurl[0] == "bearcrack":
                                y = get_mc_info("bearcrack.mooo.com", 25565, cmode)
                                nurl[0] = "BearCrack"
                            else:
                                if ':' in nurl[0]:
                                    mc_index = nurl[0].index(':') + 1
                                    mcport = nurl[0][mc_index:]
                                    mc_address = nurl[0][:mc_index - 1]
                                if mcport == 25565:
                                    y = get_mc_info(nurl[0], 25565, cmode)
                                else:
                                    y = get_mc_info(mc_address, int(mcport), cmode)
                            result = nurl[0] + ' Details: \n'
                            result = result + y
                            send(result)
                            result = None
                            url = None
                            mcport = None
                            cmode = None
                            mc_index = None
                            mc_address = None                         
                        else:
                            send(chat_not_registered_message)

                    elif msg.startswith('!md5 '):
                        word = msg.replace('!md5 ', '', 1)
                        send('MD5 Hash : ' + md5(word))
                        word = None

                    elif msg.startswith('!youtube ') or msg.startswith('!yt ') or msg.startswith('.'):
                        msg = msg.replace('!youtube ', '', 1)
                        msg = msg.replace('!yt ', '', 1)
                        if len(msg) == 11 or y in msg or y_short in msg:
                            if chat.Bookmarked or senderHandle == 'aw9292929296983244':
                                if len(msg) == 11: #Exact 11 character Youtube ID was entered
                                    result = youtube(msg, senderHandle, senderDisplay)
                                elif y in msg or y_short in msg:
                                    v_id = msg
                                    if y in msg:
                                        v_id_1 = v_id.index('?v=') + 3
                                        v_id_2 = v_id_1 + 11
                                        v_id = v_id[v_id_1:v_id_2]
                                    else:
                                        v_id_1 = v_id.index('youtu.be/') + 9
                                        v_id_2 = v_id_1 + 11
                                        v_id = v_id[v_id_1:v_id_2]
                                    result = youtube(v_id, senderHandle, senderDisplay)
                                print('[INFO] ' + senderDisplay + ' (' + senderHandle + ') sent a YouTube link!')
                                send(result)
                            else:
                                send(chat_not_registered_message)
                        msg = None
                        result = None
                        y = None
                        v_id = None
                        v_id_1 = None
                        v_id_2 = None

            #ADMIN COMMANDS (aw9292929296983244 ONLY)
            if Status == 'RECEIVED' and senderHandle == 'aw9292929296983244':
                        if msg == '!lock':
                            lock = True
                            skype.CurrentUserStatus = Skype4Py.enums.cusAway
                            print('BearNet Bot Locked!')
                            send('BearNet Bot Locked!')
                            
                        elif msg.startswith("!register"):
                            if not chat.Bookmarked:
                                chat.Bookmark()
                                send("Chat Group \"" + chat.Name + "\" registered!")
                                
                            else:
                                send("Chat Group \"" + chat.Name + "\" is already registered!")
                                
                        elif msg.startswith("!unregister"):
                            if chat.Bookmarked:
                                chat.Unbookmark()
                                send("Chat Group \"" + chat.Name + "\" unregistered!")
                                
                            else:
                                send("Chat Group \"" + chat.Name + "\" was not even registered!")

                        elif msg == '!restart':
                            python = sys.executable
                            send('BearNet Bot Restarting!')
                            os.execl(python, python, * sys.argv)

                        elif msg == '!updatebot':
                            send('Updating Bot!\nDownloading script...')
                            os.system("wget github.com/bearbear12345/BigBearSkype/raw/master/src/BigBearSkype.py -O BigBearSkype.py -P /skype/BigBearSkype --no-check-certificate")
                            send("Download complete!\nUpdating script!")
                            send("Update complete!\nRestarting!")
                            os.execl(sys.executable, sys.executable, * sys.argv)
                            
                            
##                        elif msg.startswith('!mute '):
##                            if getAdmin(chat) == True:
##                                user = msg.replace('!mute ', '', 1)
##                                status = False
##                                for name in chat.MemberObjects:
##                                    if name.Handle == user and name.Role !=
##                                    'LISTENER':
##                                        status = True
##                                    else:
##                                        pass
##                                if status == True:
##                                    try:
##                                        send(user + ', you have been muted!
##                                        No one can hear/see your chats.')
##                                        send('/setrole ' + user + '
##                                        LISTENER')
##                                    except:
##                                        pass
##                                else:
##                                    send(user + ' is not found in this chat
##                                    or is already muted!')
##                        elif msg.startswith('!unmute '):
##                            if getAdmin(chat) == True:
##                                user = msg.replace('!unmute ', '', 1)
##                                status = False
##                                for name in chat.Members:
##                                    if name.Handle == user and name.Role ==
##                                    'LISTENER':
##                                        status = True
##                                    else:
##                                        pass
##                                if status == True:
##                                    try:
##                                        send(user + ', you have been
##                                        unmuted.')
##                                        send('/setrole ' + user + ' USER')
##                                    except:
##                                        pass
##                                else:
##                                    send(user + ' is not found in this chat
##                                    or is already unmuted!')
                        elif msg.startswith('!ban '):
                            if msg.startswith('!ban add '):
                                name = msg.replace('!ban add ', '', 1)
                                if name in bannedList:
                                    send('User ' + name + ' is already banned!')
                                elif name not in bannedList:
                                    bannedList.append(name)
                                    bannedList.sort()
                                    updateList('banned')
                                    send('User ' + name + ' has been banned!')
                            elif msg.startswith('!ban remove '):
                                name = msg.replace('!ban remove ', '', 1)
                                if name in bannedList:
                                    bannedList.remove(name)
                                    bannedList.sort()
                                    updateList('banned')
                                    send('User ' + name + ' has been unbanned!')
                                elif name not in bannedList:
                                    send('User ' + name + ' is not banned!')
                            elif msg.startswith('!ban list'):
                                message = ""
                                for name in bannedList:
                                    message += name + ", "
                                send("Banned Username(s): " + message)
                            
    except:
        #I am a lazy person and can't be bothered to handle exceptions
        #properly.
        if str(sys.exc_info()[1]) == "{'status': 400, 'body': 'Invalid id', 'reason': 'Bad Request'}":
            send("YouTube Video Could Not Be Retrieved:\nError 400: Invalid YouTube Link!")
        elif str(sys.exc_info()[1]) == "{'status': 404, 'body': 'Video not found', 'reason': 'Not Found'}":
            send("YouTube Video Could Not Be Retrieved:\nError 404: Not Found!")
        elif str(sys.exc_info()[1]) == "[Errno 111] Connection refused":
            if mcport == 25565:
                send(url + " is OFFLINE")
            else:
                send(url + ":" + str(mcport) + " is OFFLINE")
        elif str(sys.exc_info()[1]) == "[Errno -2] Name or service not known":
            if mcport == 25565:
                send(url + " is non-existent")
            else:
                send(url + ":" + str(mcport) + " is non-existent")
        elif str(sys.exc_info()[1]) == "timed out":
            send("Connection Timed Out!")
        if str(sys.exc_info()[1]) == "getsockaddrarg: port must be 0-65535.":
            pass #Do Nothing
        else:
            print('[ERROR] ' + str(sys.exc_info()[1]))
##########################################################################
#START INSTANCE
print('******************************************************************************')
infoFile = open('info.txt','r')
for line in infoFile.readlines():
    print('- ' + line.replace('\n', ''))
print('Checking for Skype4Py API...')
try:
    import Skype4Py
    skype = Skype4Py.Skype(Transport='x11')
    skype.OnAttachmentStatus = OnAttachmentStatus
    skype.OnMessageStatus = OnMessageStatus
    skype.OnUserAuthorizationRequestReceived = OnUserAuthorizationRequestReceived
    skype.FriendlyName = 'BearNet'
    print('Skype4Py API found!')
except:
    print('Failed to locate Skype4Py API! Quitting...')
    print('******************************************************************************')
    sys.exit() 
try:
    print("Finding existing Skype instance")
    if not skype.Client.IsRunning:
        print("Skype not found!")
        skype.Client.Start()
        print("Waiting 15 seconds for Skype to start...")
        time.sleep(15)
    else: #Skype found
        print("Skype found!")   
except:
    print('Failed to start Skype process! Quitting...')
    print('******************************************************************************')
    sys.exit() 
print('Connecting API to Skype...')
try:
    skype.Attach()
except:
    print('Failed to connect API to Skype! Quitting...')
    print('******************************************************************************')
    sys.exit()
print('Loading banned list...')
bannedFile = open('database/banned.txt','r')
for line in bannedFile.readlines():
    name = line.replace('\n', '')
    bannedList.append(name)
    bannedList.sort()
bannedFile.close()
print('Banned list contains ' + str(len(bannedList)) + ' names!')
print('******************************************************************************')
#ENDLESS LOOP
while True:
    time.sleep(1)
