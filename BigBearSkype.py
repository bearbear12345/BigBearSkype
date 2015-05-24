import logging
import urllib
import json
import sys
import os
import re
from datetime import datetime
import time
import string

import Skype4Py

ADFLY_KEY=""
ADFLY_ID=""

# Youtube is cancer - 2015
youtube_categories = {
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "18": "Short Movies",
    "19": "Travel & Events",
    "20": "Gaming",
    "21": "Videoblogging",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology",
    "30": "Movies",
    "31": "Anime/Animation",
    "32": "Action/Adventure",
    "33": "Classics",
    "34": "Comedy",
    "35": "Documentary",
    "36": "Drama",
    "37": "Family",
    "38": "Foreign",
    "39": "Horror",
    "40": "Sci-Fi/Fantasy",
    "41": "Thriller",
    "42": "Shorts",
    "43": "Shows",
    "44": "Trailers"
}


# Setup
bot_isLocked = False

senderHandle = None
chat = None
send = None

# Logging
if not os.path.isdir("logs/"):
    os.makedirs("logs")
log = logging.getLogger("BigBearSkype")
log.setLevel(logging.INFO)
log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_out = logging.StreamHandler()
log_out.setFormatter(log_format)
log.addHandler(log_out)
log_file = logging.FileHandler("logs/bot.log")
log_file.setFormatter(log_format)
log.addHandler(log_file)
# Direct output to file
logger_direct = logging.getLogger("BigBearSkype_direct")
logger_direct.setLevel(logging.INFO)
logger_direct_file = logging.FileHandler("logs/bot.log")
logger_direct_file.setFormatter(logging.Formatter("%(message)s"))
logger_direct.addHandler(logger_direct_file)
log_direct = logger_direct.info
log_direct("==========" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "==========")

# Functions
# Utility Functions
def util_restartscript():
    log.info("BearNet Bot restarting")
    os.execl(sys.executable, sys.executable, *sys.argv)


def util_getresponsefiles():
    return "\n".join(os.listdir("config/file_responses/"))


def util_managebans(action, user):
    if action == "add" and user not in config_banned_users:
        config_banned_users.append(user)
    elif action == "remove" and user in config_banned_users:
        config_banned_users.remove(user)
    config_banned_users.sort()
    with open('config/banned_users.txt', "w") as f:
        f.write("\n".join(config_banned_users))
    return config_banned_users


# User Commands
def command_adfly(url):
    global senderHandle
    log.info("[%s] Adf.ly Link: %s" % (senderHandle, url))
    result = urllib.urlopen(
        "http://api.adf.ly/api.php?key=" + ADFLY_KEY + "&uid=" + ADFLY_ID + "&advert_type=int&domain=adf.ly&url=" + url).read()
    if result != "":
        return result
    raise Exception("Invalid link!")


def command_chatinfo():
    global chat
    global senderHandle
    log.info("[%s] Chat Info" % senderHandle)
    if chat.Topic == "":
        chatname = chat.Name
    else:
        chatname = chat.Topic
    return "Name: " + chatname + "\nMembers: " + str(len(chat.Members)) + "\nMessages: " + str(len(chat.Messages))


def command_github(string):
    global senderHandle
    array = string.split()
    if len(array) == 1:
        log.info("[%s] GitHub(%s)" % (senderHandle, array[0]))
        data = urllib.urlopen("https://api.github.com/users/%s" % array[0])
        if data.getcode() == 200:
            data = json.loads(data.read())
            data_id = "User ID: %s\n" % data["id"]
            data_name = "Name: %s\n" % data["name"] if data["name"] != "" else ""
            data_email = "Email: %s\n" % data["email"] if data["email"] != "" else ""
            data_company = "Company: %s\n" % data["company"] if data["company"] != "" else ""
            data_location = "Location: %s\n" % data["location"] if data["location"] != "" else ""
            data_bio = "Biography: %s\n" % data["bio"] if data["bio"] is not None else ""
            data_blog = "Blog Address: %s\n" % data["blog"] if data["blog"] != "" else ""
            data_public_repos = "Public Repositories: %s\n" % data["public_repos"]
            data_public_gists = "Public Repositories: %s\n" % data["public_gists"]
            data_followers = "Followers: %s\n" % data["followers"]
            data_following = "Users Followed: %s\n" % data["following"]
            data_url = "User Link: " + data["html_url"]
            return "====GitHub Info====\n%s\n===================" % (
                data_id + data_name + data_email + data_company + data_location + data_bio + data_blog + data_public_repos + data_public_gists + data_followers + data_following + data_url)
        elif data.getcode() == 404:
            raise Exception("Error 404: No Such GitHub User '%s'Exists!" % array[0])
        else:
            raise Exception("Function 'command_github(%s)' has encountered an error! Error code %s" % (
                array[0], data.getcode()))
    else:
        data = urllib.urlopen("https://api.github.com/repos/%s/%s" % (array[0], array[1]))
        if data.getcode() == 200:
            data = json.loads(data.read())
            data_owner = "Owner: %s\n" % data["owner"]["login"]
            data_repository = "Repository: %s\n" % data["name"]
            data_description = "Description: %s\n" % data["description"]
            data_url = "Repo Link: " + data["html_url"]
            return "====GitHub Info====\n%s\n===================" % (
                data_owner + data_repository + data_description + data_url)
        elif data.getcode() == 404:
            raise Exception(
                "Error 404: No Such GitHub Repository/User Exists!\nUser: %s\nRepository: %s" % (array[0], array[1]))
        else:
            raise Exception("Function 'command_github(%s, %s)' has encountered an error! Error code %s" % (
                array[0], array[1], data.getcode()))


def command_isup(url):
    global senderHandle
    log.info("[%s] Is Up: %s" % (senderHandle, url))
    page = urllib.urlopen("http://downforeveryoneorjustme.com/" + url.lower()).read()
    if "If you can see this page and still think we're down, it's just you." in page:
        return url + " Is UP"
    if "It's just you." in page and "is up." in page:
        return url + " Is UP"
    if "It's not just you!" in page and "looks down from here." in page:
        return url + " Is DOWN"
    if "Huh? " in page and "doesn't look like a site on the interwho." in page:
        raise Exception(url + " is not a valid address!")
    raise Exception("Function 'command_isup(%s)' has encountered an error!" % url)


def command_listresponsefiles():
    log.info("[%s] List response files" % senderHandle)
    return "Files:\n" + util_getresponsefiles()


def command_readresponsefile(filename):
    if "/" in filename:
        raise Exception("Blocked reading file '%s'! File out of scope!\n\"In other words... No. - Andrew\"" % filename)
    try:
        with open("config/file_responses/" + filename, "r") as f:
            return f.read()
    except IOError:
        raise Exception("File '%s' does not exist!\nAvailable files:\n%s" % (filename, util_getresponsefiles()))


def command_youtube(link):
    global senderHandle
    if len(link) == 11:
        v_id = link
    else:
        youtube_regex = re.match(
            "(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})",
            link)
        if youtube_regex:
            v_id = youtube_regex.group(6)
        else:
            raise Exception("Invalid YouTube URL!")
    video=json.loads(urllib.urlopen("https://www.googleapis.com/youtube/v3/videos?key=AIzaSyBNCS8xcoVeSLDIJZ3qqgtwbt2bEfv-KWw&part=snippet,contentDetails,statistics&fields=items(snippet(title,description,categoryId),contentDetails(duration),statistics(viewCount,likeCount,dislikeCount))&id="+v_id).read())['items']
    if len(video[0]) == 0:
        raise Exception("Invalid YouTube Video ID!")
    log.info("[%s] YouTube ID: %s" % (senderHandle, v_id))
    video = video[0]
    data_title = "[ Title ] %s\n" % video['snippet']['title']
    data_category = "[ Video Category ] %s\n" % youtube_categories[video['snippet']['categoryId']]
    # Youtube video duration... WTF.
    duration = ""
    for character in video['contentDetails']['duration'].replace("P","").replace("T","").lower():
        duration += character
        if character in string.ascii_lowercase:
            duration += " "
    duration = duration[:-1]
    data_duration = "[ Duration ] %s\n" % duration
    data_views = "[ Views ] %s\n" % video['statistics']['viewCount']
    data_rating = "[ Likes ] %s\n[ Dislikes ] %s\n[ Rating ] %s%%\n" % (video['statistics']['likeCount'],video['statistics']['dislikeCount'],str(round(int(video['statistics']['likeCount'])*100/float(int(video['statistics']['likeCount'])+int(video['statistics']['dislikeCount'])),2)))
    data_url = "[ YouTube URL ] http://youtu.be/%s\n" % v_id
    data_description = "[ Description ]\n" + video['snippet']['description']
    return "==========\n%s\n==========" % ( data_title + data_category + data_duration + data_views + data_rating + data_url + data_description)


# Admin Commands
def command_a_ban(string):
    global config_banned_users
    user_array = string.split()[1:]
    action = string.split()[0]
    if action == "reload":
        log.info("[ADMIN] [%s] Reload banned users" % senderHandle)
        config_banned_users = []
        bannedFile = open("config/banned_users.txt", "r")
        for line in bannedFile.readlines():
            name = line.replace("\n", "")
            config_banned_users.append(name)
            config_banned_users.sort()
        bannedFile.close()
        return "Reloaded banned users! Ban list contains %s name(s)!" % str(len(config_banned_users))

    elif action == "list":
        log.info("[ADMIN] [%s] List banned users" % senderHandle)
        if len(config_banned_users) == 0:
            return "No users are banned!"
        return "Banned Users: '%s'" % "', '".join(config_banned_users)
    elif action == "add" or action == "remove":
        for user in user_array:
            util_managebans(action, user)
            log.info("[ADMIN] [%s] %s user '%s'" % (senderHandle, "Banned" if action == "add" else "Pardoned", user))
        return "User(s): '%s' %s" % (
            "', '".join(user_array), "have been banned!" if action == "add" else "have been pardoned!")
    else:
        raise Exception("Invalid command arguments\nUsage:\n!ban (add/remove) (username) [username] [...]\n!ban list")


# def command_a_kick():
# def command_a_mute():
def command_a_lock(lockstatus):
    global bot_isLocked
    if lockstatus:
        log.info("[ADMIN] [%s] Lock bot" % senderHandle)
        bot_isLocked = True
        skype.CurrentUserStatus = Skype4Py.enums.cusAway
        return "BearNet Bot Locked!"
    else:
        log.info("[ADMIN] [%s] Unlock bot" % senderHandle)
        bot_isLocked = False
        skype.CurrentUserStatus = Skype4Py.enums.cusSkypeMe
        return "BearNet Bot Unlocked!"


def command_a_register(action):
    global chat
    if action == "register":
        log.info("[ADMIN] [%s] Register chat" % senderHandle)
        if not chat.Bookmarked:
            chat.Bookmark()
        return "Chat group \"%s\" registered!" % chat.Name
    elif action == "unregister":
        log.info("[ADMIN] [%s] Unregister chat" % senderHandle)
        if chat.Bookmarked:
            chat.Unbookmark()
        return "Chat group \"%s\" unregistered!" % chat.Name
    # else list
    log.info("[ADMIN] [%s] Check if chat is registered" % senderHandle)
    return "Chat group \"%s\" is %sregistered" % (chat.Name, "" if chat.Bookmarked else "not ")


def command_a_restart():
    global send
    log.info("[ADMIN] [%s] Restart bot" % senderHandle)
    send("BearNet Bot Restarting!")
    util_restartscript()


def command_a_updatebot():
    global send
    log.info("[ADMIN] [%s] Update bot" % senderHandle)
    send("Updating bot!\nDownloading script...")
    os.system(
        "wget github.com/bearbear12345/BigBearSkype/raw/master/BigBearSkype.py -O BigBearSkype.py --no-check-certificate")
    send("Download complete!\nRestarting...")
    util_restartscript()

# Command dictionary
command_list = {
    # COMMAND: command, parameters, use_args, admin
    "adfly": {"command": command_adfly,
              "parameters": "",
              "use_args": True,
              "usage": "(link) ",
              "admin": False,
    },
    "ban": {"command": command_a_ban,
            "parameters": "",
            "use_args": True,
            "usage": "\n(add/remove) (username) [username] [...]\n!ban list",
            "admin": True,
    },
    "chat": {"command": command_chatinfo,
             "parameters": "",
             "use_args": False,
             "usage": "",
             "admin": False,
    },
    "get": {"command": command_readresponsefile,
            "parameters": "",
            "use_args": True,
            "usage": "(filename)",
            "admin": False,
    },
    "github": {"command": command_github,
               "parameters": "",
               "use_args": True,
               "usage": "(username) [repository]",
               "admin": False,
    },
    "help": {"command": command_readresponsefile,
             "parameters": "help.txt",
             "use_args": False,
             "usage": "",
             "admin": False,
    },
    "info": {"command": command_readresponsefile,
             "parameters": "info.txt",
             "use_args": False,
             "usage": "",
             "admin": False,
    },
    "isup": {"command": command_isup,
             "parameters": "",
             "use_args": True,
             "usage": "(url)",
             "admin": False,
    },
    "listfiles": {"command": command_listresponsefiles,
                  "parameters": "",
                  "use_args": False,
                  "usage": "",
                  "admin": False,
    },
    "lock": {"command": command_a_lock,
             "parameters": True,
             "use_args": False,
             "usage": "",
             "admin": True,
    },
    "read": {"command": command_readresponsefile,
             "parameters": "",
             "use_args": True,
             "usage": "(filename)",
             "admin": False,
    },
    "register": {"command": command_a_register,
                 "parameters": "register",
                 "use_args": False,
                 "usage": "",
                 "admin": True,
    },
    "restart": {"command": command_a_restart,
                "parameters": "",
                "use_args": False,
                "usage": "",
                "admin": True,
    },
    "shorten": {"command": command_adfly,
                "parameters": "",
                "use_args": True,
                "usage": "(link)",
                "admin": False,
    },
    "unlock": {"command": command_a_lock,
               "parameters": False,
               "use_args": False,
               "usage": "",
               "admin": True,
    },
    "unregister": {"command": command_a_register,
                   "parameters": "unregister",
                   "use_args": False,
                   "usage": "",
                   "admin": True,
    },
    "updatebot": {"command": command_a_updatebot,
                  "parameters": "",
                  "use_args": False,
                  "usage": "",
                  "admin": True,
    },
    "youtube": {"command": command_youtube,
                "parameters": "",
                "use_args": True,
                "usage": "\n(YouTube Video ID)\n!youtube (YouTube Video URL)",
                "admin": False,
    },
    "yt": {"command": command_youtube,
           "parameters": "",
           "use_args": True,
           "usage": "\n(YouTube Video ID)\n!yt (YouTube Video URL)",
           "admin": False,
    },
}


# Hooks
# Not sure why this is needed
def onattachmentstatus(status):
    if status == Skype4Py.apiAttachAvailable:
        skype.Attach()
    if status == Skype4Py.apiAttachSuccess:
        log.info("API connected to the Skype process!")
        log.info("------------------------------------------------------------------------------")
    skype.CurrentUserStatus = Skype4Py.enums.cusSkypeMe


# Auto accept users who send a friend request
def onuserauthorizationrequestreceived(user):
    log.info(user.Handle + "sent a contact request! Accepting...")
    user.IsAuthorized = True


def onmessagestatus(message, status):
    global senderHandle
    global chat
    global send
    msg = message.Body
    chat = message.Chat
    send = chat.SendMessage
    senderHandle = message.FromHandle
    if status == 'RECEIVED':
        if msg.startswith("!"):
            command_name = msg.split()[0][1:]
            if not bot_isLocked:
                if command_name in command_list:
                    if senderHandle in config_banned_users:
                        send("%s, you are banned and cannot use commands!" % senderHandle)
                    elif command_list[command_name]["admin"] and senderHandle not in config_admins:
                        send("%s, you do not have permission to use this command!" % senderHandle)
                    elif not chat.Bookmarked and senderHandle not in config_admins:
                        send(
                            "%s, unfortunately this chat group is not registered! Contact Andrew Wong (aw9292929296983244) for assistance." % senderHandle)
                    else:
                        try:
                            arguments = " ".join(msg.split()[1:])
                            command = command_list[command_name]
                            if command["use_args"]:
                                if len(arguments) == 0:
                                    send("Invalid command arguments!\nUsage: !%s %s" % (command_name, command["usage"]))
                                else:
                                    if command["parameters"] == "":
                                        send(command["command"](arguments))
                                    else:
                                        send(command["command"](command["parameters"], arguments))
                            else:
                                if len(arguments) != 0:
                                    send("Invalid command arguments!\nUsage: !" + command_name)
                                else:
                                    if command["parameters"] == "":
                                        send(command["command"]())
                                    else:
                                        send(command["command"](command["parameters"]))
                        except Exception as err:
                            log.warn(err.message)
                            send(err.message)
            else:
                if command_name == "unlock":
                    send(command_list["unlock"]["command"](False))

# Program
log.info("Starting BearNet Bot...")
log.debug("Initialising Skype4Py Instance")
skype = Skype4Py.Skype(Transport="x11")
log.debug("Attaching onattachmentstatus event")
skype.OnAttachmentStatus = onattachmentstatus
log.debug("Attaching onmessagestatus event")
skype.OnMessageStatus = onmessagestatus
log.debug("Attaching onuserauthorizationrequestreceived event")
skype.OnUserAuthorizationRequestReceived = onuserauthorizationrequestreceived
log.debug("Setting Skype4Py friendly name to 'BearNet Bot'")
skype.FriendlyName = "BearNet Bot"
log.debug("Checking if Skype is running")
if not skype.Client.IsRunning:
    log.info("Skype is not running!")
    skype.Client.Start()
    log.info("Waiting for Skype to start...")
while not skype.Client.IsRunning:
    time.sleep(1)
log.info("Connecting API to Skype...")
try:
    skype.Attach()
except Exception as err:
    log.error("Error: " + err.message)
    sys.exit()
log.info("Loading configuration files...")
log.debug(" Loading ban list...")
config_banned_users = []
bannedFile = open("config/banned_users.txt", "r")
for line in bannedFile.readlines():
    name = line.replace("\n", "")
    config_banned_users.append(name)
    config_banned_users.sort()
bannedFile.close()
log.debug("  Banned users list contains %s names." % str(len(config_banned_users)))
log.debug(" Loading admin list...")
config_admins = []
adminList = open("config/admins.txt", "r")
for line in adminList.readlines():
    name = line.replace("\n", "")
    config_admins.append(name)
    config_admins.sort()
adminList.close()
log.debug("  Admin list contains %s names." % str(len(config_admins)))
log.info("Bot loaded!")
while True:
    time.sleep(1)
