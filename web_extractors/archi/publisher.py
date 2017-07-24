from web_extractors.archi.rabbit_element import RabbitElement


class Publisher(RabbitElement):
    def __init__(self, host, port, user, pwd, name="SCRAPING"):
        self.queue_to_publish = name.upper() + "_P"
        super(Publisher, self).__init__(host=host, port=port,
                                        user=user, pwd=pwd,
                                        queue=self.queue_to_publish)



    def send_request(self, message):
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_to_publish,
                                   body=message)
