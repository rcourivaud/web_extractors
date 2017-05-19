import json

import pika

from web_extractors.tools.logger import Logger


# class RabbitElement(Logger):
class RabbitElement:
    def __init__(self, host, port, user, pwd):

        self.rabbitmq_host = host
        self.rabbitmq_port = port
        self.rabbitmq_username = user
        self.rabbitmq_passwd = pwd

        print("Rabbitmq host : " + self.rabbitmq_host)
        print("Rabbitmq port : " + str(self.rabbitmq_port))

        credentials = pika.PlainCredentials(self.rabbitmq_username, self.rabbitmq_passwd)

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                virtual_host='/',
                credentials=credentials
            ))
        self.channel = self.connection.channel()

        # super().__init__(name=name)
        # rabbitmq_host = conf['databases']['rabbitmq']['host']
        # rabbitmq_port = conf['databases']['rabbitmq']['port']
        # rabbitmq_username = conf['databases']['rabbitmq']['username']
        # rabbitmq_passwd = conf['databases']['rabbitmq']['passwd']

