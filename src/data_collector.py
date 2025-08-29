'''
GitHub Repository Data Collector
Fetches historical star, fork, and issue data from GitHub API
'''

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import time

try:
    from github import Github, RateLimitExceededException
    import pandas as pd
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.run(['pip', 'install', 'PyGithub', 'pandas'])
    from github import Github
    import pandas as pd


class GitHubDataCollector:
    def __init__(self, token=None):
        '''Initialize with GitHub token (optional for higher rate limits)'''
        self.github = Github(token) if token else Github()
        self.data_dir = Path('data/raw')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def get_repo_stats(self, owner, name):
        '''Fetch current repository statistics'''
        try:
            repo = self.github.get_repo(f'{owner}/{name}')
            
            stats = {
                'name': repo.full_name,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'watchers': repo.watchers_count,
                'open_issues': repo.open_issues_count,
                'language': repo.language,
                'created_at': repo.created_at.isoformat(),
                'updated_at': repo.updated_at.isoformat(),
                'description': repo.description,
                'collected_at': datetime.now().isoformat()
            }
            
            return stats
        except Exception as e:
            print(f'Error fetching {owner}/{name}: {e}')
            return None
            
    def get_star_history(self, owner, name, sample_size=1000):
        '''Get star growth history (sampled for performance)'''
        try:
            repo = self.github.get_repo(f'{owner}/{name}')
            stargazers = repo.get_stargazers_with_dates()
            
            history = []
            count = 0
            
            for star in stargazers:
                history.append({
                    'date': star.starred_at.isoformat(),
                    'cumulative_stars': count + 1
                })
                count += 1
                
                if count >= sample_size:
                    break
                    
            return history
            
        except Exception as e:
            print(f'Error getting star history: {e}')
            return []
            
    def save_data(self, owner, name):
        '''Collect and save all data for a repository'''
        print(f'Collecting data for {owner}/{name}...')
        
        # Get current stats
        stats = self.get_repo_stats(owner, name)
        if not stats:
            return False
            
        # Get star history
        print('  Fetching star history...')
        star_history = self.get_star_history(owner, name)
        
        # Combine data
        data = {
            'repository': f'{owner}/{name}',
            'stats': stats,
            'star_history': star_history
        }
        
        # Save to file
        filename = self.data_dir / f'{owner}_{name}_{datetime.now().strftime("%Y%m%d")}.json'
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f'✅ Saved to {filename}')
        return True
        
    def collect_multiple(self, repos):
        '''Collect data for multiple repositories'''
        results = []
        
        for owner, name in repos:
            success = self.save_data(owner, name)
            results.append((f'{owner}/{name}', success))
            time.sleep(2)  # Rate limiting courtesy
            
        return results


def main():
    '''Example usage'''
    
    # Initialize collector
    token = os.getenv('GITHUB_TOKEN')
    collector = GitHubDataCollector(token)
    
    # Example repositories
    repos = [
        ('tensorflow', 'tensorflow'),
        ('pytorch', 'pytorch'),
        ('scikit-learn', 'scikit-learn'),
    ]
    
    print('GitHub Repository Data Collector')
    print('=' * 50)
    
    results = collector.collect_multiple(repos)
    
    print('\nCollection Summary:')
    for repo, success in results:
        status = '✅' if success else '❌'
        print(f'  {status} {repo}')


if __name__ == '__main__':
    main()

# Updated: 2025-08-18
# Updated: 2025-08-20
# Updated: 2025-08-22
# Updated: 2025-08-26
# Updated: 2025-08-28