import pika


# class RabbitElement(Logger):
class RabbitElement:
    def __init__(self, host, port, user, pwd, queue, callback_method=None):
        self.rabbitmq_host = host
        self.rabbitmq_port = port
        self.rabbitmq_username = user
        self.rabbitmq_passwd = pwd

        self.queue = queue
        self.callback_method = callback_method
        self.chanel = None

        print("Rabbitmq host : " + self.rabbitmq_host)
        print("Rabbitmq port : " + str(self.rabbitmq_port))
        print("Listening on  : " + self.queue + "queue...")

        credentials = pika.PlainCredentials(self.rabbitmq_username, self.rabbitmq_passwd)

        self.parameters = pika.ConnectionParameters(
            host=self.rabbitmq_host,
            port=self.rabbitmq_port,
            virtual_host='/',
            credentials=credentials
        )

        self.connection = pika.SelectConnection(self.parameters, self.on_connected)

    def on_connected(self, connection):
        """Called when we are fully connected to RabbitMQ"""
        # Open a channel
        connection.channel(self.on_channel_open)

    def on_queue_declared(self, frame):
        """Called when RabbitMQ has told us our Queue has been declared, frame is the response from RabbitMQ"""
        if self.callback_method:
            self.channel.basic_consume(self.callback_method, queue=self.queue)

    def on_channel_open(self, new_channel):
        """Called when our channel has opened"""
        self.channel = new_channel
        self.channel.basic_qos(prefetch_count=1)

        self.channel.queue_declare(queue=self.queue, durable=True,
                                   exclusive=False, auto_delete=False,
                                   callback=self.on_queue_declared)
