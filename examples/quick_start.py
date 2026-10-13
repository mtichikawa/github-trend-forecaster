'''
Quick Start Example
Demonstrates basic usage of the forecaster
'''

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_collector import GitHubDataCollector
from src.models.prophet_forecast import RepoForecaster
from typing import Any


def quick_forecast(owner: Any, name: Any):
    '''Run complete forecast workflow'''
    
    print(f'🔮 Forecasting {owner}/{name}')
    print('=' * 50)
    
    # Step 1: Collect data
    print('\n1. Collecting repository data...')
    collector = GitHubDataCollector(os.getenv('GITHUB_TOKEN'))
    if not collector.save_data(owner, name):
        sys.exit(f'Could not fetch repository stats for {owner}/{name}')
    
    # Step 2: Train model
    print('\n2. Training forecast model...')
    forecaster = RepoForecaster()
    data = forecaster.load_data(f'{owner}_{name}')
    df = forecaster.prepare_data(data)
    forecaster.train(df)
    
    # Step 3: Generate forecast
    print('\n3. Generating 90-day forecast...')
    forecast = forecaster.predict(periods=90)
    
    # Step 4: Show results
    current = df['y'].iloc[-1]
    predicted = forecast['yhat'].iloc[-1]
    growth = predicted - current
    
    print('\n📊 Results:')
    print(f'   Current stars: {current:,.0f}')
    print(f'   Predicted (90d): {predicted:,.0f}')
    print(f'   Expected growth: +{growth:,.0f}')
    
    # Step 5: Save visualization
    print('\n4. Creating visualization...')
    Path('assets').mkdir(exist_ok=True)
    forecaster.plot_forecast(
        f'{owner}/{name}',
        save_path=f'assets/{owner}_{name}_forecast.png'
    )
    
    print('\n✅ Complete!')


if __name__ == '__main__':
    # Example: Forecast PyTorch growth
    quick_forecast('pytorch', 'pytorch')
