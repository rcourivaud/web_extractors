from errors import NotImplementedMethodError
from web_extractors.archi.rabbit_element import RabbitElement
import abc

class Receiver(RabbitElement):
    def __init__(self, name):
        super(Receiver, self).__init__(name + "_r")

        self.queue_to_listen = name.upper() + "_R"

        self.channel.queue_declare(queue=self.queue_to_listen, durable=True)
        self.channel.basic_consume(self.callback,
                                   queue=self.queue_to_listen,
                                   no_ack=True)
        print(' Result [*] Waiting for messages. To exit press CTRL+C')

    @abc.abstractmethod
    def callback(self,ch, method, properties, body):
        raise NotImplementedMethodError("You need to override the callback method")

    def launch(self):
        self.channel.start_consuming()

if __name__ == "__main__":
    receiver = Receiver("TEST")
    receiver.launch()
