import os
import random


class UserAgentManager:
    def __init__(self, agent_file=os.path.dirname(os.path.realpath(__file__)) + '/../UserAgents.txt'):
        self.agent_file = agent_file
        self.useragents = self.load_user_agents(self.agent_file)

    def load_user_agents(self, useragentsfile):
        """
        useragentfile : string
            path to text file of user agents, one per line
        """
        useragents = []
        with open(useragentsfile, 'rb') as uaf:
            for ua in uaf.readlines():
                if ua:
                    useragents.append(str(ua.strip()[1:-1 - 1]))
        return useragents

    def get_random_user_agent(self):
        """
        useragents : string array of different user agents
        :return random agent:
        """
        user_agent = random.choice(self.useragents)
        return user_agent

    def get_len_user_agent(self):
        return len(self.useragents)


if __name__ == '__main__':
    ua = UserAgentManager()
    print("Number of User Agent headers: " + str(ua.get_len_user_agent()))
    print("User-Agent: " + ua.get_random_user_agent())