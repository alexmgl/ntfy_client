# NTFY Client

A Python client to send notifications to the NTFY API.

![Language](https://img.shields.io/badge/language-Python-blue)
![Version](https://img.shields.io/badge/version-v1.0.1-brightgreen)
![Python Version](https://img.shields.io/badge/python-%3E%3D3.6-informational)

## Overview

The NTFY Client provides an easy-to-use interface for interacting with the NTFY API. It features:
- **Centralised Topic Management**: Set a topic during initialisation or auto-generate one securely.
- **Flexible Notification Methods**:Send notifications, subscribe to topics, or use a decorator to automatically notify after function execution.

## Installation

This project requires Python 3.7 or later.

## Installation

Install directly from GitHub using pip:

```bash
pip install git+https://github.com/alexmgl/ntfy_client.git
```

Or clone the repository and install locally:

```bash
git clone https://github.com/alexmgl/ntfy_client.git
cd ntfy_client
pip install .
```

### Install Dependencies:

If you're using pip:

```bash
pip install -r requirements.txt
```

Or if you use Poetry:

```bash
poetry install
```

### Usage

#### Basic Usage

You can create an instance of the client by specifying a topic. If you do not provide a topic, a secure one will be auto-generated (if enabled):
```python
from ntfy_client import NtfyClient

# Create a client with a specified topic
client = NtfyClient(topic="example-topic")

# Send a notification to the topic
client.send_notification("Hello, world!")
```

#### Auto-generating a Topic

If you prefer to let the client generate a secure topic automatically, simply omit the topic argument:
```python
from ntfy_client import NtfyClient

# Create a client with an auto-generated secure topic
client = NtfyClient()

# The client will use the generated topic for notifications
client.send_notification("Hello from an auto-generated topic!")
```

#### Subscribing to a Topic
The client supports subscribing to a topic using server-sent events. This example demonstrates how to receive messages:
```python
from ntfy_client import NtfyClient

client = NtfyClient(topic="example-topic")

# Subscribe to the topic and print received messages
for message in client.subscribe():
    print("Received message:", message)
```

#### Using the Notification Decorator
You can use the ntfy decorator to automatically send a notification after a function is executed:
```python
from ntfy_client import NtfyClient

client = NtfyClient(topic="example-topic")

@client.ntfy("Function execution completed!")
def my_function():
    print("Function is running...")

# When my_function is called, it will automatically send a notification.
my_function()
```

### License
This project is licensed under the MIT License.