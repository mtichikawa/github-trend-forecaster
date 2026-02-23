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
        '''
        Get star growth history (sampled for performance).

        Returns a dict with keys:
            history   - list of {date, cumulative_stars} records
            truncated - True if sample_size was reached before full history
            sampled   - number of records actually returned
        '''
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
                    print(f'  ⚠️  Star history truncated at {sample_size} records (repo may have more)')
                    return {'history': history, 'truncated': True, 'sampled': count}

            return {'history': history, 'truncated': False, 'sampled': count}

        except RateLimitExceededException:
            reset_time = self.github.get_rate_limit().core.reset
            wait_secs = max(0, (reset_time - datetime.utcnow()).total_seconds()) + 5
            print(f'  ⏳ Rate limit hit. Waiting {wait_secs:.0f}s until reset...')
            time.sleep(wait_secs)
            # Retry once after the wait
            return self.get_star_history(owner, name, sample_size)

        except Exception as e:
            print(f'Error getting star history for {owner}/{name}: {e}')
            return {'history': [], 'truncated': False, 'sampled': 0}
            
    def save_data(self, owner, name):
        '''Collect and save all data for a repository'''
        print(f'Collecting data for {owner}/{name}...')

        # Get current stats
        stats = self.get_repo_stats(owner, name)
        if not stats:
            return False

        # Get star history
        print('  Fetching star history...')
        star_result = self.get_star_history(owner, name)
        star_history = star_result['history']
        if star_result['truncated']:
            print(f'  Note: history truncated to {star_result["sampled"]} records')

        # Combine data
        data = {
            'repository': f'{owner}/{name}',
            'stats': stats,
            'star_history': star_history,
            'star_history_truncated': star_result['truncated'],
        }

        # Save to file
        filename = self.data_dir / f'{owner}_{name}_{datetime.now().strftime("%Y%m%d")}.json'
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f'✅ Saved to {filename}')
        return True

    def collect_multiple(self, repos):
        '''
        Collect data for multiple repositories with rate-limit awareness.

        Sleeps briefly between requests as a courtesy to the GitHub API.
        RateLimitExceededException is handled inside get_star_history(); if
        get_repo_stats() hits the limit it will surface as a generic exception
        and mark that repo as failed without aborting the whole run.
        '''
        results = []

        for owner, name in repos:
            try:
                success = self.save_data(owner, name)
            except RateLimitExceededException:
                reset_time = self.github.get_rate_limit().core.reset
                wait_secs = max(0, (reset_time - datetime.utcnow()).total_seconds()) + 5
                print(f'  ⏳ Rate limit hit collecting {owner}/{name}. Waiting {wait_secs:.0f}s...')
                time.sleep(wait_secs)
                success = self.save_data(owner, name)  # retry once
            except Exception as e:
                print(f'  ❌ Unexpected error collecting {owner}/{name}: {e}')
                success = False

            results.append((f'{owner}/{name}', success))
            time.sleep(2)  # courtesy delay between repos

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

