import json
from bot import Twitch


def main():
    accounts = []

    with open('config.json', 'r') as config:
        loaded_cfg = json.load(config)
        for acc in loaded_cfg['accounts']:
            accounts.append(Twitch(acc['token'], acc['username']))

    for account in accounts:
        account.connect()

    try:
        while True:
            for bot in accounts:
                bot.loop_for_messages()

    except KeyboardInterrupt:
        for bot in accounts:
            bot.force_disconnect()
            bot.close_socket()
# TODO make method to generate and edit status_config


if __name__ == '__main__':
    main()
