from src import NtfyClient

if __name__ == '__main__':

    notifier = NtfyClient()

    topic = "LHuqWJWA1jdeTol9MOuXXA"

    # Generate different types of secure topics
    random_topic = notifier.generate_secure_topic(method='random', length=16, complexity=3)

    hmac_topic = notifier.generate_secure_topic(
        method='hmac',
        secret_key='your_secret_key',
        identifier='user_device_id'
    )

    # Send notifications
    notifier.send_notification(
        topic=topic,
        title="Scrape Completed",
        message="Validation",
        priority=5,
        tags="warning"
    )
