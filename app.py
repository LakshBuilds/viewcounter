import os
import re
import textwrap
import requests
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st
from apify_client import ApifyClient
# Handle ApifyApiError import for different apify-client versions
try:
    from apify_client._errors import ApifyApiError
except ImportError:
    try:
        from apify_client.errors import ApifyApiError
    except ImportError:
        # Fallback: use Exception if ApifyApiError is not available
        ApifyApiError = Exception
from supabase import create_client, Client
from dotenv import load_dotenv

# Try to use experimental session state persistence
try:
    from streamlit import session_state as ss
    # Enable session state persistence
    if hasattr(st, 'experimental_user'):
        pass  # Future: use experimental features if available
except ImportError:
    pass

# Load environment variables from .env file
load_dotenv()

ACTOR_ID = "xMc5Ga1oCONPmWJIa"
DEFAULT_RESULTS_LIMIT = 5
TABLE_FIELDS = [
    ("Owner", "ownerUsername"),
    ("Added By", "created_by_name"),
    ("Caption preview", "caption"),
    ("Likes", "likesCount"),
    ("Comments", "commentsCount"),
    ("Views", "videoPlayCount"),
    ("Payout", "payout"),
    ("Location", "locationName"),
    ("Published", "timestamp"),
    ("Permalink", "url"),
]

CUSTOM_CSS = """
<style>
    :root {
        --bg-primary: #0a0a0a;
        --bg-secondary: #0f0f0f;
        --bg-card: #1a1a1a;
        --border: rgba(255, 255, 255, 0.1);
        --text-primary: #ffffff;
        --text-secondary: #999999;
        --accent-pink: #ec4899;
        --accent-purple: #8b5cf6;
        --accent-orange: #f97316;
    }
    
    .stApp {
        background: var(--bg-primary);
        color: var(--text-primary);
    }
    
    /* Hide Streamlit default header and reduce top spacing */
    .stApp > header {
        display: none;
    }
    
    .stApp {
        margin-top: -80px;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    .main-header {
        background: var(--bg-secondary);
        border-bottom: 1px solid var(--border);
        padding: 1rem 2rem;
        margin: 0;
        margin-bottom: 1.5rem;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .metric-trend {
        font-size: 0.875rem;
        color: var(--accent-pink);
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .reel-activity-item {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .reel-emoji {
        width: 3rem;
        height: 3rem;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--accent-orange), var(--accent-pink));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .chart-container {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 0.75rem;
        padding: 1.5rem;
    }
    
    .stDataFrame {
        background: var(--bg-card);
    }
    
    .stButton>button {
        background: var(--accent-purple);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background: #7c3aed;
    }
    
    /* Compact logout button - round with blue color, no hover effect */
    button[key*="logout_btn"] {
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        max-width: 40px !important;
        padding: 0 !important;
        margin: 0 !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 0.75rem !important;
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        cursor: pointer !important;
    }
    
    button[key*="logout_btn"]:hover {
        background: #3b82f6 !important;
        transform: none !important;
    }
    
    .refresh-btn {
        background: var(--accent-pink) !important;
    }
    
    .refresh-btn:hover {
        background: #db2777 !important;
    }
    
    [data-testid="stHeader"] {
        background: transparent;
    }
    
    .stExpander {
        background: var(--bg-card);
        border: 1px solid var(--border);
    }
    
    .stTextInput>div>div>input {
        background: var(--bg-card);
        color: var(--text-primary);
        border: 1px solid var(--border);
    }
    
    /* Clerk-style authentication UI */
    .auth-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .auth-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 1rem;
        padding: 2.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .auth-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .auth-title {
        font-size: 1.875rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .auth-subtitle {
        font-size: 0.875rem;
        color: var(--text-secondary);
    }
    
    .auth-button-primary {
        background: #6c47ff !important;
        color: white !important;
        border: none !important;
        border-radius: 0.5rem !important;
        font-weight: 500 !important;
    }
    
    .auth-button-primary:hover {
        background: #5a3ae6 !important;
    }
    
    /* User Avatar */
    .user-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #3b82f6;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 1rem;
        margin: 0;
        cursor: pointer;
        flex-shrink: 0;
    }
    
    /* Avatar button styling */
    button[key*="avatar_btn"] {
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        max-width: 40px !important;
        padding: 0 !important;
        margin: 0 !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        cursor: pointer !important;
    }
    
    button[key*="avatar_btn"]:hover {
        background: #3b82f6 !important;
    }
    
    /* Logout button that appears when avatar is clicked */
    button[key*="logout_btn"]:not([key*="logout_btn_header"]) {
        padding: 0.3rem 0.6rem !important;
        font-size: 0.75rem !important;
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        border-radius: 0.5rem !important;
    }
    
    button[key*="logout_btn"]:not([key*="logout_btn_header"]):hover {
        background: #2563eb !important;
    }
    
    .user-info-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }
    
    .user-email-text {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-align: center;
    }
</style>
"""


def get_default_api_token() -> str:
    return os.getenv("APIFY_API_TOKEN", "").strip()


def get_supabase_url() -> str:
    # Check multiple environment variable names
    url = os.getenv("SUPABASE_URL", "").strip() or os.getenv("NEXT_PUBLIC_SUPABASE_URL", "").strip()
    return url


def get_supabase_key() -> str:
    # Check multiple environment variable names
    key = os.getenv("SUPABASE_KEY", "").strip() or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "").strip() or os.getenv("SUPABASE_ANON_KEY", "").strip()
    return key


def get_clerk_secret_key() -> str:
    """Get Clerk secret key from environment or session state."""
    key = os.getenv("CLERK_SECRET_KEY", "").strip()
    if not key and "clerk_secret_key" in st.session_state:
        key = st.session_state.clerk_secret_key
    return key


def get_clerk_frontend_api() -> str:
    """Get Clerk frontend API key from environment or session state."""
    key = os.getenv("CLERK_FRONTEND_API", "").strip() or os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "").strip()
    if not key and "clerk_frontend_api" in st.session_state:
        key = st.session_state.clerk_frontend_api
    if not key:
        # Default key from user
        key = "pk_test_Y29tcG9zZWQtc25pcGUtMTQuY2xlcmsuYWNjb3VudHMuZGV2JA"
    return key


@st.cache_resource(show_spinner=False)
def get_client(api_token: str) -> ApifyClient:
    return ApifyClient(api_token)


@st.cache_resource(show_spinner=False)
def get_supabase_client() -> Optional[Client]:
    """Initialize Supabase client if credentials are available."""
    url = get_supabase_url()
    key = get_supabase_key()
    if url and key:
        try:
            # Temporarily remove proxy env vars to avoid client init issues
            old_proxy = os.environ.pop("HTTP_PROXY", None)
            old_https_proxy = os.environ.pop("HTTPS_PROXY", None)
            old_all_proxy = os.environ.pop("ALL_PROXY", None)
            
            try:
                client = create_client(url, key)
                return client
            finally:
                # Restore proxy environment variables if they existed
                if old_proxy:
                    os.environ["HTTP_PROXY"] = old_proxy
                if old_https_proxy:
                    os.environ["HTTPS_PROXY"] = old_https_proxy
                if old_all_proxy:
                    os.environ["ALL_PROXY"] = old_all_proxy
        except Exception as e:
            # Store error in session state for debugging
            if "supabase_error" not in st.session_state:
                st.session_state["supabase_error"] = str(e)
            return None
    return None


def test_supabase_connection() -> tuple[bool, str]:
    """Test Supabase connection and return status with error message."""
    url = get_supabase_url()
    key = get_supabase_key()
    
    if not url or not key:
        return False, "Supabase URL or Key is missing"
    
    # Validate URL format
    if not url.startswith("https://") or ".supabase.co" not in url:
        return False, f"Invalid Supabase URL format. Expected: https://xxx.supabase.co"
    
    # Validate key format (JWT tokens start with eyJ)
    if not key.startswith("eyJ"):
        return False, "Invalid Supabase Key format. Should be a JWT token starting with 'eyJ'"
    
    try:
        # Temporarily remove any proxy-related environment variables that might interfere
        old_proxy = os.environ.pop("HTTP_PROXY", None)
        old_https_proxy = os.environ.pop("HTTPS_PROXY", None)
        old_all_proxy = os.environ.pop("ALL_PROXY", None)
        
        try:
            client = create_client(url, key)
            # Try accessing auth service to verify it's available
            _ = client.auth
            # Try a simple query to verify database access (this will fail if table doesn't exist, but that's OK)
            try:
                _ = client.table("reels").select("id").limit(1).execute()
            except Exception:
                # Table might not exist yet, but connection is OK
                pass
            return True, "Connection successful"
        finally:
            # Restore proxy environment variables if they existed
            if old_proxy:
                os.environ["HTTP_PROXY"] = old_proxy
            if old_https_proxy:
                os.environ["HTTPS_PROXY"] = old_https_proxy
            if old_all_proxy:
                os.environ["ALL_PROXY"] = old_all_proxy
    except TypeError as e:
        error_msg = str(e)
        if "proxy" in error_msg.lower():
            return False, "Supabase client version issue. Try: pip install --upgrade supabase"
        return False, f"Client initialization error: {error_msg}"
    except Exception as e:
        error_msg = str(e)
        # Provide more specific error messages
        if "Invalid API key" in error_msg or "401" in error_msg or "Unauthorized" in error_msg:
            return False, "Invalid API key. Please check your Supabase anon key from Settings → API"
        elif "404" in error_msg or "Not Found" in error_msg:
            return False, "Supabase project not found. Check your project URL"
        elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            return False, "Connection timeout. Check your internet connection or if the project is paused"
        else:
            return False, f"Connection failed: {error_msg}"


def is_valid_business_email(email: str) -> bool:
    """Check if email is a valid @buyhatke.com business email."""
    return email.endswith("@buyhatke.com") and "@" in email and email.count("@") == 1


def is_admin_user(email: str) -> bool:
    """Check if user is an admin. For now, all @buyhatke.com emails are admins."""
    return is_valid_business_email(email)


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with Clerk."""
    secret_key = get_clerk_secret_key()
    if not secret_key:
        st.error("❌ Clerk secret key not configured. Please enter it in the configuration section.")
        return None
    
    if not is_valid_business_email(email):
        st.error("Only @buyhatke.com business emails are allowed.")
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }
        
        # Verify user exists in Clerk by listing users with this email
        list_users_url = f"https://api.clerk.com/v1/users?email_address={email}"
        response = requests.get(list_users_url, headers=headers)
        
        if response.status_code == 200:
            users_data = response.json()
            # Clerk returns a dict with "data" key containing the array
            users = users_data.get("data", []) if isinstance(users_data, dict) else users_data
            
            if users and len(users) > 0:
                user_info = users[0]  # Get first matching user
                # Note: Clerk doesn't verify passwords via backend API
                # In production, you'd verify a session token from Clerk frontend
                # For now, we verify the user exists and create a session
                
                # Get email from user_info
                email_addresses = user_info.get("email_addresses", [])
                user_email = email_addresses[0].get("email_address") if email_addresses else email
                
                # Get user metadata
                metadata = user_info.get("public_metadata", {})
                full_name = metadata.get("full_name", "")
                if not full_name:
                    first = user_info.get("first_name", "")
                    last = user_info.get("last_name", "")
                    full_name = f"{first} {last}".strip()
                if not full_name:
                    full_name = user_email.split("@")[0]
                
                user_data = {
                    "id": user_info.get("id"),
                    "email": user_email,
                    "full_name": full_name,
                    "is_admin": is_admin_user(user_email)
                }
                
                return {
                    "user": user_data,
                    "session": {"access_token": "clerk_session_token", "user": user_info}
                }
            else:
                st.error("❌ User not found. Please sign up first.")
        elif response.status_code == 401:
            st.error("❌ Invalid Clerk secret key. Please check your configuration.")
        else:
            error_data = response.json() if response.content else {"message": "Unknown error"}
            st.error(f"❌ Login failed: {error_data.get('message', 'Unknown error')}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {str(e)}")
    except Exception as e:
        error_msg = str(e)
        if "Invalid" in error_msg or "401" in error_msg:
            st.error("Invalid email or password.")
        else:
            st.error(f"Login failed: {error_msg}")
    return None


def signup_user(email: str, password: str, full_name: str) -> Optional[Dict[str, Any]]:
    """Sign up new user with Clerk."""
    if not is_valid_business_email(email):
        st.error("Only @buyhatke.com business emails are allowed.")
        return None
    
    secret_key = get_clerk_secret_key()
    if not secret_key:
        st.error("❌ Clerk secret key not configured. Please enter it in the configuration section.")
        return None
    
    try:
        # Clerk's backend API for creating users
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }
        
        # Create user via Clerk API
        create_user_url = "https://api.clerk.com/v1/users"
        
        # Split full name into first and last
        name_parts = full_name.strip().split()
        first_name = name_parts[0] if name_parts else email.split("@")[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        user_data = {
            "email_address": [email],
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "public_metadata": {
                "is_admin": is_admin_user(email),
                "full_name": full_name
            },
            "skip_password_checks": False,
            "skip_password_requirement": False
        }
        
        response = requests.post(create_user_url, json=user_data, headers=headers)
        
        if response.status_code == 200 or response.status_code == 201:
            user_info = response.json()
            # Get email from the response
            email_addresses = user_info.get("email_addresses", [])
            user_email = email_addresses[0].get("email_address") if email_addresses else email
            
            return {
                "user": {
                    "id": user_info.get("id"),
                    "email": user_email,
                    "full_name": full_name,
                    "is_admin": is_admin_user(email)
                },
                "session": {"access_token": "clerk_session_token", "user": user_info}
            }
        elif response.status_code == 422:
            error_data = response.json()
            errors = error_data.get("errors", [])
            error_messages = []
            for error in errors:
                if "email_address" in str(error).lower() or "email" in str(error).lower():
                    error_messages.append("This email is already registered. Please login instead.")
                elif "password" in str(error).lower():
                    error_messages.append(f"Password error: {error.get('message', 'Invalid password')}")
                else:
                    error_messages.append(error.get("message", str(error)))
            
            if error_messages:
                st.error(f"❌ {' '.join(error_messages)}")
            else:
                st.error(f"❌ Signup failed: {error_data}")
        elif response.status_code == 401:
            st.error("❌ Invalid Clerk secret key. Please check your configuration.")
        else:
            error_data = response.json() if response.content else {"message": "Unknown error"}
            error_msg = error_data.get("message") or error_data.get("errors", [{}])[0].get("message", "Unknown error")
            st.error(f"❌ Signup failed: {error_msg}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {str(e)}")
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ Signup failed: {error_msg}")
        with st.expander("🔍 Technical Details"):
            st.code(error_msg, language="text")
    return None


def logout_user():
    """Logout current user."""
    # Clear session state (keep configuration keys)
    keys_to_keep = ["supabase_url", "supabase_key", "clerk_secret_key", "clerk_frontend_api"]
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    # Explicitly clear user-related state
    st.session_state["user"] = None
    st.session_state["user_email"] = None
    st.session_state["is_admin"] = False
    # Clear query params
    if "auth_email" in st.query_params:
        del st.query_params["auth_email"]


def convert_keys_to_lowercase(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert camelCase keys to lowercase for PostgreSQL compatibility and filter invalid fields."""
    # Valid database columns (from schema - all lowercase)
    valid_columns = {
        "id", "shortcode", "ownerusername", "ownerfullname", "ownerid", "caption",
        "likescount", "commentscount", "videoviewcount", "videoplaycount", "videowatchcount",
        "repostcount", "savedcount", "sentcount", "sharecount", "locationname",
        "timestamp", "takenat", "lastupdatedat", "publishedtime",
        "displayurl", "videourl", "thumbnailurl", "audioname", "audiourl",
        "producttype", "url", "permalink", "inputurl", "payout",
        "created_at", "updated_at", "created_by_user_id", "created_by_email", "created_by_name"
    }
    
    result = {}
    for key, value in data.items():
        # Handle special cases that are already lowercase
        if key in ["created_at", "updated_at", "created_by_user_id", "created_by_email", "created_by_name", "id"]:
            result[key] = value
        else:
            # Convert camelCase to lowercase (e.g., shortCode -> shortcode, likesCount -> likescount)
            db_key = re.sub(r'(?<!^)(?=[A-Z])', '', key).lower()
            # Only include if it's a valid column (filter out 'alt', 'hashtags', 'mentions', etc.)
            if db_key in valid_columns:
                result[db_key] = value
    return result


def load_data_from_supabase(user_id: Optional[str] = None) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Load reel data from Supabase. If user_id is provided, load only that user's reels."""
    supabase = get_supabase_client()
    if not supabase:
        return [], []
    
    try:
        query = supabase.table("reels").select("*")
        if user_id:
            query = query.eq("created_by_user_id", user_id)
        response = query.order("created_at", desc=False).execute()
        if response.data:
            items = response.data
            rows = []
            for idx, item in enumerate(items, start=1):
                # Transform item data back to row format
                # Database returns lowercase keys, but we need to check both formats
                row: Dict[str, Any] = {"#": idx}
                for label, key in TABLE_FIELDS:
                    # Try both camelCase and lowercase
                    value = item.get(key) or item.get(key.lower())
                    if key == "caption" and isinstance(value, str):
                        value = textwrap.shorten(value, width=110, placeholder="…")
                    elif key == "timestamp":
                        value = format_timestamp(value)
                    elif key == "payout":
                        # Format payout as currency
                        try:
                            payout_val = float(value) if value else 0.0
                            # Round to 2 decimal places to avoid precision issues
                            payout_val = round(payout_val, 2)
                            value = f"₹{payout_val:,.2f}"
                        except (ValueError, TypeError):
                            value = "₹0.00"
                    row[label] = value or ""
                rows.append(row)
            return rows, items
    except Exception as e:
        st.warning(f"Could not load data from Supabase: {e}")
    
    return [], []


def save_data_to_supabase(items: List[Dict[str, Any]], user_id: Optional[str] = None, user_email: Optional[str] = None, user_name: Optional[str] = None) -> bool:
    """Save reel data to Supabase with user tracking."""
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        # Get existing reel IDs to avoid duplicates (check by user to allow same reel for different users)
        # Note: PostgreSQL converts unquoted identifiers to lowercase, so use lowercase column names
        existing_response = supabase.table("reels").select("id,shortcode,created_by_user_id").execute()
        existing_by_user = {}
        for item in existing_response.data:
            uid = item.get("created_by_user_id")
            if uid not in existing_by_user:
                existing_by_user[uid] = {"ids": set(), "codes": set()}
            if item.get("id"):
                existing_by_user[uid]["ids"].add(item.get("id"))
            if item.get("shortcode"):
                existing_by_user[uid]["codes"].add(item.get("shortcode"))
        
        user_existing = existing_by_user.get(user_id, {"ids": set(), "codes": set()})
        
        new_items = []
        for item in items:
            reel_id = item.get("id")
            short_code = item.get("shortCode")  # Keep camelCase from API response
            
            # Check if this user already has this reel
            if reel_id in user_existing["ids"] or short_code in user_existing["codes"]:
                # Update existing record for this user
                # First, get existing payout value from database to preserve it
                existing_payout = None
                try:
                    if reel_id:
                        existing_response = supabase.table("reels").select("payout").eq("id", reel_id).eq("created_by_user_id", user_id).execute()
                        if existing_response.data and len(existing_response.data) > 0:
                            existing_payout = existing_response.data[0].get("payout") or existing_response.data[0].get("Payout")
                except Exception:
                    pass
                
                # Convert camelCase keys to lowercase for database
                update_data = convert_keys_to_lowercase(item)
                update_data["updated_at"] = datetime.utcnow().isoformat()
                
                # Preserve existing payout value from database
                if existing_payout is not None:
                    # Always preserve the existing payout from database
                    update_data["payout"] = float(existing_payout) if existing_payout else 0.0
                else:
                    # If no existing payout found, use the one from item or default to 0
                    new_payout = item.get("payout") or item.get("Payout") or 0.0
                    update_data["payout"] = float(new_payout) if new_payout else 0.0
                
                try:
                    if user_id:
                        supabase.table("reels").update(update_data).eq("id", reel_id).eq("created_by_user_id", user_id).execute()
                except Exception:
                    try:
                        supabase.table("reels").update(update_data).eq("shortcode", short_code).eq("created_by_user_id", user_id).execute()
                    except Exception:
                        pass
                continue
            
            # Add user tracking and timestamps
            item_with_metadata = item.copy()
            item_with_metadata["created_at"] = datetime.utcnow().isoformat()
            item_with_metadata["updated_at"] = datetime.utcnow().isoformat()
            
            # Initialize payout to 0 if not present
            if "payout" not in item_with_metadata and "Payout" not in item_with_metadata:
                item_with_metadata["payout"] = 0.0
            
            if user_id:
                item_with_metadata["created_by_user_id"] = user_id
            if user_email:
                item_with_metadata["created_by_email"] = user_email
            if user_name:
                item_with_metadata["created_by_name"] = user_name
            
            # Convert camelCase keys to lowercase for database
            db_item = convert_keys_to_lowercase(item_with_metadata)
            new_items.append(db_item)
        
        # Insert new items in batches
        if new_items:
            batch_size = 100
            for i in range(0, len(new_items), batch_size):
                batch = new_items[i:i + batch_size]
                supabase.table("reels").insert(batch).execute()
        
        return True
    except Exception as e:
        st.error(f"Error saving to Supabase: {e}")
        return False


def is_reel_url(value: str) -> bool:
    return "instagram.com" in value and "/reel/" in value


def is_post_url(value: str) -> bool:
    """Check if URL is an Instagram post (not just reel)."""
    return "instagram.com" in value and "/p/" in value


def normalize_reel_input(value: str) -> Dict[str, Any]:
    trimmed = value.strip()
    if not trimmed:
        raise ValueError("Please provide a reel URL or username.")

    payload: Dict[str, Any] = {
        "resultsLimit": DEFAULT_RESULTS_LIMIT,
        "includeSharesCount": False,
        "skipPinnedPosts": False,
    }

    # Handle both reel and post URLs
    if is_reel_url(trimmed) or is_post_url(trimmed):
        clean_url = trimmed.split("?")[0].rstrip("/")
        payload["directUrls"] = [clean_url]
        payload["username"] = [clean_url]
    else:
        username = trimmed.removeprefix("@")
        payload["username"] = [username]

    return payload


def fetch_reel_data(api_token: str, reel_value: str) -> List[Dict[str, Any]]:
    run_input = normalize_reel_input(reel_value)
    client = get_client(api_token)
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    dataset = client.dataset(run["defaultDatasetId"])
    return list(dataset.iterate_items())


def format_timestamp(value: Any) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).strftime("%d %b %Y %H:%M")
    except ValueError:
        return str(value)


def transform_items(items: List[Dict[str, Any]], start_index: int) -> List[Dict[str, Any]]:
    rows = []
    for offset, item in enumerate(items, start=start_index + 1):
        row: Dict[str, Any] = {"#": offset}
        for label, key in TABLE_FIELDS:
            value = item.get(key)
            if key == "caption" and isinstance(value, str):
                value = textwrap.shorten(value, width=110, placeholder="…")
            elif key == "timestamp":
                value = format_timestamp(value)
            elif key == "payout":
                # Format payout as currency
                try:
                    payout_val = float(value) if value else 0.0
                    # Round to 2 decimal places to avoid precision issues
                    payout_val = round(payout_val, 2)
                    value = f"₹{payout_val:,.2f}"
                except (ValueError, TypeError):
                    value = "₹0.00"
            row[label] = value or ""
        rows.append(row)
    return rows


def calculate_metrics(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate metrics from items, handling both camelCase and lowercase keys."""
    total_likes = 0
    total_comments = 0
    total_views = 0
    total_payout = 0.0
    
    for item in items:
        # Try both camelCase and lowercase keys
        likes = item.get("likesCount") or item.get("likescount") or 0
        comments = item.get("commentsCount") or item.get("commentscount") or 0
        views = item.get("videoPlayCount") or item.get("videoplaycount") or item.get("videoViewCount") or item.get("videoviewcount") or 0
        payout = item.get("payout") or item.get("Payout") or 0
        
        total_likes += int(likes) if likes else 0
        total_comments += int(comments) if comments else 0
        total_views += int(views) if views else 0
        try:
            payout_val = float(payout) if payout else 0.0
            # Round to 2 decimal places to avoid precision issues
            payout_val = round(payout_val, 2)
            total_payout += payout_val
        except (ValueError, TypeError):
            total_payout += 0.0
    
    return {
        "likes": total_likes,
        "comments": total_comments,
        "views": total_views,
        "payout": total_payout,
        "reels_count": len(items),
    }


def get_creator_statistics() -> Dict[str, Any]:
    """Get statistics for all creators."""
    supabase = get_supabase_client()
    if not supabase:
        return {}
    
    try:
        # Use lowercase column names for PostgreSQL - prioritize videoplaycount over videoviewcount
        response = supabase.table("reels").select("created_by_email,created_by_name,likescount,commentscount,videoplaycount,videoviewcount").execute()
        if not response.data:
            return {}
        
        creator_stats = {}
        for item in response.data:
            email = item.get("created_by_email", "Unknown")
            name = item.get("created_by_name", email.split("@")[0] if "@" in email else "Unknown")
            
            if email not in creator_stats:
                creator_stats[email] = {
                    "name": name,
                    "email": email,
                    "reels_count": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "total_views": 0,
                }
            
            creator_stats[email]["reels_count"] += 1
            creator_stats[email]["total_likes"] += item.get("likescount", 0) or 0
            creator_stats[email]["total_comments"] += item.get("commentscount", 0) or 0
            views = item.get("videoplaycount") or item.get("videoviewcount") or 0
            creator_stats[email]["total_views"] += views or 0
        
        return creator_stats
    except Exception as e:
        st.warning(f"Could not load creator statistics: {e}")
        return {}


def get_chart_data(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not items:
        return []
    
    chart_data = []
    for item in items:
        timestamp = item.get("timestamp")
        if timestamp:
            try:
                dt = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
                day_name = dt.strftime("%a")
            except ValueError:
                day_name = "Unknown"
        else:
            day_name = "Unknown"
        
        # Try both camelCase and lowercase keys
        likes = item.get("likesCount") or item.get("likescount") or 0
        comments = item.get("commentsCount") or item.get("commentscount") or 0
        views = item.get("videoPlayCount") or item.get("videoplaycount") or item.get("videoViewCount") or item.get("videoviewcount") or 0
        
        chart_data.append({
            "day": day_name,
            "likes": int(likes) if likes else 0,
            "comments": int(comments) if comments else 0,
            "views": int(views) if views else 0,
        })
    
    return chart_data


def refresh_all_reels(api_token: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Refresh reel data while preserving user tracking metadata and payout values."""
    # First, get existing payout values from Supabase to preserve them
    supabase = get_supabase_client()
    payout_map = {}
    if supabase:
        try:
            # Get all reel IDs from current items
            reel_ids = [item.get("id") for item in items if item.get("id")]
            if reel_ids:
                # Fetch existing payout values from database
                response = supabase.table("reels").select("id, payout").in_("id", reel_ids).execute()
                if response.data:
                    for db_item in response.data:
                        reel_id = db_item.get("id")
                        payout_val = db_item.get("payout") or db_item.get("Payout") or 0.0
                        if payout_val:
                            payout_map[reel_id] = float(payout_val) if payout_val else 0.0
        except Exception:
            pass
    
    updated_items = []
    for item in items:
        url = item.get("url") or item.get("permalink") or item.get("inputUrl")
        reel_id = item.get("id")
        # Get existing payout value (from item or database)
        existing_payout = item.get("payout") or item.get("Payout") or payout_map.get(reel_id, 0.0)
        
        if url and (is_reel_url(url) or is_post_url(url)):
            try:
                new_data = fetch_reel_data(api_token, url)
                if new_data:
                    # Preserve user tracking metadata and payout from original item
                    for new_item in new_data:
                        new_item["created_by_user_id"] = item.get("created_by_user_id")
                        new_item["created_by_email"] = item.get("created_by_email")
                        new_item["created_by_name"] = item.get("created_by_name")
                        # Preserve payout value
                        new_item["payout"] = existing_payout
                    updated_items.extend(new_data)
            except Exception:
                # If refresh fails, keep original item with payout
                item["payout"] = existing_payout
                updated_items.append(item)
        else:
            # Keep original item with payout
            item["payout"] = existing_payout
            updated_items.append(item)
    return updated_items


def parse_urls_from_text(text: str) -> List[str]:
    """Parse URLs from text, one per line, filtering out invalid entries."""
    urls = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Skip "NA" entries and story markers
        if line.upper().startswith("NA") or "STORY" in line.upper():
            continue
        # Check if it's a valid Instagram URL
        if "instagram.com" in line:
            # Clean URL (remove query params)
            clean_url = line.split("?")[0].rstrip("/")
            # Only include reel or post URLs, skip profile URLs
            if "/reel/" in clean_url or "/p/" in clean_url:
                urls.append(clean_url)
    return urls


def render_login_signup():
    """Render login/signup UI with Clerk-style design."""
    # Hide Streamlit header and reduce spacing
    st.markdown("""
    <style>
        .stApp > header {
            display: none;
        }
        .stApp {
            margin-top: -80px;
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Center the content with minimal spacing
    st.markdown("""
    <div style='display: flex; justify-content: center; align-items: flex-start; padding: 1rem 2rem;'>
        <div style='max-width: 400px; width: 100%;'>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style='text-align: center; margin-bottom: 1.5rem;'>
        <h1 style='font-size: 1.875rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem;'>Welcome</h1>
        <p style='font-size: 0.875rem; color: #999999;'>Sign in to your account or create a new one</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for Sign In and Sign Up
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("<div style='margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="yourname@buyhatke.com", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            st.markdown("</div>", unsafe_allow_html=True)
            
            login_btn = st.form_submit_button("Sign In", type="primary", use_container_width=True)
            
            if login_btn:
                if not email or not password:
                    st.error("Please enter both email and password.")
                elif not is_valid_business_email(email):
                    st.error("Only @buyhatke.com business emails are allowed.")
                else:
                    with st.spinner("Signing in..."):
                        result = authenticate_user(email, password)
                        if result:
                            user = result["user"]
                            user_email_val = user.get("email") if isinstance(user, dict) else user.email
                            st.session_state["user"] = user
                            st.session_state["user_email"] = user_email_val
                            st.session_state["is_admin"] = is_admin_user(user_email_val)
                            # Store in a persistent way (using query params as fallback)
                            st.query_params["auth_email"] = user_email_val
                            st.success("✅ Login successful!")
                            st.rerun()
    
    with tab2:
        with st.form("signup_form", clear_on_submit=False):
            st.markdown("<p style='font-size: 0.875rem; color: #999999; margin-bottom: 1rem;'>Only @buyhatke.com business emails are allowed.</p>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
            full_name = st.text_input("Full Name", placeholder="John Doe", key="signup_name")
            email = st.text_input("Email", placeholder="yourname@buyhatke.com", key="signup_email")
            password = st.text_input("Password", type="password", help="Must be at least 6 characters", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
            st.markdown("</div>", unsafe_allow_html=True)
            
            signup_btn = st.form_submit_button("Create Account", type="primary", use_container_width=True)
            
            if signup_btn:
                if not full_name or not email or not password:
                    st.error("Please fill in all fields.")
                elif not is_valid_business_email(email):
                    st.error("Only @buyhatke.com business emails are allowed.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    with st.spinner("Creating your account..."):
                        result = signup_user(email, password, full_name)
                        if result:
                            user = result["user"]
                            user_email_val = user.get("email") if isinstance(user, dict) else user.email
                            st.session_state["user"] = user
                            st.session_state["user_email"] = user_email_val
                            st.session_state["is_admin"] = is_admin_user(user_email_val)
                            # Store in a persistent way (using query params as fallback)
                            st.query_params["auth_email"] = user_email_val
                            st.success("✅ Sign up successful! You are now logged in.")
                            st.rerun()
    
    # Footer
    st.markdown("""
    <div style='text-align: center; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.1);'>
        <p style='font-size: 0.75rem; color: #666666;'>Powered by buyhatke</p>
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="Instagram Reel Dashboard", 
        page_icon="📊", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Initialize session state
    if "sheet_rows" not in st.session_state:
        st.session_state["sheet_rows"] = []
        st.session_state["sheet_items"] = []
    
    # Initialize session state - don't reset if already exists
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = None
    if "is_admin" not in st.session_state:
        st.session_state["is_admin"] = False
    
    # Check if user is logged in
    # First, check if we have auth_email in query params (from previous session)
    auth_email_from_params = st.query_params.get("auth_email", None)
    if auth_email_from_params and not st.session_state.get("user_email"):
        st.session_state["user_email"] = auth_email_from_params
    
    # If session state has user_email but no user object, try to restore session
    user_email = st.session_state.get("user_email")
    if not st.session_state.get("user") and user_email:
        # Try to restore user session from Clerk
        try:
            secret_key = get_clerk_secret_key()
            if secret_key and is_valid_business_email(user_email):
                headers = {
                    "Authorization": f"Bearer {secret_key}",
                    "Content-Type": "application/json"
                }
                list_users_url = f"https://api.clerk.com/v1/users?email_address={user_email}"
                response = requests.get(list_users_url, headers=headers)
                
                if response.status_code == 200:
                    users_data = response.json()
                    users = users_data.get("data", []) if isinstance(users_data, dict) else users_data
                    
                    if users and len(users) > 0:
                        user_info = users[0]
                        email_addresses = user_info.get("email_addresses", [])
                        restored_email = email_addresses[0].get("email_address") if email_addresses else user_email
                        
                        metadata = user_info.get("public_metadata", {})
                        full_name = metadata.get("full_name", "")
                        if not full_name:
                            first = user_info.get("first_name", "")
                            last = user_info.get("last_name", "")
                            full_name = f"{first} {last}".strip()
                        if not full_name:
                            full_name = restored_email.split("@")[0]
                        
                        # Restore user session
                        st.session_state["user"] = {
                            "id": user_info.get("id"),
                            "email": restored_email,
                            "full_name": full_name,
                            "is_admin": is_admin_user(restored_email)
                        }
                        st.session_state["user_email"] = restored_email
                        st.session_state["is_admin"] = is_admin_user(restored_email)
        except Exception:
            # If restoration fails, clear the session
            st.session_state["user"] = None
            st.session_state["user_email"] = None
            st.session_state["is_admin"] = False
    
    # Check if user is logged in
    if not st.session_state.get("user"):
        render_login_signup()
        return
    
    # User is logged in - show dashboard
    user = st.session_state.get("user")
    user_email = st.session_state.get("user_email", "Unknown")
    
    # Handle both dict and object user formats
    if isinstance(user, dict):
        user_id = user.get("id")
        user_name = user.get("full_name", user_email.split("@")[0] if "@" in user_email else "User")
    else:
        user_id = user.id if user and hasattr(user, 'id') else None
        if user and hasattr(user, 'user_metadata') and user.user_metadata:
            user_name = user.user_metadata.get("full_name", user_email.split("@")[0] if "@" in user_email else "User")
        else:
            user_name = user_email.split("@")[0] if "@" in user_email else "User"
    
    is_admin = st.session_state.get("is_admin", False)
    
    # Load user-specific data from Supabase on first run
    if "data_loaded" not in st.session_state:
        st.session_state["data_loaded"] = True
        st.session_state["last_view_mode"] = "Your Reels"
        with st.spinner("Loading your reels from Supabase..."):
            rows, items = load_data_from_supabase(user_id)
            if rows and items:
                st.session_state["sheet_rows"] = rows
                st.session_state["sheet_items"] = items
    
    # Header - Compact with avatar and logout together
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    
    # Top row: Avatar + Logout together, Dashboard title, and API token
    col1, col2, col3 = st.columns([2, 4, 2])
    
    with col1:
        # User avatar with initial - clickable to show logout
        user_initial = user_email[0].upper() if user_email and user_email != "Unknown" else "U"
        
        # Check if avatar was clicked (using session state)
        avatar_clicked_key = "avatar_clicked"
        if avatar_clicked_key not in st.session_state:
            st.session_state[avatar_clicked_key] = False
        
        # Avatar button
        col_avatar1, col_avatar2 = st.columns([1, 3])
        with col_avatar1:
            if st.button(user_initial, key="avatar_btn", use_container_width=False, help="Click to show logout"):
                st.session_state[avatar_clicked_key] = not st.session_state[avatar_clicked_key]
                st.rerun()
        
        # Show logout option if avatar was clicked
        if st.session_state[avatar_clicked_key]:
            with col_avatar2:
                if st.button("🚪 Logout", key="logout_btn", use_container_width=False):
                    logout_user()
                    st.rerun()
    
    with col2:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("### Instagram Creators Dashboard", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        # Only show API token input to admins
        if is_admin:
            if "admin_api_token" not in st.session_state:
                st.session_state["admin_api_token"] = get_default_api_token() or os.getenv("APIFY_API_TOKEN", "")
            
            api_token = st.text_input(
                "API Token (Admin Only)",
                value=st.session_state["admin_api_token"],
                type="password",
                help="Apify API token - Admin only",
                label_visibility="collapsed",
                key="admin_api_token_input"
            )
            st.session_state["admin_api_token"] = api_token
        else:
            # For non-admins, use the stored admin token (hidden)
            if "admin_api_token" not in st.session_state:
                st.session_state["admin_api_token"] = get_default_api_token() or os.getenv("APIFY_API_TOKEN", "")
            api_token = st.session_state["admin_api_token"]
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Creator Statistics Dashboard
    st.markdown("### 👥 Creator Statistics")
    creator_stats = get_creator_statistics()
    
    if creator_stats:
        # Individual User Stats
        user_stats = creator_stats.get(user_email, {})
        user_metrics = calculate_metrics(st.session_state["sheet_items"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Your Statistics")
            if user_stats:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Your Reels</div>
                    <div class="metric-value">{user_stats.get('reels_count', user_metrics.get('reels_count', 0))}</div>
                    <div class="metric-trend">Total reels you've added</div>
                </div>
                """, unsafe_allow_html=True)
                
                col1a, col1b, col1c = st.columns(3)
                with col1a:
                    st.metric("Your Likes", f"{user_stats.get('total_likes', user_metrics.get('likes', 0)):,}")
                with col1b:
                    st.metric("Your Comments", f"{user_stats.get('total_comments', user_metrics.get('comments', 0)):,}")
                with col1c:
                    st.metric("Your Views", f"{user_stats.get('total_views', user_metrics.get('views', 0)):,}")
            else:
                st.info("Add reels to see your statistics here.")
        
        with col2:
            st.markdown("#### 🌐 Overall Team Statistics")
            all_creators = list(creator_stats.values())
            total_reels = sum(c.get("reels_count", 0) for c in all_creators)
            total_likes = sum(c.get("total_likes", 0) for c in all_creators)
            total_comments = sum(c.get("total_comments", 0) for c in all_creators)
            total_views = sum(c.get("total_views", 0) for c in all_creators)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Team Reels</div>
                <div class="metric-value">{total_reels}</div>
                <div class="metric-trend">Total reels from all creators</div>
            </div>
            """, unsafe_allow_html=True)
            
            col2a, col2b, col2c = st.columns(3)
            with col2a:
                st.metric("Team Likes", f"{total_likes:,}")
            with col2b:
                st.metric("Team Comments", f"{total_comments:,}")
            with col2c:
                st.metric("Team Views", f"{total_views:,}")
        
        # Creator Leaderboard
        st.markdown("#### 🏆 Creator Leaderboard")
        sorted_creators = sorted(creator_stats.values(), key=lambda x: x.get("total_views", 0), reverse=True)
        
        leaderboard_data = []
        for idx, creator in enumerate(sorted_creators, start=1):
            leaderboard_data.append({
                "Rank": idx,
                "Creator": creator.get("name", creator.get("email", "Unknown")),
                "Email": creator.get("email", "Unknown"),
                "Reels": creator.get("reels_count", 0),
                "Total Likes": f"{creator.get('total_likes', 0):,}",
                "Total Comments": f"{creator.get('total_comments', 0):,}",
                "Total Views": f"{creator.get('total_views', 0):,}",
            })
        
        if leaderboard_data:
            leaderboard_df = pd.DataFrame(leaderboard_data)
            st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)
    else:
        st.info("👆 Add reels to see creator statistics.")
    
    # View Toggle - Show first
    view_mode = st.radio("View Mode", ["Your Reels", "All Team Reels"], horizontal=True, key="view_mode_radio")
    
    # Reload data based on view mode
    if view_mode == "All Team Reels":
        if "last_view_mode" not in st.session_state or st.session_state.get("last_view_mode") != "All Team Reels":
            st.session_state["last_view_mode"] = "All Team Reels"
            with st.spinner("Loading all team reels..."):
                rows, items = load_data_from_supabase()  # Load all reels
                st.session_state["sheet_rows"] = rows
                st.session_state["sheet_items"] = items
    else:
        if "last_view_mode" not in st.session_state or st.session_state.get("last_view_mode") != "Your Reels":
            st.session_state["last_view_mode"] = "Your Reels"
            with st.spinner("Loading your reels..."):
                rows, items = load_data_from_supabase(user_id)  # Load user's reels
                st.session_state["sheet_rows"] = rows
                st.session_state["sheet_items"] = items
    
    # Import URL Section - Only show in "Your Reels" mode
    if view_mode == "Your Reels":
        tab1, tab2 = st.tabs(["➕ Single URL", "📋 Bulk Import"])
        
        with tab1:
            col1, col2 = st.columns([4, 1])
        with col1:
            reel_url = st.text_input(
                "Instagram Reel URL",
                placeholder="https://www.instagram.com/reel/XXXXXXXXX/",
                label_visibility="collapsed",
            )
        with col2:
            add_btn = st.button("Add Reel", type="primary", use_container_width=True)
        
        if add_btn:
            if not api_token:
                st.error("API token required.")
            elif not reel_url:
                st.error("Please enter a reel URL.")
            else:
                with st.spinner("Fetching data from Apify…"):
                    try:
                        results = fetch_reel_data(api_token, reel_url)
                        if results:
                            # Save to Supabase first with user tracking
                            if save_data_to_supabase(results, user_id, user_email, user_name):
                                # Reload data from Supabase to ensure consistency
                                rows, items = load_data_from_supabase(user_id)
                                st.session_state["sheet_rows"] = rows
                                st.session_state["sheet_items"] = items
                                st.success(f"✅ Added {len(results)} reel(s) to the sheet and saved to Supabase.")
                            else:
                                st.warning("✅ Added to sheet but failed to save to Supabase.")
                            st.rerun()
                        else:
                            st.warning("No data returned. Check the URL or try again later.")
                    except ValueError as value_error:
                        st.error(str(value_error))
                    except ApifyApiError as api_error:
                        error_msg = getattr(api_error, 'message', str(api_error))
                        st.error(f"Apify error: {error_msg}")
                    except Exception as exc:
                        st.error(f"Unexpected error: {exc}")
        
        with tab2:
            st.markdown("**Paste multiple Instagram reel/post URLs (one per line):**")
            bulk_urls_text = st.text_area(
                "Bulk URLs",
                placeholder="https://www.instagram.com/reel/XXXXXXXXX/\nhttps://www.instagram.com/reel/YYYYYYYYY/\nhttps://www.instagram.com/p/ZZZZZZZZZ/",
                height=200,
                label_visibility="collapsed",
            )
            col1, col2 = st.columns([1, 4])
            with col1:
                bulk_import_btn = st.button("🚀 Import All", type="primary", use_container_width=True)
            
            if bulk_import_btn:
                if not api_token:
                    st.error("API token required.")
                elif not bulk_urls_text:
                    st.error("Please paste URLs to import.")
                else:
                    urls = parse_urls_from_text(bulk_urls_text)
                    if not urls:
                        st.warning("No valid reel/post URLs found. Make sure URLs contain '/reel/' or '/p/'.")
                    else:
                        st.info(f"Found {len(urls)} valid URL(s). Processing...")
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        success_count = 0
                        failed_urls = []
                        
                        for idx, url in enumerate(urls):
                            progress = (idx + 1) / len(urls)
                            progress_bar.progress(progress)
                            status_text.text(f"Processing {idx + 1}/{len(urls)}: {url[:50]}...")
                            
                            try:
                                results = fetch_reel_data(api_token, url)
                                if results:
                                    # Save to Supabase first with user tracking
                                    if save_data_to_supabase(results, user_id, user_email, user_name):
                                        # Then add to session state
                                        new_rows = transform_items(results, len(st.session_state["sheet_rows"]))
                                        st.session_state["sheet_rows"].extend(new_rows)
                                        st.session_state["sheet_items"].extend(results)
                                        success_count += len(results)
                                    else:
                                        failed_urls.append(f"{url} - Failed to save to Supabase")
                                else:
                                    failed_urls.append(url)
                            except Exception as exc:
                                failed_urls.append(f"{url} - {str(exc)}")
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        if success_count > 0:
                            # Reload data from Supabase to ensure consistency
                            with st.spinner("Reloading data from Supabase..."):
                                rows, items = load_data_from_supabase(user_id)
                                st.session_state["sheet_rows"] = rows
                                st.session_state["sheet_items"] = items
                            st.success(f"✅ Successfully imported {success_count} reel(s) from {len(urls) - len(failed_urls)} URL(s) and saved to Supabase.")
                        if failed_urls:
                            with st.expander(f"❌ Failed URLs ({len(failed_urls)})", expanded=False):
                                for failed in failed_urls:
                                    st.text(failed)
                        st.rerun()
    else:
        # In "All Team Reels" mode, just show info
        st.info("💡 Switch to 'Your Reels' mode to add new reels. This view shows all team reels for statistics.")
    
    # Metrics and Charts
    if st.session_state["sheet_items"]:
        metrics = calculate_metrics(st.session_state["sheet_items"])
        
        # Metrics Cards
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Reels Count</div>
                <div class="metric-value">{metrics['reels_count']:,}</div>
                <div class="metric-trend">Total reels</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Likes</div>
                <div class="metric-value">{metrics['likes']:,}</div>
                <div class="metric-trend"> Up from last update</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Comments</div>
                <div class="metric-value">{metrics['comments']:,}</div>
                <div class="metric-trend">Up from last update</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Views</div>
                <div class="metric-value">{metrics['views']:,}</div>
                <div class="metric-trend"> Up from last update</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Payout</div>
                <div class="metric-value">₹{metrics.get('payout', 0):,.2f}</div>
                <div class="metric-trend">Total payout</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Refresh Button
        if st.button("🔄 Refresh All Reels", type="secondary", use_container_width=False):
            if not api_token:
                st.error("API token required.")
            else:
                with st.spinner("Refreshing all reels data…"):
                    try:
                        updated_items = refresh_all_reels(api_token, st.session_state["sheet_items"])
                        if updated_items:
                            st.session_state["sheet_items"] = updated_items
                            st.session_state["sheet_rows"] = []
                            for idx, item in enumerate(updated_items, start=1):
                                new_rows = transform_items([item], idx - 1)
                                st.session_state["sheet_rows"].extend(new_rows)
                            # Save to Supabase with user tracking
                            if save_data_to_supabase(updated_items, user_id, user_email, user_name):
                                st.success(f"✅ Refreshed {len(updated_items)} reel(s) and saved to Supabase.")
                            else:
                                st.success(f"✅ Refreshed {len(updated_items)} reel(s).")
                            st.rerun()
                    except Exception as exc:
                        st.error(f"Error refreshing: {exc}")
        
        # Chart
        chart_data = get_chart_data(st.session_state["sheet_items"])
        if chart_data:
            st.markdown("### 📈 Overview")
            chart_df = pd.DataFrame(chart_data)
            st.line_chart(
                chart_df.set_index("day")[["likes", "comments", "views"]],
                height=300,
            )
        
        # Reel Activity
        st.markdown("### 🎬 Reel Activity")
        for idx, item in enumerate(st.session_state["sheet_items"][:10], start=1):
            emoji = "🎬"
            title = item.get("caption", "Untitled Reel")
            if isinstance(title, str) and len(title) > 50:
                title = textwrap.shorten(title, width=50, placeholder="…")
            owner = item.get("ownerUsername") or item.get("ownerusername") or "Unknown"
            views = item.get("videoPlayCount") or item.get("videoplaycount") or item.get("videoViewCount") or item.get("videoviewcount") or 0
            views = int(views) if views else 0
            
            st.markdown(f"""
            <div class="reel-activity-item">
                <div class="reel-emoji">{emoji}</div>
                <div style="flex: 1;">
                    <div style="font-weight: 500; margin-bottom: 0.25rem;">{title}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">@{owner}</div>
                </div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">👁️ {views:,} views</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Data Sheet with Delete functionality
        st.markdown("### 📋 Reels Sheet")
        
        if st.session_state["sheet_rows"]:
            sheet_df = pd.DataFrame(st.session_state["sheet_rows"])
            
            if view_mode == "Your Reels":
                # Create table with delete buttons
                num_cols = len(TABLE_FIELDS) + 1  # +1 for delete column
                
                # Display header row
                header_cols = st.columns(num_cols)
                for col_idx, (label, _) in enumerate(TABLE_FIELDS):
                    with header_cols[col_idx]:
                        st.markdown(f"<div style='font-weight: bold; padding: 0.5rem; background-color: rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.1);'>{label}</div>", unsafe_allow_html=True)
                with header_cols[num_cols - 1]:
                    st.markdown(f"<div style='text-align: center; font-weight: bold; padding: 0.5rem; background-color: rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.1);'>Delete</div>", unsafe_allow_html=True)
                
                # Display data rows with delete buttons
                for row_idx, (row, item) in enumerate(zip(st.session_state["sheet_rows"], st.session_state["sheet_items"])):
                    row_cols = st.columns(num_cols)
                    
                    # Display row data
                    for col_idx, (label, key) in enumerate(TABLE_FIELDS):
                        with row_cols[col_idx]:
                            value = row.get(label, "")
                            # Make Payout editable
                            if label == "Payout":
                                payout_key = f"payout_{row_idx}_{item.get('id', row_idx)}"
                                
                                # Get current payout value - prioritize item data over formatted row value
                                current_payout_raw = item.get("payout") or item.get("Payout") or 0
                                
                                # Convert to string for exact representation
                                if isinstance(current_payout_raw, (int, float)):
                                    # Format to 2 decimal places to avoid precision issues
                                    current_payout_str = f"{current_payout_raw:.2f}"
                                elif isinstance(current_payout_raw, str):
                                    # If it's a formatted string, extract the number
                                    current_payout_str = current_payout_raw.replace("₹", "").replace(",", "").strip()
                                    try:
                                        # Validate and reformat
                                        current_payout_float = float(current_payout_str)
                                        current_payout_str = f"{current_payout_float:.2f}"
                                    except (ValueError, TypeError):
                                        current_payout_str = "0.00"
                                else:
                                    current_payout_str = "0.00"
                                
                                # Use text input for exact value entry
                                # Store the last saved value in session state to prevent unnecessary updates
                                last_saved_key = f"last_payout_{item.get('id', row_idx)}"
                                if last_saved_key not in st.session_state:
                                    st.session_state[last_saved_key] = current_payout_str
                                
                                new_payout_str = st.text_input(
                                    "",
                                    value=current_payout_str,
                                    key=payout_key,
                                    label_visibility="collapsed",
                                    help="Enter payout amount (e.g., 1500.00). Press Enter or click outside to save."
                                )
                                
                                # Validate and convert the input
                                try:
                                    if new_payout_str and new_payout_str.strip():
                                        new_payout_float = float(new_payout_str.strip())
                                        # Round to 2 decimal places
                                        new_payout_float = round(new_payout_float, 2)
                                        formatted_str = f"{new_payout_float:.2f}"
                                        
                                        # Get current value as float for comparison
                                        current_payout_float = float(current_payout_str)
                                        current_payout_float = round(current_payout_float, 2)
                                        
                                        # Only update if the value actually changed (not just a rerun)
                                        # Compare with the last saved value to avoid unnecessary updates
                                        last_saved = st.session_state.get(last_saved_key, current_payout_str)
                                        last_saved_float = float(last_saved) if last_saved else 0.0
                                        last_saved_float = round(last_saved_float, 2)
                                        
                                        # Update if changed from last saved value
                                        if abs(new_payout_float - last_saved_float) > 0.001:
                                            item["payout"] = new_payout_float
                                            row[label] = f"₹{new_payout_float:,.2f}"
                                            st.session_state[last_saved_key] = formatted_str
                                            
                                            # Save to Supabase
                                            try:
                                                supabase = get_supabase_client()
                                                if supabase:
                                                    reel_id = item.get("id")
                                                    if reel_id:
                                                        # Save as exact numeric value
                                                        supabase.table("reels").update({"payout": new_payout_float}).eq("id", reel_id).eq("created_by_user_id", user_id).execute()
                                                        st.success(f"✅ Payout updated to ₹{new_payout_float:,.2f}")
                                            except Exception as e:
                                                st.warning(f"Could not save payout: {e}")
                                    else:
                                        # Empty input, keep current value
                                        pass
                                except (ValueError, TypeError):
                                    # Invalid input, show error but don't update
                                    st.error(f"Invalid payout amount: {new_payout_str}. Please enter a number.")
                            # Make Permalink clickable
                            elif label == "Permalink":
                                # Get URL from item (try both camelCase and lowercase keys)
                                url = (item.get("url") or item.get("permalink") or item.get("inputUrl") or 
                                       item.get("inputurl") or "")
                                
                                if url:
                                    # Ensure URL is complete
                                    if not url.startswith("http"):
                                        url = f"https://www.instagram.com{url}" if url.startswith("/") else f"https://www.instagram.com/p/{url}/"
                                    st.markdown(f"<div style='padding: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.05);'><a href='{url}' target='_blank' style='color: #4A9EFF; text-decoration: none; font-weight: 500;'>🔗 View Reel</a></div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div style='padding: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); color: #666;'>No link</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='padding: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.05);'>{value}</div>", unsafe_allow_html=True)
                    
                    # Delete button in last column
                    with row_cols[num_cols - 1]:
                        delete_key = f"delete_{row_idx}_{item.get('id', row_idx)}"
                        if st.button("🗑️", key=delete_key, help="Delete this reel", use_container_width=True):
                            # Delete from Supabase if user owns it
                            reel_id = item.get("id")
                            if reel_id:
                                try:
                                    supabase = get_supabase_client()
                                    if supabase:
                                        # Delete from Supabase (only if user owns it)
                                        supabase.table("reels").delete().eq("id", reel_id).eq("created_by_user_id", user_id).execute()
                                except Exception as e:
                                    st.warning(f"Could not delete from Supabase: {e}")
                            
                            # Remove from session state
                            st.session_state["sheet_rows"].pop(row_idx)
                            st.session_state["sheet_items"].pop(row_idx)
                            
                            # Reload from Supabase to ensure consistency
                            rows, items = load_data_from_supabase(user_id)
                            st.session_state["sheet_rows"] = rows
                            st.session_state["sheet_items"] = items
                            
                            st.success("✅ Reel deleted!")
                            st.rerun()
            else:
                # In "All Team Reels" mode, just show the dataframe
                st.dataframe(sheet_df, use_container_width=True, hide_index=True)
        else:
            st.info("No reels to display. Add reels using the import section above.")
        
        # Download CSV button
        if st.session_state["sheet_rows"]:
            sheet_df = pd.DataFrame(st.session_state["sheet_rows"])
            csv_data = sheet_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", csv_data, file_name="reels_sheet.csv", mime="text/csv")
        
        with st.expander("🔍 Raw API Data"):
            st.json(st.session_state["sheet_items"])
    else:
        st.info("👆 Add your first Instagram reel URL to populate the dashboard.")


if __name__ == "__main__":
    main()
