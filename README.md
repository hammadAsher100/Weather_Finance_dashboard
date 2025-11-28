🌤️📈 Weather & Finance ETL Dashboard
A dynamic ETL and data analysis system that fetches real-time weather and financial data from third-party APIs, processes the data, and provides interactive visualizations through a professional Streamlit dashboard.

🚀 Live Demo URL: https://weatherfinancedashboard.streamlit.app/

📖 Overview
This project demonstrates a complete ETL (Extract, Transform, Load) pipeline with real-time data processing, interactive visualizations, and a modern web interface. Built for hackathon demonstration with production-ready features.

✨ Features
🌤️ Weather Analytics
Real-time weather data from OpenWeatherMap API

Global city coverage with 10,000+ cities supported

Interactive gauges for temperature, humidity, wind speed

Multi-parameter analysis with professional metrics

Weather condition visualization with emoji indicators

📈 Finance Analytics
Live stock market data from Alpha Vantage API

5,000+ stock symbols supported

Interactive candlestick charts with technical indicators

Moving averages & trend analysis

Performance metrics and returns distribution

Volume analysis and price action tracking

🛠️ Technical Features
Complete ETL pipeline (Extract → Transform → Load)

Real-time data processing with pandas

Interactive Plotly visualizations

Local caching for API rate limit optimization

Error handling for invalid inputs and API failures

Modular code structure with proper separation of concerns

Responsive design works on all devices

🎯 Quick Start
Using the Live Demo
Visit: https://weatherfinancedashboard.streamlit.app/

Navigate using the sidebar

Try these examples:

Weather: Enter "London", "New York", or "Tokyo"

Finance: Try "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN"

Local Development
bash
# Clone repository
git clone https://github.com/hammadAsher100/Hackathon_task.git
cd Hackathon_task

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run dashboard/app.py
📁 Project Structure
text
Hackathon_task/
├── api_client/                 # API clients for data extraction
│   ├── openweathermap_client.py
│   ├── alphavantage_client.py
│   └── __init__.py
├── dashboard/                  # Streamlit web application
│   └── app.py                 # Main dashboard application
├── analysis/                   # Data analysis and visualization
│   ├── finance_analysis.py
│   ├── weather_analysis.py
│   └── __init__.py
├── etl/                        # Data transformation modules
│   ├── weather_etl.py
│   ├── finance_etl.py
│   └── __init__.py
├── Task02.py                   # Command-line ETL script
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml            # Streamlit configuration
└── README.md                   # This file
🛠️ Installation & Setup
Prerequisites
Python 3.8+

pip (Python package manager)

1. Clone the Repository
bash
git clone https://github.com/hammadAsher100/Hackathon_task.git
cd Hackathon_task
2. Install Dependencies
bash
pip install -r requirements.txt
3. Set Up API Keys (Optional - Demo mode works without keys)
bash
# Create .streamlit/secrets.toml
OPENWEATHER_API_KEY = "your_openweather_api_key_here"
ALPHAVANTAGE_API_KEY = "your_alphavantage_api_key_here"
4. Run the Application
bash
streamlit run dashboard/app.py
📊 Dashboard Sections
🏠 Overview
Feature highlights and quick start guide

Statistics and capabilities overview

Interactive navigation

🌤️ Weather Dashboard
Real-time weather metrics

Interactive temperature gauges

Multi-city comparison

Weather condition analysis

📈 Finance Dashboard
Stock price charts (candlestick & line)

Technical indicators (moving averages)

Volume analysis

Returns distribution and performance metrics

📊 Combined View
Side-by-side data comparison

Summary statistics

Export capabilities

🔧 API Integration
OpenWeatherMap API
Endpoint: Current weather data

Rate Limit: 60 calls/minute (free tier)

Features: Temperature, humidity, pressure, wind speed, conditions

Alpha Vantage API
Endpoint: Stock time series data

Rate Limit: 5 calls/minute, 500 calls/day (free tier)

Features: Daily & intraday data, volume, price movements

🎨 Visualizations
Candlestick Charts - Stock price movements

Interactive Gauges - Weather metrics

Moving Averages - Technical analysis

Returns Distribution - Statistical analysis

Bar & Line Charts - Comparative analysis

Real-time Updates - Auto-refresh functionality

🚀 Deployment
This project is deployed on Streamlit Community Cloud:

Platform: Streamlit Community Cloud

Status: Live & Active

Cost: Free forever

🤝 Contributing
Fork the repository

Create a feature branch: git checkout -b feature/new-feature

Commit your changes: git commit -am 'Add new feature'

Push to the branch: git push origin feature/new-feature

Submit a pull request

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
OpenWeatherMap for weather data API

Alpha Vantage for financial data API

Streamlit for the amazing dashboard framework

Plotly for interactive visualizations

📞 Support
If you encounter any issues or have questions:

Check the Issues page

Create a new issue with detailed description

Contact: **[Hammad Asher](mailto:hammadasher06@gmail.com)**


⭐ Star this repo if you find it helpful!

