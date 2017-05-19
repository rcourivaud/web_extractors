from web_extractors.archi.rabbit_element import RabbitElement


class Publisher(RabbitElement):
    def __init__(self, host, port, user, pwd, name="SCRAPING"):
        super(Publisher, self).__init__(host=host, port=port, user=user, pwd=pwd)
        self.queue_to_publish = name.upper() + "_P"

        self.channel.queue_declare(queue=self.queue_to_publish, durable=True)
        #self.logger.debug("Initialisation Publisher : " + self.queue_to_publish)

    def send_request(self, message):
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_to_publish,
                                   body=message)
        #self.logger.debug(" [x] Sent : " + message)