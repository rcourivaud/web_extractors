class NotImplementedMethodError(Exception):
    def __init__(self, message, ):
        super(NotImplementedMethodError, self).__init__(message)