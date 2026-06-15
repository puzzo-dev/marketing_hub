# -*- coding: utf-8 -*-
"""
Social Media Platform Adapter

Configuration-driven adapter that reads ALL settings from the 
Social Media Network doctype. No code needed for new platforms!

## Adding New Platforms:

Just create a Social Media Network record with:
- API endpoints (with {placeholders})
- Request field names
- Response field paths  
- Authentication type
- Platform limits

Done! Zero Python code required.

For platform-specific behavior, create a custom adapter:
- Extend BasePlatformAdapter
- Set custom_adapter_class in Social Media Network
"""

from marketing_hub.utils.social_adapters.base import BasePlatformAdapter
from marketing_hub.utils.social_adapters.generic import (
	AuthenticationError,
	GenericAdapter,
	PlatformAPIError,
	RateLimitError,
)
from marketing_hub.utils.social_adapters.linkedin import LinkedInAdapter
from marketing_hub.utils.social_adapters.meta import MetaAdapter
from marketing_hub.utils.social_adapters.twitter import TwitterAdapter

__all__ = [
	'BasePlatformAdapter',
	'GenericAdapter',
	'MetaAdapter',
	'LinkedInAdapter',
	'TwitterAdapter',
	'PlatformAPIError',
	'RateLimitError',
	'AuthenticationError',
]

