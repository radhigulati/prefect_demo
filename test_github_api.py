import httpx
from pprint import pprint

def fetch_stats(github_repo: str):
    """Fetch the statistics for a GitHub repo"""
    print(f"Fetching stats for {github_repo}...")
    
    response = httpx.get(
        f"https://api.github.com/repos/{github_repo}",
        headers={"Accept": "application/vnd.github.v3+json"}
    )
    
    print(f"Status code: {response.status_code}")
    
    # Get the JSON response
    data = response.json()
    
    # Print all keys in the response
    print(f"Keys in response: {list(data.keys())}")
    
    # Pretty print the first part of the response
    print("Response preview:")
    pprint(data, depth=1)
    
    return data

# Run for a single repository
if __name__ == "__main__":
    repo = "PrefectHQ/prefect"  # Example repository
    result = fetch_stats(repo)
    
    # Check if stargazers_count exists
    if "stargazers_count" in result:
        print(f"\nStars: {result['stargazers_count']}")
    else:
        print("\nNo stargazers_count found in response!")