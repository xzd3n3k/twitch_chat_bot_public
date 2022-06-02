# imports
import requests
import json
from requests.structures import CaseInsensitiveDict


# checking if channel is online or not, depends on that returns True or False
def channel_status(channel, token, client_id):
    headers = CaseInsensitiveDict()     # setting all necessary headers
    headers['Authorization'] = f"Bearer {token}"
    headers["Client-Id"] = client_id

    # making get request for channel info
    channel_info_request = requests.get(f"https://api.twitch.tv/helix/search/channels?query={channel}",
                                        headers=headers)

    # if successful loads info and return if its live or not
    if channel_info_request.status_code == 200:
        channel_info = json.loads(channel_info_request.text)

        for acc in channel_info['data']:

            if acc['display_name'].lower() == channel.lower():
                return acc['is_live']

    return channel_status(channel, token, client_id)
