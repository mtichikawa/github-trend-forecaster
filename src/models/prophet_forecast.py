'''
Time Series Forecasting with Facebook Prophet
Predicts future repository growth
'''

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

try:
    from prophet import Prophet
    import matplotlib.pyplot as plt
except ImportError:
    print("Installing Prophet...")
    import subprocess
    subprocess.run(['pip', 'install', 'prophet', 'matplotlib'])
    from prophet import Prophet
    import matplotlib.pyplot as plt


class RepoForecaster:
    def __init__(self):
        self.model = None
        self.forecast = None
        
    def load_data(self, repo_name):
        '''Load repository data from collected JSON'''
        data_dir = Path('data/raw')
        
        # Find most recent data file
        pattern = f'*{repo_name.replace("/", "_")}*.json'
        files = list(data_dir.glob(pattern))
        
        if not files:
            raise FileNotFoundError(f'No data found for {repo_name}')
            
        latest = max(files, key=lambda p: p.stat().st_mtime)
        
        with open(latest, 'r') as f:
            data = json.load(f)
            
        return data
        
    def prepare_data(self, data):
        '''Convert to Prophet format (ds, y columns)'''
        star_history = data.get('star_history', [])
        
        if not star_history:
            raise ValueError('No star history in data')
            
        df = pd.DataFrame(star_history)
        df['ds'] = pd.to_datetime(df['date'])
        df['y'] = df['cumulative_stars']
        
        return df[['ds', 'y']]
        
    def train(self, df):
        '''Train Prophet model'''
        print('Training forecasting model...')
        
        self.model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True
        )
        
        self.model.fit(df)
        print('✅ Model trained')
        
    def predict(self, periods=90):
        '''Generate forecast'''
        if not self.model:
            raise ValueError('Model not trained yet')
            
        future = self.model.make_future_dataframe(periods=periods)
        self.forecast = self.model.predict(future)
        
        return self.forecast
        
    def evaluate(self, test_df):
        '''Calculate forecast accuracy'''
        if self.forecast is None:
            raise ValueError('No forecast available')
            
        # Merge actual and predicted
        merged = test_df.merge(
            self.forecast[['ds', 'yhat']],
            on='ds',
            how='inner'
        )
        
        if len(merged) == 0:
            return {}
            
        # Calculate metrics
        mae = np.mean(np.abs(merged['y'] - merged['yhat']))
        rmse = np.sqrt(np.mean((merged['y'] - merged['yhat']) ** 2))
        
        # R-squared
        ss_res = np.sum((merged['y'] - merged['yhat']) ** 2)
        ss_tot = np.sum((merged['y'] - np.mean(merged['y'])) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        metrics = {
            'MAE': round(mae, 2),
            'RMSE': round(rmse, 2),
            'R2': round(r2, 4),
            'samples': len(merged)
        }
        
        return metrics
        
    def plot_forecast(self, repo_name, save_path=None):
        '''Create forecast visualization'''
        if self.forecast is None:
            raise ValueError('No forecast to plot')
            
        fig = self.model.plot(self.forecast)
        plt.title(f'{repo_name} - Star Growth Forecast')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Stars')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f'✅ Plot saved to {save_path}')
        else:
            plt.show()
            
        plt.close()
        
    def plot_components(self, save_path=None):
        '''Plot trend and seasonality components'''
        if self.forecast is None:
            raise ValueError('No forecast to plot')
            
        fig = self.model.plot_components(self.forecast)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f'✅ Components plot saved to {save_path}')
        else:
            plt.show()
            
        plt.close()


def main():
    '''Example forecasting workflow'''
    import sys
    
    repo_name = sys.argv[1] if len(sys.argv) > 1 else 'tensorflow/tensorflow'
    
    print(f'Forecasting growth for {repo_name}')
    print('=' * 50)
    
    # Initialize forecaster
    forecaster = RepoForecaster()
    
    # Load and prepare data
    print('Loading data...')
    data = forecaster.load_data(repo_name)
    df = forecaster.prepare_data(data)
    print(f'  Loaded {len(df)} data points')
    
    # Train model
    forecaster.train(df)
    
    # Make predictions
    print('Generating 90-day forecast...')
    forecast = forecaster.predict(periods=90)
    
    # Show prediction
    current_stars = df['y'].iloc[-1]
    predicted_stars = forecast['yhat'].iloc[-1]
    growth = predicted_stars - current_stars
    
    print(f'\nForecast Results:')
    print(f'  Current stars: {current_stars:,.0f}')
    print(f'  Predicted (90 days): {predicted_stars:,.0f}')
    print(f'  Expected growth: +{growth:,.0f} stars')
    
    # Save plot
    output_dir = Path('assets')
    output_dir.mkdir(exist_ok=True)
    
    repo_safe = repo_name.replace('/', '_')
    forecaster.plot_forecast(
        repo_name,
        save_path=f'assets/{repo_safe}_forecast.png'
    )


if __name__ == '__main__':
    main()
