import json

import requests_cache

from webextractors.archi.rabbit_element import RabbitElement


class Scraper(RabbitElement):
    def __init__(self, host, port, user, pwd, name="SCRAPING", all_scrapers=None, cache=None):
        if all_scrapers:
            self.all_scrappers = all_scrapers
            super().__init__(host=host, port=port, user=user, pwd=pwd)

            self.reply_to = name.upper() + "_R"
            self.queue_listener = name.upper() + "_P"

            self.initialize_listener()
            self.initialize_replier()

            if cache:
                requests_cache.install_cache(cache_name=cache)
        else:
            print("You need to specify scrapers")

    def extract(self, message):
        print(message)
        body = json.loads(message.decode("utf-8"))
        params = body.get("params")
        url = body.get("url")
        which = body.get("which")
        print(body)

        # Choose the right scraper to call
        return self.all_scrappers[which].extract_url(url=url, params=params)

    def initialize_listener(self):
        self.channel.queue_declare(queue=self.queue_listener, durable=True)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback_on_receive,
                                   queue=self.queue_listener)

    def launch(self):
        print(' [*] Waiting for messages. To exit press CTRL+C')
        # self.logger.debug(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def callback_on_receive(self, ch, method, properties, body):
        print("Receive Message")
        result = self.extract(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        self.reply_to_queue(result)

    def initialize_replier(self):
        self.channel.queue_declare(queue=self.reply_to, durable=True)

    def reply_to_queue(self, body):
        self.channel.basic_publish(exchange='',
                                   routing_key=self.reply_to,
                                   body=json.dumps(body))



if __name__ == '__main__':
    sc = Scraper("Scraper")
    sc.launch()