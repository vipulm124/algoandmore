import requests
from email.utils import parsedate_to_datetime
from datetime import datetime
import time

def parse_retry_after(retry_after_value):
    """Parse Retry-After header (seconds or Http date)"""
    try:
        return int(retry_after_value)
    except ValueError:
        try:
            retry_datetime = parsedate_to_datetime(retry_after_value)
            wait_seconds  = (retry_datetime - datetime.now(retry_datetime.tzinfo)).total_seconds()
            return max(0, int(wait_seconds))
        except:
            return None


def make_request_with_retry(url, max_retries=5):

    retries = 0

    while retries <= max_retries:
        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                print(f"Success: {response.json()}")
                return response
            
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")

                if retry_after:
                    wait_time = parse_retry_after(retry_after)

                    if wait_time:
                        print(f"Rate limited (429). Retry-After: {retry_after}")
                        print(f"Waiting {wait_time} seconds....")
                        time.sleep(wait_time)
                        retries += 1
                        continue

                print("Rate limited but couldn't parse Retry-After header")
                break

            elif response.status_code == 503:
                retry_after = response.headers.get("Retry-After")

                if retry_after:
                    wait_time = parse_retry_after(retry_after)
                    if wait_time:
                        print(f"Service unavailable (503). Retry-After: {retry_after}") 
                        print(f"Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        retries += 1
                        continue
                
                print("Service unavailable")
                break

            else:
                print(f"Error: {response.status_code} - {response.text}")
                break
        
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break

    print(f"Failed after: {retries} retries")
    return None

def test_rate_limiting():
    """Test rate limiting with Retry-After"""
    print("=" * 60)
    print("Testing Rate Limiting (429 with Retry-After in seconds)")
    print("=" * 60)

    for i in range(6):
        print(f"\n Request {i+1}:")
        make_request_with_retry('http://localhost:8000/api/data')
        time.sleep(0.5)

def test_service_unavailable():
    """Test 503 with Retry-After as Http data"""
    print("\n" + "=" * 60)
    print("Testing Service Unavailable (503 with Retry-After as date)")
    print("=" * 60)
    
    print("\nRequest:")
    make_request_with_retry('http://localhost:8000/api/status')


if __name__ == "__main__":
    # requests.get("http://localhost:8000/reset")

    # Run tests
    test_rate_limiting()
    test_service_unavailable()



