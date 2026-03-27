'''
Time Series Forecasting with Facebook Prophet
Predicts future repository growth
'''

import json
import logging
import pandas as pd

log = logging.getLogger(__name__)
import numpy as np
from pathlib import Path
from datetime import datetime

from prophet import Prophet
import matplotlib.pyplot as plt


class RepoForecaster:
    """
    Prophet-based repository star growth forecaster.

    Loads collected GitHub star history from data/raw/, trains a Prophet
    model, and generates multi-day forecasts with uncertainty intervals.

    Interface contract — the LSTM comparison model (src/models/lstm_model.py,
    to be built in U1 W2) must expose the same public methods so that notebooks
    and scripts can swap models without code changes:

        load_data(repo_name: str) -> dict
            Load raw data dict from data/raw/.

        prepare_data(data: dict) -> pd.DataFrame
            Return a DataFrame with at minimum columns 'ds' (datetime) and 'y' (numeric).

        train(df: pd.DataFrame) -> None
            Fit the model in-place; sets self.model.

        predict(periods: int = 90) -> pd.DataFrame
            Return a forecast DataFrame containing at minimum 'ds' and 'yhat'.
            May also include 'yhat_lower', 'yhat_upper'.

        evaluate(test_df: pd.DataFrame) -> dict
            Return {'MAE': float, 'RMSE': float, 'R2': float, 'samples': int}.

        plot_forecast(repo_name: str, save_path: str = None) -> None
        plot_components(save_path: str = None) -> None

    For non-default hyperparameters use fit_with_config() from prophet_model.py
    instead of train(). fit_with_config() replaces self.model in-place so
    predict() and evaluate() continue to work normally afterward.
    """

    def __init__(self):
        self.model = None
        self.forecast = None  # see class docstring for LSTM-compatible interface contract

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
        """
        Train Prophet model with default hyperparameters.

        Sets self.model. For configurable hyperparameters use
        fit_with_config(self, df, config) from prophet_model.py instead.

        Args:
            df: DataFrame with columns 'ds' (datetime) and 'y' (cumulative stars).
        """
        print('Training forecasting model...')
        
        self.model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True
        )
        
        self.model.fit(df)
        print('✅ Model trained')
        
    def predict(self, periods=90):
        """
        Generate forecast for the given number of future days.

        Args:
            periods: number of days ahead to forecast (default 90).

        Returns:
            DataFrame with columns including 'ds', 'yhat', 'yhat_lower', 'yhat_upper'.
            Stores result in self.forecast for use by evaluate() and plot methods.
        """
        if not self.model:
            raise ValueError('Model not trained yet')
            
        future = self.model.make_future_dataframe(periods=periods)
        self.forecast = self.model.predict(future)
        
        return self.forecast
        
    def evaluate(self, test_df):
        """
        Calculate forecast accuracy against held-out actuals.

        Joins test_df['ds'] with self.forecast['yhat'] on date and computes
        MAE, RMSE, and R². The LSTM model must return the same keys.

        Args:
            test_df: DataFrame with columns 'ds' and 'y' (actual values).

        Returns:
            dict with keys: 'MAE' (float), 'RMSE' (float), 'R2' (float), 'samples' (int).
            Returns empty dict if no overlapping dates are found.
        """
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
