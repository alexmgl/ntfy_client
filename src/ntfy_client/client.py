import requests
import secrets
import base64
import hashlib
import hmac
import uuid
import functools


class NtfyClient:
    def __init__(self, base_url="https://ntfy.sh", topic=None, auto_generate_topic=True):
        """
        Initialise Ntfy notifier with optional base URL and topic.

        Args:
            base_url (str, optional): Base URL for ntfy service. Defaults to public ntfy.sh.
            topic (str, optional): Specific topic for notifications. Defaults to None.
            auto_generate_topic (bool, optional): Whether to auto-generate a secure topic if none provided. Defaults to True.
        """
        self.base_url = base_url
        self.session = requests.Session()
        if topic:
            self.topic = topic
        elif auto_generate_topic:
            self.topic = self.generate_secure_topic(method='random', length=32, complexity=2)
        else:
            self.topic = None

    def generate_secure_topic(self, method='random', **kwargs):
        """
        Generate a secure topic using various methods.

        Args:
            method (str): Topic generation method.
            **kwargs: Additional parameters for topic generation.

        Returns:
            str: Generated secure topic.
        """
        if method == 'random':
            length = kwargs.get('length', 32)
            complexity = kwargs.get('complexity', 2)
            return self._generate_random_topic(length, complexity)
        elif method == 'hmac':
            secret_key = kwargs.get('secret_key')
            identifier = kwargs.get('identifier')
            if not secret_key or not identifier:
                raise ValueError("For HMAC method, secret_key and identifier must be provided.")
            return self._generate_hmac_topic(secret_key, identifier)
        elif method == 'uuid':
            return str(uuid.uuid4())
        elif method == 'compound':
            base_topic = kwargs.get('base_topic')
            return self._generate_compound_topic(base_topic)
        else:
            raise ValueError(f"Unsupported topic generation method: {method}")

    @staticmethod
    def _generate_random_topic(length=32, complexity=2):
        """
        Generate a cryptographically secure random topic.

        Args:
            length (int): Length of random bytes.
            complexity (int): Encoding complexity.

        Returns:
            str: Secure random topic.
        """
        if complexity == 1:
            return base64.b64encode(secrets.token_bytes(length)).decode('utf-8').rstrip('=')
        elif complexity == 2:
            return secrets.token_hex(length)
        else:
            return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode('utf-8').rstrip('=')

    @staticmethod
    def _generate_hmac_topic(secret_key, identifier, hash_algorithm=hashlib.sha256):
        """
        Generate a topic using HMAC.

        Args:
            secret_key (str): Secret key.
            identifier (str): Unique identifier.
            hash_algorithm (hashlib): Hash algorithm to use.

        Returns:
            str: HMAC-generated topic.
        """
        secret_key = secret_key.encode('utf-8')
        identifier = identifier.encode('utf-8')
        hmac_result = hmac.new(secret_key, identifier, hash_algorithm)
        return hmac_result.hexdigest()

    @staticmethod
    def _generate_compound_topic(base_topic=None):
        """
        Create a compound topic with multiple layers of randomness.

        Args:
            base_topic (str, optional): Optional base topic.

        Returns:
            str: Compound secure topic.
        """
        random_part1 = secrets.token_hex(8)
        random_part2 = base64.urlsafe_b64encode(secrets.token_bytes(12)).decode('utf-8').rstrip('=')
        if base_topic:
            base_hash = hashlib.sha256(base_topic.encode('utf-8')).hexdigest()[:16]
            return f"{base_hash}-{random_part1}-{random_part2}"
        return f"{random_part1}-{random_part2}"

    def send_notification(self, message, topic=None, **kwargs):
        """
        Send a notification to a specific topic.
        If topic is not provided, use the instance's topic.

        Args:
            message (str): Notification message.
            topic (str, optional): Notification topic. Defaults to None.
            **kwargs: Additional notification parameters.

        Returns:
            requests.Response: Response from the ntfy server.
        """
        topic = topic or self.topic
        if not topic:
            raise ValueError("No topic provided for sending notification.")
        url = f"{self.base_url}/{topic}"
        headers = {"Priority": str(kwargs.get('priority', 3))}
        if 'title' in kwargs:
            headers["Title"] = kwargs['title']
        if 'tags' in kwargs:
            headers["Tags"] = kwargs['tags']
        try:
            response = self.session.post(url, data=message.encode('utf-8'), headers=headers)
            response.raise_for_status()
            print(f"Notification sent successfully to topic: {topic}")
            return response
        except requests.RequestException as e:
            print(f"Failed to send notification: {e}")
            return None

    def subscribe(self, topic=None, **kwargs):
        """
        Subscribe to a topic (server-sent events).
        If topic is not provided, use the instance's topic.

        Args:
            topic (str, optional): Topic to subscribe to. Defaults to None.
            **kwargs: Additional subscription parameters.

        Yields:
            str: Received messages.
        """
        topic = topic or self.topic
        if not topic:
            raise ValueError("No topic provided for subscription.")
        subscribe_url = f"{self.base_url}/{topic}/json"
        try:
            with self.session.get(subscribe_url, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        yield line.decode('utf-8')
        except requests.RequestException as e:
            print(f"Subscription error: {e}")

    def ntfy(self, message, topic=None, **notify_kwargs):
        """
        A decorator that sends an ntfy notification after the decorated function is executed.
        If topic is not provided, use the instance's topic.

        Args:
            message (str): Notification message.
            topic (str, optional): Notification topic. Defaults to None.
            **notify_kwargs: Additional arguments for send_notification.

        Returns:
            Callable: Decorated function.
        """
        topic = topic or self.topic
        if not topic:
            raise ValueError("No topic provided for notification decorator.")

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                self.send_notification(message=message, topic=topic, **notify_kwargs)
                return result

            return wrapper

        return decorator


if __name__ == "__main__":

    # Example usage:
    client = NtfyClient(topic="example-topic")
    client.send_notification("Hello, world!")
