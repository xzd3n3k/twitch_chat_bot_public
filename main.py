from bot import Twitch


def main():
    acc = Twitch('oauth:', '')
    acc.connect()
    acc.loop_for_messages()
    # acc.force_disconnect()
    # acc.close_socket()


if __name__ == '__main__':
    main()
