import requests
import secrets
import base64
import hashlib
import hmac
import uuid


class NtfyClient:

    def __init__(self, base_url="https://ntfy.sh"):
        """
        Initialise Ntfy notifier with optional base URL

        Args:
            base_url (str, optional): Base URL for ntfy service. Defaults to public ntfy.sh
        """
        self.base_url = base_url
        self.session = requests.Session()

    def generate_secure_topic(self, method='random', **kwargs):
        """
        Generate a secure topic using various methods

        Args:
            method (str): Topic generation method
            **kwargs: Additional parameters for topic generation

        Returns:
            str: Generated secure topic
        """
        if method == 'random':
            length = kwargs.get('length', 32)
            complexity = kwargs.get('complexity', 2)
            return self._generate_random_topic(length, complexity)

        elif method == 'hmac':
            secret_key = kwargs.get('secret_key')
            identifier = kwargs.get('identifier')
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
        Generate a cryptographically secure random topic

        Args:
            length (int): Length of random bytes
            complexity (int): Encoding complexity

        Returns:
            str: Secure random topic
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
        Generate a topic using HMAC

        Args:
            secret_key (str): Secret key
            identifier (str): Unique identifier
            hash_algorithm (hashlib): Hash algorithm to use

        Returns:
            str: HMAC-generated topic
        """
        secret_key = secret_key.encode('utf-8')
        identifier = identifier.encode('utf-8')

        hmac_result = hmac.new(secret_key, identifier, hash_algorithm)
        return hmac_result.hexdigest()

    @staticmethod
    def _generate_compound_topic(base_topic=None):
        """
        Create a compound topic with multiple layers of randomness

        Args:
            base_topic (str, optional): Optional base topic

        Returns:
            str: Compound secure topic
        """
        random_part1 = secrets.token_hex(8)
        random_part2 = base64.urlsafe_b64encode(secrets.token_bytes(12)).decode('utf-8').rstrip('=')

        if base_topic:
            base_hash = hashlib.sha256(base_topic.encode('utf-8')).hexdigest()[:16]
            return f"{base_hash}-{random_part1}-{random_part2}"

        return f"{random_part1}-{random_part2}"

    def send_notification(self, topic, message, **kwargs):
        """
        Send a notification to a specific topic

        Args:
            topic (str): Notification topic
            message (str): Notification message
            **kwargs: Additional notification parameters

        Returns:
            requests.Response: Response from the ntfy server
        """
        # Prepare notification URL
        url = f"{self.base_url}/{topic}"

        # Default and custom headers
        headers = {
            "Priority": str(kwargs.get('priority', 3))
        }

        # Optional title
        if 'title' in kwargs:
            headers["Title"] = kwargs['title']

        # Optional tags
        if 'tags' in kwargs:
            headers["Tags"] = kwargs['tags']

        try:
            # Send notification
            response = self.session.post(
                url,
                data=message.encode('utf-8'),
                headers=headers
            )

            # Raise an exception for bad responses
            response.raise_for_status()

            print(f"Notification sent successfully to topic: {topic}")
            return response

        except requests.RequestException as e:
            print(f"Failed to send notification: {e}")
            return None

    def subscribe(self, topic, **kwargs):
        """
        Subscribe to a topic (server-sent events)

        Args:
            topic (str): Topic to subscribe to
            **kwargs: Additional subscription parameters

        Yields:
            str: Received messages
        """
        subscribe_url = f"{self.base_url}/{topic}/json"

        try:
            with self.session.get(subscribe_url, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        yield line.decode('utf-8')

        except requests.RequestException as e:
            print(f"Subscription error: {e}")


if __name__ == "__main__":
    pass
