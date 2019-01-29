class HttpLocust:
    """Mocks out the HttpLocust object
    """
    task_set = None

    def __init__(self, client):
        self.client = client

    def run(self):
        task_set_instance = self.task_set(self)
        task_set_instance.start()
