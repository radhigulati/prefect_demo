from typing import Any
from datetime import timedelta

import httpx
from prefect import flow, task
from prefect.cache_policies import INPUTS
from prefect.concurrency.sync import rate_limit

@task(
    retries=3,
    cache_policy=INPUTS,
    cache_expiration=timedelta(days=1),
    log_prints=True  # Add this to see debugging output
)
def fetch_stats(github_repo: str) -> dict[str, Any]:
    """Task 1: Fetch the statistics for a GitHub repo"""
    rate_limit("github-api")
    
    # Add headers and error handling
    headers = {
        "Accept": "application/vnd.github.v3+json",
        # Add your GitHub token if you have one:
        # "Authorization": "token YOUR_GITHUB_TOKEN"
    }
    
    response = httpx.get(
        f"https://api.github.com/repos/{github_repo}",
        headers=headers,
        timeout=10
    )
    
    # Check for errors
    if response.status_code != 200:
        print(f"Error for {github_repo}: {response.status_code} - {response.text}")
        return {"error": response.text, "status_code": response.status_code}
    
    data = response.json()
    print(f"Available keys for {github_repo}: {list(data.keys())}")
    return data


@task(log_prints=True)  # Add logging
def get_stars(repo_stats: dict[str, Any]) -> int:
    """Task 2: Get the number of stars from GitHub repo statistics"""
    # Handle error cases
    if "error" in repo_stats:
        print(f"Error in API response: {repo_stats.get('error')}")
        return 0
    
    # Check if key exists
    if "stargazers_count" not in repo_stats:
        print(f"No 'stargazers_count' found. Available keys: {list(repo_stats.keys())}")
        return 0
        
    return repo_stats["stargazers_count"]


@flow(log_prints=True)
def show_stars(github_repos: list[str]) -> None:
    """Flow: Show number of GitHub repo stars"""

    # Task 1: Make HTTP requests concurrently
    stats_futures = fetch_stats.map(github_repos)

    # Task 2: Once each concurrent task completes, get the star counts
    stars = get_stars.map(stats_futures).result()

    # Show the results
    for repo, star_count in zip(github_repos, stars):
        print(f"{repo}: {star_count} stars")


# Run the flow
if __name__ == "__main__":
    show_stars([
        "PrefectHQ/prefect",
        "pydantic/pydantic",
        "huggingface/transformers"
    ])