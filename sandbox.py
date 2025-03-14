from src import NtfyClient

if __name__ == '__main__':

    # EXAMPLE ONE

    client = NtfyClient(topic="LHuqWJWA1jdeTol9MOuXXA")

    # Send notifications
    client.send_notification(
        title="Example 1.1",
        message="Validation",
        priority=5,
        tags="watermelon,boomerang"
    )

    @client.ntfy(message="Example 1.2", priority=5, title="Notification", tags="watermelon,boomerang")
    def demo_function(x, y):
        print(f"Adding {x} and {y}")
        return x + y

    # EXAMPLE TWO

    client = NtfyClient()

    topic = "LHuqWJWA1jdeTol9MOuXXA"

    # Send notifications
    client.send_notification(
        topic=topic,
        title="Example 2.1",
        message="Validation",
        priority=5,
        tags="warning"
    )

    @client.ntfy(topic=topic, message="Example 2.2", priority=5, title="Notification", tags="warning")
    def demo_function(x, y):
        print(f"Adding {x} and {y}")
        return x + y
