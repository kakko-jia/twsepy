# Copyright 2024 JayC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Your Python code starts here


import re
import sys
import time
import logging
import requests
import threading


class RateLimiter:
    """
    Implement rate limiting using threading lock and timestamp.
    """

    def __init__(self, rate_limit = 1, period = 1, enabled = True):
        """
        Initialize RateLimiter instance.

        :param rate_limit: Maximum number of requests allowed in the specified period.
        :param period: Time period in seconds.
        """
        self.rate_limit = rate_limit
        self.period = period
        self.enabled = enabled
        self.lock = threading.Lock()
        self.last_request_time = 0

    def limit(self):
        """
        Check the time elapsed since the last request, and if it is less than the rate limit,
        wait for the remaining time.
        """
        if not self.enabled:
            return

        with self.lock:  # Ensure thread safety in a multithreaded environment
            now = time.time()
            elapsed = now - self.last_request_time
            if elapsed < self.period / self.rate_limit:
                time.sleep(self.period / self.rate_limit - elapsed)
            self.last_request_time = time.time()

    def set_rate_limit(self, new_rate_limit):
        """
        Update the rate limit.

        :param new_rate_limit: New maximum number of requests allowed in the specified period.
        """
        with self.lock:
            self.rate_limit = new_rate_limit

    def set_period(self, new_period):
        """
        Update the period.

        :param new_period: New time period in seconds.
        """
        with self.lock:
            self.period = new_period

    def enable(self):
        self.enabled(True)

    def disable(self):
        self.enabled(False)


# Global default rate limiter
default_rate_limiter = RateLimiter(rate_limit=5, period=5, enabled = False)

def limited_request(url, headers=None, params=None, proxy=None, rate_limiter=default_rate_limiter):
    """
    Send a rate-limited HTTP GET request and log the request details.

    :param url: The requested URL.
    :param headers: The request headers.
    :param params: The request parameters.
    :param proxy: Proxy settings. Can be a string or a dictionary with 'https' key.
    :return: The response object.
    """
    rate_limiter.limit()  # Apply rate limiting

    if proxy and isinstance(proxy, dict) and "https" in proxy:
        proxy = {"https": proxy["https"]}
    elif proxy and isinstance(proxy, str):
        proxy = {"https": proxy}

    response = requests.get(url, headers=headers, params=params, proxies=proxy)
    log_request(url, params, response)
    return response


def log_request(url, params, response):
    """
    Log each HTTP request including the requested URL, parameters, and response status code.

    :param url: The requested URL.
    :param params: The request parameters.
    :param response: The response object.
    """
    logging.info(f"Requested URL: {url}")
    logging.info(f"Parameters: {params}")
    logging.info(f"Response Status Code: {response.status_code}")


def simple_progress_bar(current, total, ticker_name, bar_length=40):
    """
    Display a progress bar.

    :param current: Current progress.
    :param total: Total steps.
    :param bar_length: Length of the progress bar.
    :param data_name: Name of the data being downloaded.
    """
    progress = current / total
    block = int(round(bar_length * progress))
    progress_bar = "=" * block + "-" * (bar_length - block)
    sys.stdout.write(f"\rProgress - {ticker_name}: [{progress_bar}] {current}/{total} ({progress:.2%})")
    sys.stdout.flush()


def remove_html_tags(text):
    """
    Remove HTML tags from a string.

    :param text: The input string with HTML tags.
    :return: A string without HTML tags.
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


"""
Future Development Notes:

1. Implement a thread pool to manage and allocate threads for handling a large number of concurrent requests.
2. Extend the RateLimiter class to support more rate limiting strategies, such as the token bucket algorithm.
3. Add exception handling to manage various exceptions that may occur during network requests.
4. Provide configurable logging levels and formats to suit different needs.

Future developers can expand functionality based on these notes.
"""
