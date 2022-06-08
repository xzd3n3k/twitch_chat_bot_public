class ChatLog:
    # constructor
    def __init__(self, channel):
        self.channel = channel  # channel name
        self.log = []   # place where channel messages goes
        self.statistic = {}     # storing count of repeated messages
        self.erase = False  # variable telling program if we need to erase chat log

    # function to add message to log - includes log analysis
    def add_message(self, message):
        self.log.append(message)

        # checking if we need to erase chat log or not
        if self.erase:
            self.erase = False      # sets var back to default
            self.statistic = {}     # resets statistics
            self.log = []       # resets log

        scp_log = [x.lower() for x in self.log]     # making copy of log but all letters are low

        if message.lower() in scp_log:      # checking if message (low) is in log or not
            scp_keys = [x.lower() for x in self.statistic]  # making copy of keys but all letter are low

            if message.lower() in scp_keys:     # checking if message is in stats or not

                for key in self.statistic:      # iterating keys in stats

                    if key.lower() == message.lower():      # if key is same as message
                        self.statistic[key] += 1    # add count to stats

            else:
                self.statistic[message] = 1     # else make message key and set count to 1

        if len(self.statistic) > 1:     # if something is in stats
            msg_to_send = max(self.statistic, key=self.statistic.get)   # find message with the highest count

            if self.statistic[msg_to_send] > 10:    # if highest count is bigger than 10
                self.erase = True   # make program erase log

                return self.channel, msg_to_send    # and return channel + message which we want to send

        if len(self.log) > 100:     # if log has more than 100 messages
            self.log.pop(0)  # remove first message from log
