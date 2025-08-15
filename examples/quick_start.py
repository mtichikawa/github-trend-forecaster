'''
Quick Start Example
Demonstrates basic usage of the forecaster
'''

from src.data_collector import GitHubDataCollector
from src.models.prophet_forecast import RepoForecaster


def quick_forecast(owner, name):
    '''Run complete forecast workflow'''
    
    print(f'🔮 Forecasting {owner}/{name}')
    print('=' * 50)
    
    # Step 1: Collect data
    print('\n1. Collecting repository data...')
    collector = GitHubDataCollector()
    collector.save_data(owner, name)
    
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
    forecaster.plot_forecast(
        f'{owner}/{name}',
        save_path=f'assets/{owner}_{name}_forecast.png'
    )
    
    print('\n✅ Complete!')


if __name__ == '__main__':
    # Example: Forecast PyTorch growth
    quick_forecast('pytorch', 'pytorch')
