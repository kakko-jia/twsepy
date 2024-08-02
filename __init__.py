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


from .core import daily_closing_prices, market_trading_info, daily_stock_ratios, margin_trading, FIP_trading_data
from .config import DEFAULT_HEADERS, BASE_URL
from .exceptions import CrawlerException, RequestFailedException
from .ticker import Ticker

__version__ = "0.1.0"
__author__ = "JJ"

import warnings
warnings.filterwarnings('default', category=DeprecationWarning, module='^twsepy')

__all__ = [
    'daily_closing_prices', 'market_trading_info', 'daily_stock_ratios', 'margin_trading', 'FIP_trading_data',
    'DEFAULT_HEADERS', 'BASE_URL', 'CrawlerException', 'RequestFailedException', 'Ticker'
]
