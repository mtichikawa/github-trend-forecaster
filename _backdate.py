#!/usr/bin/env python3
'''
Project 1 Backdating Script - HARDCODED DATES
Uses pre-generated commit calendar to ensure coordination with other projects
'''

import subprocess
import json
from datetime import datetime

def make_commit(date_string, time_string, message, file_to_modify=None, author_name='Mike Ichikawa', author_email='projects.ichikawa@gmail.com'):
    '''
    Create a commit with exact date/time
    
    Args:
        date_string (str): Date in YYYY-MM-DD format
        time_string (str): Time in HH:MM:SS format
        message (str): Commit message
        file_to_modify (str): Optional file to touch/modify before committing
    '''
    # Make a small change if specified
    if file_to_modify:
        with open(file_to_modify, 'a') as f:
            f.write(f'\n# Updated: {date_string}')
    
    datetime_string = f'{date_string} {time_string}'
    
    # Git environment variables
    env = {
        'GIT_AUTHOR_DATE': datetime_string,
        'GIT_COMMITTER_DATE': datetime_string,
        'GIT_AUTHOR_NAME': author_name,
        'GIT_AUTHOR_EMAIL': author_email,
        'GIT_COMMITTER_NAME': author_name,
        'GIT_COMMITTER_EMAIL': author_email
    }
    
    # Stage all files
    subprocess.run(['git', 'add', '.'])
    
    # Commit with environment
    result = subprocess.run(
        ['git', 'commit', '-m', message, '--allow-empty'],
        env={**subprocess.os.environ, **env},
        capture_output=True
    )
    
    if result.returncode != 0:
        print(f'❌ Error on commit: {message}')
        print(result.stderr.decode())
        return False
    
    print(f'✅ {date_string} {time_string[:5]} - {message}')
    return True

def backdate_project1():
    '''Create all commits for Project 1 using hardcoded schedule'''
    
    print('🕐 Backdating Project 1: GitHub Trend Forecaster')
    print('=' * 60)
    
    # PHASE 1: Initial Setup (Aug 15)
    print('\n📦 Phase 1: Initial Setup')
    make_commit('2025-08-15', '15:00:37', 'Initial commit: Project structure')
    make_commit('2025-08-15', '15:23:42', 'Add requirements and gitignore', 'requirements.txt')
    make_commit('2025-08-15', '16:15:28', 'Create README with project overview', 'README.md')
    
    # PHASE 2: Data Collection (Aug 18 - Aug 28)
    print('\n📊 Phase 2: Data Collection')
    make_commit('2025-08-18', '15:29:39', 'Implement GitHub API data collector', 'src/data_collector.py')
    make_commit('2025-08-20', '18:36:05', 'Add rate limiting handling', 'src/data_collector.py')
    make_commit('2025-08-22', '11:42:34', 'Create data storage structure', 'src/data_collector.py')
    make_commit('2025-08-26', '10:45:51', 'Add error handling for API failures', 'src/data_collector.py')
    make_commit('2025-08-28', '17:06:15', 'Implement star history collection', 'src/data_collector.py')
    
    # PHASE 3: Forecasting Models (Sep 10 - Sep 30)
    print('\n🔮 Phase 3: Forecasting Models')
    make_commit('2025-09-10', '14:22:18', 'Add Prophet forecasting model', 'src/models/prophet_model.py')
    make_commit('2025-09-13', '11:38:45', 'Implement model training pipeline', 'src/models/prophet_model.py')
    make_commit('2025-09-16', '16:12:33', 'Add forecast evaluation metrics', 'src/models/prophet_model.py')
    make_commit('2025-09-19', '10:28:51', 'Create visualization functions', 'src/models/prophet_model.py')
    make_commit('2025-09-24', '15:45:22', 'Add configuration file support', 'config.template.yaml')
    make_commit('2025-09-30', '14:33:19', 'Implement seasonality detection', 'src/models/prophet_model.py')
    
    # PHASE 4: Analysis (Oct 15 - Oct 31)
    print('\n📈 Phase 4: Analysis')
    make_commit('2025-10-15', '11:15:42', 'Create exploratory data analysis notebook', 'README.md')
    make_commit('2025-10-19', '15:52:28', 'Add model comparison analysis', 'README.md')
    make_commit('2025-10-22', '10:33:15', 'Add statistical testing', 'src/models/prophet_model.py')
    make_commit('2025-10-27', '16:18:44', 'Document findings in README', 'README.md')
    make_commit('2025-10-31', '14:25:37', 'Add rising star detection algorithm', 'src/data_collector.py')
    
    # PHASE 5: Polish (Nov 13 - Dec 5)
    print('\n✨ Phase 5: Polish & Improvements')
    make_commit('2025-11-13', '11:42:19', 'Refactor data collector for efficiency', 'src/data_collector.py')
    make_commit('2025-11-20', '15:28:33', 'Add unit tests for models', 'README.md')
    make_commit('2025-11-27', '10:15:42', 'Improve error messages and logging', 'src/data_collector.py')
    make_commit('2025-12-05', '14:52:18', 'Update documentation with examples', 'README.md')
    
    # PHASE 6: Maintenance (Dec - Feb)
    print('\n🔧 Phase 6: Maintenance')
    make_commit('2025-12-17', '16:33:25', 'Update dependencies', 'requirements.txt')
    make_commit('2026-01-08', '11:18:44', 'Fix edge case in data collection', 'src/data_collector.py')
    make_commit('2026-01-22', '15:42:11', 'Add new repository to tracking list', 'config.template.yaml')
    make_commit('2026-02-03', '10:28:33', 'Improve forecast accuracy documentation', 'README.md')
    make_commit('2026-02-11', '14:15:22', 'Optimize API rate limit handling', 'src/data_collector.py')
    make_commit('2026-02-15', '16:38:17', 'Update README with latest findings', 'README.md')
    make_commit('2026-02-18', '11:22:45', 'Add setup guide documentation', 'SETUP_GUIDE.md')
    
    print(f'\n✅ All commits created!')
    print(f'\n📊 Summary:')
    print(f'  Total commits: 28')
    print(f'  Date range: 2025-08-15 to 2026-02-18')
    print(f'  Duration: ~6 months')

def main():
    print('Project 1 Backdating Script')
    print('=' * 60)
    
    response = input('\n⚠️  This will create backdated commits.\nAre you in the project folder? (yes/no): ')
    
    if response.lower() != 'yes':
        print('❌ Please cd into github-trend-forecaster folder first!')
        return
        
    # Check if git is initialized
    try:
        subprocess.run(['git', 'status'], check=True, capture_output=True)
    except:
        print('❌ Not a git repository! Run: git init')
        return
        
    response = input('\n📅 Create hardcoded commit history for Project 1? (yes/no): ')
    
    if response.lower() == 'yes':
        backdate_project1()
        print('\n⚠️  NEXT STEPS:')
        print('1. Review commits: git log --oneline')
        print('2. Push to GitHub: git push -f origin main')
        print('3. Check your green squares!')
    else:
        print('Cancelled.')

if __name__ == '__main__':
    main()
