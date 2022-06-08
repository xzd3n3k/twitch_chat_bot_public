# imports
import time
from random import randint
import socket
import select
from collections import namedtuple
import json
from channelStatus import channel_status
from chatLog import ChatLog

# Message declaration
Message = namedtuple(
    'Message',
    'prefix user channel irc_command irc_args text'
)


class Twitch:
    # constructor
    def __init__(self, oauth, username, cfg='config.json', status_cfg='status_config.json'):
        # self.irc = None
        self.irc_server = 'irc.twitch.tv'
        self.irc_port = 6667
        self.oauth = oauth
        self.username = username    # TODO make multiaccount - load users from config
        self.cfg = cfg
        self.status_cfg = status_cfg
        self.loggers = []

        # opens config iterates channels and make chatLog instance for each channel
        with open('config.json', 'r') as configLog:
            data = json.load(configLog)

            for channel in data['channels']:
                self.loggers.append(ChatLog(channel))
        
        # connect to socket and authorize
        self.irc = socket.socket()
        self.irc.connect((self.irc_server, self.irc_port))
        self.send_command(f'PASS {self.oauth}')
        self.send_command(f'NICK {self.username}')
        
        # greeting map
        self.channel_map = [
            ["roshtein", [["yoo rosh", "hi", "hi rosh", "sup", "hello rosh", "good evening", "hi everyone"],
                          ["roshCARROT", "PauseChamp", "PauseShake", "ROSHI", "roshDab", "AlienPls", "vibePls",
                           "roshAbdul",
                           "YEPJAM", "WIGGLE"]]],
            ["ayezee", [["yoo zee", "hi", "hi zee", "sup", "hello zee", "good evening", "hi everyone"],
                        ["HeyZee", "Jammies", "scootsGIGAZEE", "ayezeeBYE", "scootsGREG", "Scoots", "pugPls",
                         "ayezeePls",
                         "TinfoilZeeRight", "ayezeeSCOOTS"]]],
            ["casinodaddy", [["yoo daddy", "hi", "hi daddy", "sup", "hello daddy", "good evening", "hi everyone"],
                             ["Kappa", "LUL", "PogChamp", "WutFace", "HeyGuys", "VoHiYo", "GlitchCat", "DxCat",
                              "OSFrog"]]],
            ["frankdimes", [["yoo frankie", "hi", "hi frankie", "sup", "hello frankie", "good evening", "hi everyone"],
                            ["dimeBye", "Hmm", "PogChamp", "LUL", "VoHiYo", "WutFace", "Kappa", "GlitchCat", "DxCat",
                             "OSFrog"]]],
            ["deuceace", [["yoo deuce", "hi", "hi deuce", "sup", "hello deuce", "good evening", "hi everyone"],
                          ["ShadyLulu", "twitchRaid", "MingLee", "LUL", "WutFace", "Kappa", "PogChamp", "DxCat",
                           "OSFrog",
                           "VoHiYo"]]],
            ["vondice", [["yoo dice", "hi", "hi dice", "sup", "hello dice", "good evening", "hi everyone"],
                         ["peepoSmash", "vonLEO", "LUL", "MingLee", "WutFace", "Kappa", "PogChamp", "DxCat",
                          "GlitchCat",
                          "VoHiYo"]]],
            ["sweezy", [["yoo sweezy", "cau", "cau sweezy", "jakjee", "ahoj sweezy", "dobrej vecir", "cau lidi"],
                        ["pepeLaugh", "sweezyOop", "KEKW", "redyPiskoty", "catJAM", "restt2", "OMEGALUL", "resttOk",
                         "resttM"]]],
            ["watchgamestv", [["yoo ibby", "hi", "hi ibby", "sup", "hello ibby", "good evening", "hi everyone"],
                              ["Kappa", "PogChamp", "WutFace", "dpgdkProdcess", "ayezeeGASM", "watchgChip", "SabaPing",
                               "ShadyLulu", "DxCat"]]],
            ["yassuo", [["yoo moe", "hi", "hi moe", "sup", "hello moe", "good evening", "hi everyone"],
                        ["Kappa", "PogChamp", "WutFace", "LUL", "VoHiYo", "DxCat", "ShadyLulu", "OSFrog", "peepoSmash",
                         "pepeLaugh", "MingLee"]]]
        ]
        
    # sends message to channel chat
    def send_privmsg(self, channel, message):
        self.send_command(f'PRIVMSG #{channel} :{message}')

    # send command to irc
    def send_command(self, command):
        try:
            self.irc.send((command + '\r\n').encode())
        except BrokenPipeError or ConnectionError or ConnectionResetError:
            self.irc.send((command + '\r\n').encode())

    # function which generate greeting and emoji
    def greeting(self, channel_name):
        emoji = randint(0, 1)   # var telling if we will get emoji or not

        for acc in self.channel_map:    # iterating channels in map

            if acc[0] == channel_name:  # if channel is found
                message_index = randint(1, len(self.channel_map[1][0])-1)   # generate index of greeting
                message = acc[1][0][message_index]  # save greeting into variable

                if emoji == 1:  # if emoji is going to be generated
                    emoji_index = randint(1, len(self.channel_map[1][1])-1)     # generate index of emoji
                    message += ' '  # add space between text and emoji
                    message += acc[1][1][emoji_index]   # generate and add emoji

                return message

        # if channel does not have any map, use these preset greetings
        backup = ['Hello there Kappa', 'Hi', 'Hey LUL', 'Wasup DxCat', 'hehey', 'hello', 'im Here pepeLaugh', 'such a nice day OSFrog', 'Hey there', 'sup guys SoonerLater']
        return backup[randint(1, len(backup)-1)]

    # connect to channel chat
    def connect(self):
        with open(self.cfg) as config_file:  # opens config file
            config = json.load(config_file)

            for channel in config['channels']:  # iterate all channels

                if channel_status(channel, config['api']['token'], config['api']['clientID']):
                    # checking if channel is live

                    with open(self.status_cfg, 'r+') as status_file:     # opens status config file and load it
                        status_loaded = json.load(status_file)

                        for status in status_loaded[self.username]:      # iterating statuses

                            if (status['channel'] == channel) and (not status['isConnected']):
                                # checking if acc is connected to channel chat
                                status['isConnected'] = True
                                # if is not connected, connect and write it into status config
                                status_file.seek(0)
                                json.dump(status_loaded, status_file, indent=4)
                                status_file.truncate()

                                self.send_command(f'JOIN #{channel}')   # JOINS channel chat
                                print(f'{self.username} joining to {channel}')

                                cooldown = randint(0, 5)
                                time.sleep(cooldown)
                                self.send_privmsg(channel, self.greeting(channel))
                                # TODO make random message every 5-20mins

    # disconnect from channel chat
    def disconnect(self):
        with open(self.cfg) as config_file:  # opens config file
            config = json.load(config_file)

            for channel in config['channels']:  # iterating channels in config file
                if not channel_status(channel, config['api']['token'], config['api']['clientID']):
                    # checking if channel is offline

                    with open(self.status_cfg, 'r+') as status_file:     # if is offline open status config file
                        status_loaded = json.load(status_file)

                        for status in status_loaded[self.username]:  # iterate statuses in status config

                            if (status['channel'] == channel) and (status['isConnected']):
                                # checking if acc is connected to channel chat
                                status['isConnected'] = False
                                # if yes, disconnect and write it into status config file
                                status_file.seek(0)
                                json.dump(status_loaded, status_file, indent=4)
                                status_file.truncate()

                                self.send_command(f'PART #{channel}')   # LEAVE channels chat
                                print(f'{self.username} leaving from {channel}...')

    # disconnect method which force acc to disconnect from channel neither its online or not
    # same as disconnect but does not check for offline status
    def force_disconnect(self):
        with open(self.cfg) as config_file:
            config = json.load(config_file)

            for channel in config['channels']:

                with open(self.status_cfg, 'r+') as status_file:
                    status_loaded = json.load(status_file)

                    for status in status_loaded[self.username]:

                        if (status['channel'] == channel) and (status['isConnected']):
                            status['isConnected'] = False
                            status_file.seek(0)
                            json.dump(status_loaded, status_file, indent=4)
                            status_file.truncate()

                            self.send_command(f'PART #{channel}')
                            print(f'{self.username} leaving from {channel}...')

    # closes socket
    def close_socket(self):
        print('Closing socket...')
        self.irc.close()
        print('Socket closed successfully.')

    # gets user from prefix (from twitch messages)
    def get_user_from_prefix(self, prefix):
        domain = prefix.split('!')[0]

        if domain.endswith('.tmi.twitch.tv'):
            return domain.replace('.tmi.twitch.tv', '')

        if 'tmi.twitch.tv' not in domain:
            return domain

    # parsing message
    def parse_message(self, received_msg):
        parts = received_msg.split(' ')

        prefix = None
        user = None
        channel = None
        text = None
        irc_command = None
        irc_args = None

        if parts[0].startswith(':'):
            prefix = parts[0][1:]
            user = self.get_user_from_prefix(prefix)
            parts = parts[1:]

        text_start = next(
            (idx for idx, part in enumerate(parts) if part.startswith(':')),
            None
        )

        if text_start is not None:
            text_parts = parts[text_start:]
            text_parts[0] = text_parts[0][1:]
            text = ' '.join(text_parts)
            parts = parts[:text_start]

        irc_command = parts[0]
        irc_args = parts[1:]

        hash_start = next(
            (idx for idx, part in enumerate(irc_args) if part.startswith('#')),
            None
        )

        if hash_start is not None:
            channel = irc_args[hash_start][1:]

        message = Message(
            prefix=prefix,
            user=user,
            channel=channel,
            text=text,
            irc_command=irc_command,
            irc_args=irc_args
        )

        return message

    # what does it do with message
    def handle_message(self, received_msg):
        if len(received_msg) == 0:
            return

        message = self.parse_message(received_msg)
        # print(f'> {message}')

        if message.irc_command == '001':
            print(f'Watcher {self.username} connected')

        if message.irc_command == 'PING':   # if twitch pings us we have to pong him
            self.send_command('PONG :tmi.twitch.tv')

        if (message.text is not None) and (message.channel is not None) and (message.text[0] not in '!._/-?'):

            for logger in self.loggers:

                if logger.channel == message.channel:
                    logger_load = logger.add_message(message.text)

                    if logger_load is not None:
                        self.send_privmsg(logger_load[0], logger_load[1])

    # main cycle, checking messages etc.
    def loop_for_messages(self):
        # while True:
        ready = select.select([self.irc], [], [], 2)

        if ready[0]:
            try:
                received_msgs = self.irc.recv(2048).decode()
            except ConnectionResetError or BrokenPipeError or ConnectionError:
                return

            for received_msg in received_msgs.split('\r\n'):
                self.handle_message(received_msg)

        self.disconnect()
        self.connect()
