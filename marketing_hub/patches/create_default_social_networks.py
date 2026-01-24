"""
Create default Social Media Networks
"""

import frappe


def execute():
	"""Create default social media networks if they don't exist"""
	networks = [
		{
			"network_name": "Facebook",
			"network_code": "facebook",
			"is_active": 1,
			"network_type": "Social Media",
			"api_base_url": "https://graph.facebook.com/v18.0",
			"supports_scheduling": 1,
			"supports_media": 1,
			"post_types": "Text\nImage\nVideo\nCarousel\nStory\nReel\nLive",
			"max_text_length": 63206,
			"max_media_count": 10,
			"supported_formats": "jpg, png, gif, mp4, mov",
			"description": "Meta's Facebook platform for personal and business profiles"
		},
		{
			"network_name": "Instagram",
			"network_code": "instagram",
			"is_active": 1,
			"network_type": "Social Media",
			"api_base_url": "https://graph.instagram.com",
			"supports_scheduling": 1,
			"supports_media": 1,
			"post_types": "Image\nVideo\nCarousel\nStory\nReel",
			"max_text_length": 2200,
			"max_media_count": 10,
			"supported_formats": "jpg, png, mp4",
			"description": "Meta's Instagram platform for photo and video sharing"
		},
		{
			"network_name": "Twitter/X",
			"network_code": "twitter",
			"is_active": 1,
			"network_type": "Social Media",
			"api_base_url": "https://api.twitter.com/2",
			"supports_scheduling": 1,
			"supports_media": 1,
			"post_types": "Text\nImage\nVideo",
			"max_text_length": 280,
			"max_media_count": 4,
			"supported_formats": "jpg, png, gif, mp4",
			"description": "Twitter (now X) microblogging platform"
		},
		{
			"network_name": "LinkedIn",
			"network_code": "linkedin",
			"is_active": 1,
			"network_type": "Social Media",
			"api_base_url": "https://api.linkedin.com/v2",
			"supports_scheduling": 1,
			"supports_media": 1,
			"post_types": "Text\nImage\nVideo\nCarousel",
			"max_text_length": 3000,
			"max_media_count": 9,
			"supported_formats": "jpg, png, gif, mp4",
			"description": "Professional networking platform"
		},
		{
			"network_name": "TikTok",
			"network_code": "tiktok",
			"is_active": 1,
			"network_type": "Social Media",
			"api_base_url": "https://open-api.tiktok.com",
			"supports_scheduling": 1,
			"supports_media": 1,
			"post_types": "Video",
			"max_text_length": 2200,
			"max_media_count": 1,
			"supported_formats": "mp4, mov",
			"description": "Short-form video social media platform"
		},
		{
			"network_name": "YouTube",
			"network_code": "youtube",
			"is_active": 1,
			"network_type": "Social Media",
			"api_base_url": "https://www.googleapis.com/youtube/v3",
			"supports_scheduling": 1,
			"supports_media": 1,
			"post_types": "Video\nShorts\nLive",
			"max_text_length": 5000,
			"max_media_count": 1,
			"supported_formats": "mp4, mov, avi",
			"description": "Google's video sharing platform"
		},
		{
			"network_name": "Pinterest",
			"network_code": "pinterest",
			"is_active": 1,
			"network_type": "Social Media",
			"api_base_url": "https://api.pinterest.com/v5",
			"supports_scheduling": 1,
			"supports_media": 1,
			"post_types": "Image\nVideo",
			"max_text_length": 500,
			"max_media_count": 1,
			"supported_formats": "jpg, png, mp4",
			"description": "Visual discovery and bookmarking platform"
		},
		{
			"network_name": "Google Ads",
			"network_code": "google_ads",
			"is_active": 1,
			"network_type": "Advertising Platform",
			"api_base_url": "https://googleads.googleapis.com/v14",
			"supports_scheduling": 1,
			"supports_media": 1,
			"post_types": "Search\nDisplay\nVideo\nShopping",
			"max_text_length": 90,
			"supported_formats": "jpg, png, gif, mp4",
			"description": "Google's online advertising platform"
		},
		{
			"network_name": "Meta Ads",
			"network_code": "meta_ads",
			"is_active": 1,
			"network_type": "Advertising Platform",
			"api_base_url": "https://graph.facebook.com/v18.0",
			"supports_scheduling": 1,
			"supports_media": 1,
			"post_types": "Image\nVideo\nCarousel\nCollection",
			"max_text_length": 125,
			"max_media_count": 10,
			"supported_formats": "jpg, png, mp4",
			"description": "Meta's advertising platform for Facebook and Instagram"
		},
		{
			"network_name": "LinkedIn Ads",
			"network_code": "linkedin_ads",
			"is_active": 1,
			"network_type": "Advertising Platform",
			"api_base_url": "https://api.linkedin.com/v2",
			"supports_scheduling": 1,
			"supports_media": 1,
			"post_types": "Sponsored Content\nSponsored InMail\nText Ads",
			"max_text_length": 600,
			"supported_formats": "jpg, png, mp4",
			"description": "LinkedIn's advertising platform"
		}
	]
	
	for network_data in networks:
		if not frappe.db.exists("Social Media Network", network_data["network_name"]):
			try:
				network = frappe.get_doc({
					"doctype": "Social Media Network",
					**network_data
				})
				network.insert()
				frappe.db.commit()
				print(f"Created Social Media Network: {network_data['network_name']}")
			except Exception as e:
				frappe.log_error(f"Failed to create network {network_data['network_name']}: {str(e)}")
				print(f"Failed to create {network_data['network_name']}: {str(e)}")
		else:
			print(f"Social Media Network already exists: {network_data['network_name']}")
