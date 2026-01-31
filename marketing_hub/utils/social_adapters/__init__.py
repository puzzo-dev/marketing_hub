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
"""

from marketing_hub.utils.social_adapters.generic import (
	GenericAdapter,
	PlatformAPIError,
	RateLimitError,
	AuthenticationError
)

__all__ = [
	'GenericAdapter',
	'PlatformAPIError',
	'RateLimitError',
	'AuthenticationError',
]
