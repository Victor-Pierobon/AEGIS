import requests
import time
from config import Config

def api_health_check():
    """Check connectivity to DeepSeek API endpoints"""
    try:
        test_payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1
        }
        
        response = requests.post(
            Config.API_ENDPOINTS[0],
            headers={"Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}"},
            json=test_payload,
            timeout=5
        )
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("\nRunning A.E.G.I.S. Diagnostic Protocol...")
    print(f"Timestamp: {time.ctime()}")
    
    if api_health_check():
        print("Status: ██████ ONLINE ██████")
        print("All systems nominal")
    else:
        print("Status: ████ DEGRADED PERFORMANCE ████")
        print("Initiating fallback protocols...")

    print("Diagnostic complete\n")