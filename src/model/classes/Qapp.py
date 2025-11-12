import requests
import json
from typing import Dict, Any, Optional

def reloadApp() -> Dict[str, Any]:

    # Qlik automation endpoint URL
    url = 'https://phsq.us.qlikcloud.com/api/v1/automations/ad02ea4c-5257-4a99-8bde-a7f6610febf6/actions/execute'
    
    # Execution token for authentication
    token = 'ZCBMbZpYUyi90TWFJYQ8iZ35r9RJPre47QFUtJCNu4u7VTCWvKQQeZu0LuKq3UdY'
    
    # Headers for the request
    headers = {
        'X-Execution-Token': token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:

        print("\ndoing request to qlik app...\n")
        response = requests.post(url, headers=headers, timeout=30)
        
        response.raise_for_status()
        
        try:
            result = response.json()
        except json.JSONDecodeError:
       
            result = {
                'status': 'success',
                'message': 'Automation triggered successfully',
                'response_text': response.text,
                'status_code': response.status_code
            }
        
        print(f"✅ App reload automation triggered successfully!")
        print(f"Status Code: {response.status_code}")
        
        return result

    except Exception as e:
        error_msg = f"Unexpected error occurred: {e}"
        print(f"❌ Error: {error_msg}")
        return {
            'status': 'error',
            'error': error_msg,
            'error_type': 'unexpected_error'
        }


def reloadAppAsync() -> None:
    """
    Triggers the Qlik automation asynchronously without waiting for response details.
    """
    url = 'https://rbhujxybcm4eatw.us.qlikcloud.com/api/v1/automations/ad02ea4c-5257-4a99-8bde-a7f6610febf6/actions/execute'
    token = 'ZCBMbZpYUyi90TWFJYQ8iZ35r9RJPre47QFUtJCNu4u7VTCWvKQQeZu0LuKq3UdY'
    
    headers = {
        'X-Execution-Token': token,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, timeout=5)
        if response.status_code in [200, 201, 202]:
            print("✅ App reload automation triggered!")
        else:
            print(f"⚠️ Automation triggered with status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to trigger automation: {e}")

