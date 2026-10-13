# GitHub Repository Trend Forecaster

Predict future growth of GitHub repositories using time series forecasting.

## Features

- Automatic data collection from GitHub API
- Facebook Prophet forecasting model
- Trend and seasonality analysis
- Forecast and trend/seasonality plots (matplotlib)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Collect star history for tensorflow, pytorch and scikit-learn to data/raw/
export GITHUB_TOKEN=...   # required: without a token GitHub returns 401 for star history
python src/data_collector.py

# Forecast one of them
python src/models/prophet_forecast.py pytorch/pytorch
```

Run both from the project root. If the star-history request fails, the collector writes no file for that repository: `save_data` raises a `RuntimeError` naming the repository and the cause, and the collector script reports it and exits non-zero.

The CSVs already in `data/raw/` are generated demo data (built in `notebooks/trend_forecaster_analysis.ipynb`), not real star counts. The forecaster reads the collector's JSON files, not these CSVs.

## Usage

```python
import os

from src.data_collector import GitHubDataCollector
from src.models.prophet_forecast import RepoForecaster

# Collect data
collector = GitHubDataCollector(os.getenv('GITHUB_TOKEN'))
collector.save_data('pytorch', 'pytorch')

# Forecast
forecaster = RepoForecaster()
data = forecaster.load_data('pytorch_pytorch')
df = forecaster.prepare_data(data)
forecaster.train(df)
forecast = forecaster.predict(periods=90)

# Visualize
forecaster.plot_forecast('pytorch/pytorch')
```

## What I Learned

- Time series forecasting with Prophet
- Working with GitHub API and rate limiting
- Handling sparse time series data
- Visualization of predictions with uncertainty

## LSTM Comparison

Not built. `notebooks/lstm_comparison_motivation.ipynb` looks at Prophet's residuals to see whether an LSTM would have room to improve. There is no LSTM model in the code.

## Contact

Mike Ichikawa — projects.ichikawa@gmail.com