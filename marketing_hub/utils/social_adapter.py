# -*- coding: utf-8 -*-
"""
Social Media Adapter

Generic entry point for publishing to social media platforms.
Uses adapter pattern for platform-specific implementations.
"""

import frappe
from frappe import _


def publish_to_platform(post):
	"""
	Generic entry point for publishing to any social platform.
	Uses adapter pattern for platform-specific logic.
	
	Args:
		post: Social Post document
	
	Returns:
		dict: Result with success status and post details
	"""
	if not post.platform:
		return {"success": False, "error": "No platform specified"}

	try:
		# Get network configuration
		network = frappe.get_doc("Social Media Network", post.platform)

		if not network.is_active:
			return {"success": False, "error": f"Platform {network.network_name} is disabled"}

		# Resolve network account for auth
		network_account_doc = None
		if post.network_account:
			network_account_doc = frappe.get_doc("Network Account", post.network_account)
		elif post.account:
			ad_account = frappe.get_doc("Ad Account", post.account)
			if ad_account.network_account:
				network_account_doc = frappe.get_doc("Network Account", ad_account.network_account)

		# Get the appropriate adapter
		adapter = get_platform_adapter(network, network_account_doc=network_account_doc)

		# Publish using adapter
		result = adapter.publish(post)
		
		# Update post document with result
		if result.get("success"):
			post.status = "Published"
			post.platform_post_id = result.get("platform_post_id")
			post.published_time = frappe.utils.now()
		else:
			post.status = "Failed"
			post.error_log = result.get("error")
		
		post.save()
		frappe.db.commit()
		
		return result
		
	except (frappe.ValidationError, frappe.DoesNotExistError) as e:
		frappe.log_error(f"Publish error: {str(e)}", "Social Adapter")
		return {"success": False, "error": str(e)}


def get_platform_adapter(network_doc, ad_account_doc=None, network_account_doc=None):
	"""
	Factory function to get the right adapter for a platform.

	If custom_adapter_class is specified in Social Media Network, use that.
	Otherwise, use the GenericAdapter which reads configuration from the doctype.

	Args:
		network_doc: Social Media Network document
		ad_account_doc: Optional Ad Account document
		network_account_doc: Optional Network Account document for auth

	Returns:
		BasePlatformAdapter: Platform-specific adapter instance
	"""
	from marketing_hub.utils.social_adapters.generic import GenericAdapter

	# Allowlist of permitted custom adapter module paths
	_ALLOWED_ADAPTER_MODULES = {
		"marketing_hub.utils.social_adapters",
		"marketing_hub.utils",
	}

	# Check if custom adapter class is specified
	if hasattr(network_doc, 'custom_adapter_class') and network_doc.custom_adapter_class:
		try:
			# Validate against allowlist before dynamic import
			module_path, class_name = network_doc.custom_adapter_class.rsplit('.', 1)
			if not any(module_path.startswith(allowed) for allowed in _ALLOWED_ADAPTER_MODULES):
				raise ImportError(
					_("Adapter module '{0}' is not in the allowed modules list.").format(module_path)
				)

			import importlib
			module = importlib.import_module(module_path)
			adapter_class = getattr(module, class_name)

			frappe.logger().info(f"Using custom adapter for {network_doc.network_name}: {network_doc.custom_adapter_class}")
			return adapter_class(network_doc, ad_account_doc, network_account_doc)

		except (ImportError, AttributeError, ModuleNotFoundError) as e:
			frappe.log_error(f"Failed to load custom adapter {network_doc.custom_adapter_class}: {str(e)}", "Adapter Factory")
			frappe.msgprint(_("Custom adapter failed, falling back to generic adapter: {0}").format(str(e)), alert=True)

	# Use GenericAdapter by default - reads all config from Social Media Network doctype
	frappe.logger().info(f"Using GenericAdapter for {network_doc.network_name}")
	return GenericAdapter(network_doc, ad_account_doc, network_account_doc)


def get_post_analytics(post):
	"""
	Fetch analytics for a published post.
	
	Args:
		post: Social Post document
	
	Returns:
		dict: Analytics metrics
	"""
	if not post.platform_post_id:
		return {"error": "Post not published yet"}
	
	try:
		network = frappe.get_doc("Social Media Network", post.platform)
		adapter = get_platform_adapter(network)
		
		analytics = adapter.get_post_analytics(post.platform_post_id)
		
		# Update post document with analytics
		if not analytics.get("error"):
			post.impressions = analytics.get("impressions", 0)
			post.reach = analytics.get("reach", 0)
			post.clicks = analytics.get("clicks", 0)
			post.likes = analytics.get("likes", 0)
			post.comments_count = analytics.get("comments", 0)
			post.shares = analytics.get("shares", 0)
			post.engagement_rate = analytics.get("engagement_rate", 0)
			post.save()
			frappe.db.commit()
		
		return analytics
		
	except (frappe.ValidationError, frappe.DoesNotExistError) as e:
		frappe.log_error(f"Get analytics error: {str(e)}", "Social Adapter")
		return {"error": str(e)}


def delete_post(post):
	"""
	Delete a post from the platform.
	
	Args:
		post: Social Post document
	
	Returns:
		dict: Deletion result
	"""
	if not post.platform_post_id:
		return {"error": "Post not published yet"}
	
	try:
		network = frappe.get_doc("Social Media Network", post.platform)
		adapter = get_platform_adapter(network)
		
		result = adapter.delete_post(post.platform_post_id)
		
		# Update post status
		if result.get("success"):
			post.status = "Deleted"
			post.save()
			frappe.db.commit()
		
		return result
		
	except (frappe.ValidationError, frappe.DoesNotExistError) as e:
		frappe.log_error(f"Delete post error: {str(e)}", "Social Adapter")
		return {"error": str(e)}


# ============ Whitelisted API Methods ============

@frappe.whitelist()
def publish_post(post_name):
	"""
	Whitelist method to publish a post from UI.
	
	Args:
		post_name: Name of Social Post document
	
	Returns:
		dict: Publication result
	"""
	post = frappe.get_doc("Social Post", post_name)
	return publish_to_platform(post)


@frappe.whitelist()
def fetch_post_analytics(post_name):
	"""
	Whitelist method to fetch analytics from UI.
	
	Args:
		post_name: Name of Social Post document
	
	Returns:
		dict: Analytics data
	"""
	post = frappe.get_doc("Social Post", post_name)
	return get_post_analytics(post)


@frappe.whitelist()
def delete_platform_post(post_name):
	"""
	Whitelist method to delete a post from UI.
	
	Args:
		post_name: Name of Social Post document
	
	Returns:
		dict: Deletion result
	"""
	post = frappe.get_doc("Social Post", post_name)
	return delete_post(post)
