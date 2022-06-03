# imports
import socket
import select
from collections import namedtuple
import json
from channelStatus import channel_status

# Message declaration
Message = namedtuple(
    'Message',
    'prefix user channel irc_command irc_args text'
)

# configs
status_cfg = 'status_config.json'
cfg = 'test_config.json'


class Twitch:
    # constructor
    def __init__(self, oauth, username):
        self.irc = None
        self.irc_server = 'irc.twitch.tv'
        self.irc_port = 6667
        self.oauth = oauth
        self.username = username    # TODO make multiaccount - load users from config

        # connect to socket and authorize
        self.irc = socket.socket()
        self.irc.connect((self.irc_server, self.irc_port))
        self.send_command(f'PASS {self.oauth}')
        self.send_command(f'NICK {self.username}')

    # sends message to channel chat
    def send_privmsg(self, channel, message):
        self.send_command(f'PRIVMSG #{channel} :{message}')

    # send command to irc
    def send_command(self, command):
        self.irc.send((command + '\r\n').encode())

    # connect to channel chat
    def connect(self):
        with open(cfg) as config_file:  # opens config file
            config = json.load(config_file)

            for channel in config['channels']:  # iterate all channels

                if channel_status(channel, config['api']['token'], config['api']['clientID']):
                    # checking if channel is live

                    with open(status_cfg, 'r+') as status_file:     # opens status config file and load it
                        status_loaded = json.load(status_file)

                        for status in status_loaded['status']:      # iterating statuses

                            if (status['channel'] == channel) and (not status['isConnected']):
                                # checking if acc is connected to channel chat
                                status['isConnected'] = True
                                # if is not connected, connect and write it into status config
                                status_file.seek(0)
                                json.dump(status_loaded, status_file, indent=4)
                                status_file.truncate()

                                self.send_command(f'JOIN #{channel}')   # JOINS channel chat
                                print(f'{self.username} joining to {channel}')
                                self.send_privmsg(channel, 'Hey there!')
                                # TODO make random message when join + random message every 5-20mins

        #self.loop_for_messages()    # 'MAIN' cycle for checking messages etc.

    # disconnect from channel chat
    def disconnect(self):
        with open(cfg) as config_file:  # opens config file
            config = json.load(config_file)

            for channel in config['channels']:  # iterating channels in config file
                if not channel_status(channel, config['api']['token'], config['api']['clientID']):
                    # checking if channel is offline

                    with open(status_cfg, 'r+') as status_file:     # if is offline open status config file
                        status_loaded = json.load(status_file)

                        for status in status_loaded['status']:  # iterate statuses in status config

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
        with open(cfg) as config_file:
            config = json.load(config_file)

            for channel in config['channels']:

                with open(status_cfg, 'r+') as status_file:
                    status_loaded = json.load(status_file)

                    for status in status_loaded['status']:

                        if (status['channel'] == channel) and (status['isConnected']):
                            status['isConnected'] = False
                            status_file.seek(0)
                            json.dump(status_loaded, status_file, indent=4)
                            status_file.truncate()

                            self.send_command(f'PART #{channel}')
                            print(f'{self.username} leaving from {channel}...')

    # closes socket
    def close_socket(self):
        self.irc.close()

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
        print(f'> {message}')

        if message.irc_command == 'PING':   # if twitch pings us we have to pong him
            self.send_command('PONG :tmi.twitch.tv')

        if (message.text is not None) and ('hi' in message.text):
            self.send_privmsg(message.channel, 'hey')

    # main cycle, checking messages etc.
    def loop_for_messages(self):

        while True:
            ready = select.select([self.irc], [], [], 3)

            if ready[0]:
                received_msgs = self.irc.recv(2048).decode()

                for received_msg in received_msgs.split('\r\n'):
                    self.handle_message(received_msg)

            self.disconnect()
            self.connect()


def main():
    acc = Twitch('oauth:', '')
    # testing
    # acc.connect()
    # acc.loop_for_messages()
    acc.force_disconnect()
    acc.close_socket()


if __name__ == '__main__':
    main()
