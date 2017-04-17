from webextractors.archi.rabbit_element import RabbitElement


class Receiver(RabbitElement):
    def __init__(self, name):
        super(Receiver, self).__init__(name + "_r")

        self.queue_to_listen = name.upper() + "_R"

        self.channel.queue_declare(queue=self.queue_to_listen, durable=True)
        self.channel.basic_consume(self.callback,
                                   queue=self.queue_to_listen,
                                   no_ack=True)
        print(' Result [*] Waiting for messages. To exit press CTRL+C')

    def callback(self,ch, method, properties, body):
        print(" Result [x] Received %r" % (body,))

    def launch(self):
        self.channel.start_consuming()

if __name__ == "__main__":
    receiver = Receiver("TEST")
    receiver.launch()
