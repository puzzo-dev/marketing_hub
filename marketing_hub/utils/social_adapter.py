# -*- coding: utf-8 -*-
import frappe
from frappe import _
from marketing_hub.utils.oauth_integration import get_platform_credentials, make_api_request

def publish_to_platform(post):
    """
    Publish content to the specified social media platform.
    Dispatches to specific handlers based on platform name.
    """
    if not post.platform:
        return {"success": False, "error": "No platform specified"}

    # Fetch the Social Media Network document configuration
    try:
        network = frappe.get_doc("Social Media Network", post.platform)
    except frappe.DoesNotExistError:
        return {"success": False, "error": f"Social Media Network '{post.platform}' not found"}

    if not network.is_active:
        return {"success": False, "error": f"Platform {network.network_name} is disabled in Settings"}

    # Map platform names to handlers
    handlers = {
        "Facebook": _publish_to_facebook,
        "LinkedIn": _publish_to_linkedin,
        "Twitter/X": _publish_to_twitter,
        "Instagram": _publish_to_instagram,
        "TikTok": _publish_to_tiktok
    }
    
    handler = handlers.get(network.network_name) # Use the verified name from the doc
    
    if not handler:
        return {"success": False, "error": f"No handler implemented for {network.network_name}"}
        
    return handler(post, network) # Pass network config to handler

def _publish_to_facebook(post, network):
    """Publish to Facebook Graph API"""
    try:
        # 1. Get Credentials (Real Check)
        creds = get_platform_credentials("Facebook", post.company)
        if not creds:
             return {"success": False, "error": "No OAuth Credentials found for Facebook. Please configure Social Login Key or Ad Account."}

        # 2. Construct Payload
        payload = {
            "message": post.content
        }
        if post.link_url:
            payload["link"] = post.link_url
            
        # 3. Make Real API Request (will fail if creds are invalid/expired)
        # Assuming 'me/feed' or similar endpoint. User said completion logic later, 
        # but connection logic must be real.
        # calls make_api_request which uses requests.post with Bearer token
        
        response = make_api_request(
            platform="Facebook",
            endpoint="me/feed", 
            method="POST",
            data=payload,
            company=post.company
        )
        
        return {
            "success": True,
            "id": response.get("id"),
            "message": "Published successfully to Facebook"
        }
        
    except Exception as e:
        frappe.log_error(f"Facebook Publish Error: {str(e)}", "Social Adapter")
        return {"success": False, "error": str(e)}

def _publish_to_linkedin(post, network):
    """Publish to LinkedIn API"""
    try:
        creds = get_platform_credentials("LinkedIn", post.company)
        if not creds:
             return {"success": False, "error": "No OAuth Credentials found for LinkedIn."}

        # LinkedIn requires complex URN structure, but we implement the real call structure
        payload = {
            "author": f"urn:li:person:{creds.get('account_id', 'unknown')}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post.content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = make_api_request(
            platform="LinkedIn",
            endpoint="ugcPosts",
            method="POST", 
            data=payload,
            company=post.company
        )
        
        return {"success": True, "id": response.get("id"), "message": "Published to LinkedIn"}
        
    except Exception as e:
        frappe.log_error(f"LinkedIn Publish Error: {str(e)}", "Social Adapter")
        return {"success": False, "error": str(e)}

def _publish_to_twitter(post, network):
    """Publish to Twitter/X API (V2)"""
    try:
        creds = get_platform_credentials("Twitter/X", post.company)
        if not creds:
             return {"success": False, "error": "No OAuth Credentials found for Twitter."}

        payload = {"text": post.content}
        
        response = make_api_request(
            platform="Twitter/X",
            endpoint="tweets",
            method="POST",
            data=payload,
            company=post.company
        )
        
        return {"success": True, "id": response.get("data", {}).get("id"), "message": "Tweeted successfully"}

    except Exception as e:
         frappe.log_error(f"Twitter Publish Error: {str(e)}", "Social Adapter")
         return {"success": False, "error": str(e)}

def _publish_to_instagram(post, network):
    """Publish to Instagram Graph API"""
    try:
        creds = get_platform_credentials("Instagram", post.company)
        if not creds:
             return {"success": False, "error": "No OAuth Credentials found for Instagram."}

        # Instagram publishing is multi-step (Container -> Publish)
        # We start with step 1
        payload = {
            "caption": post.content,
            "image_url": post.image or "" # Required for IG
        }
        
        if not payload["image_url"]:
             return {"success": False, "error": "Image is required for Instagram posts"}

        creation_response = make_api_request(
            platform="Instagram",
            endpoint="media",
            method="POST",
            data=payload,
            company=post.company
        )
        
        # Step 2: Publish Container
        publish_response = make_api_request(
            platform="Instagram", 
            endpoint="media_publish",
            method="POST",
            data={"creation_id": creation_response.get("id")},
            company=post.company
        )
        
        return {"success": True, "id": publish_response.get("id"), "message": "Published to Instagram"}
        
    except Exception as e:
        frappe.log_error(f"Instagram Publish Error: {str(e)}", "Social Adapter")
        return {"success": False, "error": str(e)}

def _publish_to_tiktok(post, network):
    """Publish to TikTok API"""
    # TikTok API is purely video based and complex upload flow
    # For now, we enforce credential check logic
    try:
        creds = get_platform_credentials("TikTok", post.company)
        if not creds:
             return {"success": False, "error": "No OAuth Credentials found for TikTok."}
             
        # Placeholder for complex upload flow - but NOT simulated success
        return {"success": False, "error": "TikTok direct publishing not yet fully implemented (requires video upload flow)"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
