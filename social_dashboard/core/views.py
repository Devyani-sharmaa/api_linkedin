import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import JsonResponse

def linkedin_login(request):
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&client_id={settings.LINKEDIN_CLIENT_ID}"
        f"&redirect_uri={settings.LINKEDIN_REDIRECT_URI}"
        "&scope=r_liteprofile r_emailaddress w_member_social"
    )
    return redirect(auth_url)

def linkedin_callback(request):
    code = request.GET.get("code")
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "client_secret": settings.LINKEDIN_CLIENT_SECRET,
    }

    response = requests.post(token_url, data=data)
    token_data = response.json()
    access_token = token_data.get("access_token")

    request.session['linkedin_access_token'] = access_token
    return JsonResponse({"access_token": access_token})

def fetch_linkedin_profile(request):
    access_token = request.session.get("linkedin_access_token")
    if not access_token:
        return JsonResponse({"error": "Not authenticated with LinkedIn"}, status=401)

    headers = {"Authorization": f"Bearer {access_token}"}
    profile_url = "https://api.linkedin.com/v2/me"

    response = requests.get(profile_url, headers=headers)
    return JsonResponse(response.json())

def post_on_linkedin(request):
    access_token = request.session.get("linkedin_access_token")
    if not access_token:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    # Fetch LinkedIn URN
    me_response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
    urn = me_response.json().get("id")
    author = f"urn:li:person:{urn}"

    post_data = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "Hello from Django + LinkedIn API!"
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    post_url = "https://api.linkedin.com/v2/ugcPosts"
    post_response = requests.post(post_url, headers=headers, json=post_data)
    return JsonResponse(post_response.json())
