import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from api_client.openweathermap_client import OpenWeatherClient
    from api_client.alphavantage_client import AlphaVantageClient
    from analysis.finance_analysis import plot_stock
    from analysis.weather_analysis import plot_temperature
except ImportError as e:
    st.error(f"Import error: {e}. Make sure all modules are properly set up.")

# Page configuration
st.set_page_config(
    page_title="Weather & Finance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize API clients
@st.cache_resource
def get_weather_client():
    return OpenWeatherClient()

@st.cache_resource
def get_finance_client():
    try:
        return AlphaVantageClient()
    except:
        return None

# Cache API responses
@st.cache_data(ttl=300)  # 5 minutes cache for weather
def get_cached_weather(city):
    try:
        client = get_weather_client()
        return client.fetch_current_weather(city)
    except Exception as e:
        st.error(f"Weather API error: {e}")
        return None

@st.cache_data(ttl=300)  # 5 minutes cache for finance
def get_cached_stock_data(symbol, interval="Daily"):
    try:
        client = get_finance_client()
        if client is None:
            st.error("Alpha Vantage client not configured. Set ALPHAVANTAGE_API_KEY in .env")
            return None
        
        if interval.lower() == "intraday":
            return client.fetch_intraday(symbol, interval="60min")
        else:
            return client.fetch_daily(symbol)
    except Exception as e:
        st.error(f"Finance API error: {e}")
        return None

# Data transformation functions
def transform_weather_data(raw_data):
    if not raw_data:
        return None
    
    def kelvin_to_celsius(temp_k):
        return temp_k - 273.15 if temp_k else None
    
    try:
        df = pd.DataFrame([{
            "city": raw_data.get("name"),
            "country": raw_data.get("sys", {}).get("country"),
            "description": raw_data.get("weather", [{}])[0].get("description"),
            "temp_c": kelvin_to_celsius(raw_data.get("main", {}).get("temp")),
            "feels_like_c": kelvin_to_celsius(raw_data.get("main", {}).get("feels_like")),
            "temp_min_c": kelvin_to_celsius(raw_data.get("main", {}).get("temp_min")),
            "temp_max_c": kelvin_to_celsius(raw_data.get("main", {}).get("temp_max")),
            "pressure": raw_data.get("main", {}).get("pressure"),
            "humidity": raw_data.get("main", {}).get("humidity"),
            "wind_speed": raw_data.get("wind", {}).get("speed"),
            "timestamp": datetime.utcfromtimestamp(raw_data.get("dt")),
        }])
        return df
    except Exception as e:
        st.error(f"Error transforming weather data: {e}")
        return None

def transform_finance_data(raw_data, symbol):
    if not raw_data:
        return None
    
    try:
        # Find time series key
        ts_key = None
        for k in raw_data.keys():
            if "Time Series" in k:
                ts_key = k
                break
        
        if not ts_key:
            st.error("No time series data found in API response")
            return None
        
        records = []
        for dt_str, metrics in raw_data[ts_key].items():
            records.append({
                "symbol": symbol,
                "datetime": pd.to_datetime(dt_str),
                "open": float(metrics.get("1. open", 0)),
                "high": float(metrics.get("2. high", 0)),
                "low": float(metrics.get("3. low", 0)),
                "close": float(metrics.get("4. close", 0)),
                "volume": int(float(metrics.get("5. volume", 0)))
            })
        
        df = pd.DataFrame(records)
        df = df.sort_values("datetime")
        return df
    except Exception as e:
        st.error(f"Error transforming finance data: {e}")
        return None

# Visualization functions
def plot_weather_metrics(weather_df):
    if weather_df is None or weather_df.empty:
        return None
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Temperature gauge
        temp = weather_df['temp_c'].iloc[0]
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = temp,
            title = {'text': "Temperature (°C)"},
            gauge = {
                'axis': {'range': [None, 40]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 10], 'color': "lightblue"},
                    {'range': [10, 25], 'color': "yellow"},
                    {'range': [25, 40], 'color': "orange"}
                ]
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Humidity
        humidity = weather_df['humidity'].iloc[0]
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = humidity,
            title = {'text': "Humidity (%)"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkgreen"},
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Wind speed
        wind_speed = weather_df['wind_speed'].iloc[0]
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = wind_speed,
            title = {'text': "Wind Speed (m/s)"},
            gauge = {
                'axis': {'range': [0, 20]},
                'bar': {'color': "darkred"},
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def plot_stock_advanced(df, symbol):
    if df is None or df.empty:
        return None
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["📈 Candlestick", "📊 Line Chart", "📉 Returns"])
    
    with tab1:
        # Candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=df['datetime'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol
        )])
        fig.update_layout(
            title=f"{symbol} - Candlestick Chart",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Line chart with moving averages
        df = df.sort_values('datetime')
        df['MA_7'] = df['close'].rolling(window=7).mean()
        df['MA_20'] = df['close'].rolling(window=20).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['datetime'], y=df['close'], name='Close Price', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df['datetime'], y=df['MA_7'], name='7-Day MA', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=df['datetime'], y=df['MA_20'], name='20-Day MA', line=dict(color='red')))
        
        fig.update_layout(
            title=f"{symbol} - Price with Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price (USD)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Returns distribution
        df['daily_return'] = df['close'].pct_change() * 100
        returns = df['daily_return'].dropna()
        
        if not returns.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.histogram(returns, nbins=30, title="Daily Returns Distribution")
                fig.update_layout(xaxis_title="Daily Return (%)", yaxis_title="Frequency")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Summary statistics
                st.metric("Mean Return", f"{returns.mean():.4f}%")
                st.metric("Std Deviation", f"{returns.std():.4f}%")
                st.metric("Max Return", f"{returns.max():.4f}%")
                st.metric("Min Return", f"{returns.min():.4f}%")

# Main application
def main():
    st.markdown('<h1 class="main-header">🌤️📈 Weather & Finance Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose Dashboard", ["Weather", "Finance", "Combined Analysis"])
    
    st.sidebar.title("Configuration")
    st.sidebar.info("Real-time data from OpenWeatherMap and Alpha Vantage APIs")
    
    if app_mode == "Weather":
        weather_dashboard()
    elif app_mode == "Finance":
        finance_dashboard()
    else:
        combined_dashboard()

def weather_dashboard():
    st.header("🌤️ Weather Dashboard")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Search Parameters")
        city = st.text_input("Enter City Name", "London")
        country = st.text_input("Enter Country Code (optional)", "GB")
        
        if st.button("Get Weather Data", type="primary"):
            with st.spinner("Fetching weather data..."):
                # Use country code if provided
                search_query = f"{city},{country}" if country else city
                raw_data = get_cached_weather(search_query)
                
                if raw_data:
                    weather_df = transform_weather_data(raw_data)
                    
                    if weather_df is not None:
                        st.session_state.weather_data = weather_df
                        st.session_state.weather_city = city
                        st.success(f"Weather data loaded for {city}!")
                    else:
                        st.error("Failed to transform weather data")
                else:
                    st.error(f"Could not fetch weather data for {city}. Please check the city name.")
    
    with col2:
        if 'weather_data' in st.session_state:
            weather_df = st.session_state.weather_data
            city = st.session_state.get('weather_city', 'Unknown')
            
            st.subheader(f"Current Weather in {city}")
            
            # Display basic info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Temperature", f"{weather_df['temp_c'].iloc[0]:.1f}°C")
            with col2:
                st.metric("Feels Like", f"{weather_df['feels_like_c'].iloc[0]:.1f}°C")
            with col3:
                st.metric("Condition", weather_df['description'].iloc[0].title())
            
            col4, col5, col6 = st.columns(3)
            with col4:
                st.metric("Humidity", f"{weather_df['humidity'].iloc[0]}%")
            with col5:
                st.metric("Pressure", f"{weather_df['pressure'].iloc[0]} hPa")
            with col6:
                st.metric("Wind Speed", f"{weather_df['wind_speed'].iloc[0]} m/s")
            
            # Interactive charts
            plot_weather_metrics(weather_df)
            
            # Raw data
            with st.expander("View Raw Data"):
                st.dataframe(weather_df)

def finance_dashboard():
    st.header("📈 Finance Dashboard")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Search Parameters")
        symbol = st.text_input("Enter Stock Symbol", "AAPL").upper()
        interval = st.selectbox("Time Interval", ["Daily", "Intraday"])
        
        if st.button("Get Stock Data", type="primary"):
            with st.spinner("Fetching stock data..."):
                raw_data = get_cached_stock_data(symbol, interval)
                
                if raw_data:
                    finance_df = transform_finance_data(raw_data, symbol)
                    
                    if finance_df is not None:
                        st.session_state.finance_data = finance_df
                        st.session_state.finance_symbol = symbol
                        st.success(f"Stock data loaded for {symbol}!")
                    else:
                        st.error("Failed to transform finance data")
                else:
                    st.error(f"Could not fetch data for {symbol}. Please check the symbol.")
    
    with col2:
        if 'finance_data' in st.session_state:
            finance_df = st.session_state.finance_data
            symbol = st.session_state.get('finance_symbol', 'Unknown')
            
            st.subheader(f"Stock Data for {symbol}")
            
            # Display summary metrics
            latest_data = finance_df.iloc[-1]
            prev_data = finance_df.iloc[-2] if len(finance_df) > 1 else latest_data
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                price_change = latest_data['close'] - prev_data['close']
                st.metric("Current Price", f"${latest_data['close']:.2f}", 
                         f"{price_change:+.2f}")
            with col2:
                st.metric("Open", f"${latest_data['open']:.2f}")
            with col3:
                st.metric("Daily High", f"${latest_data['high']:.2f}")
            with col4:
                st.metric("Volume", f"{latest_data['volume']:,}")
            
            # Interactive charts
            plot_stock_advanced(finance_df, symbol)
            
            # Raw data
            with st.expander("View Raw Data"):
                st.dataframe(finance_df)

def combined_dashboard():
    st.header("🌤️📈 Combined Analysis")
    
    st.info("This section shows data from both weather and finance APIs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Weather Status")
        if 'weather_data' in st.session_state:
            weather_df = st.session_state.weather_data
            st.dataframe(weather_df)
        else:
            st.warning("No weather data loaded. Visit the Weather dashboard first.")
    
    with col2:
        st.subheader("Finance Status")
        if 'finance_data' in st.session_state:
            finance_df = st.session_state.finance_data
            st.dataframe(finance_df)
        else:
            st.warning("No finance data loaded. Visit the Finance dashboard first.")
    
    # Summary statistics
    if 'weather_data' in st.session_state or 'finance_data' in st.session_state:
        st.subheader("Summary Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'weather_data' in st.session_state:
                weather_df = st.session_state.weather_data
                st.write("**Weather Summary:**")
                st.write(f"- Cities: {len(weather_df['city'].unique())}")
                st.write(f"- Avg Temperature: {weather_df['temp_c'].mean():.1f}°C")
                st.write(f"- Avg Humidity: {weather_df['humidity'].mean():.1f}%")
        
        with col2:
            if 'finance_data' in st.session_state:
                finance_df = st.session_state.finance_data
                st.write("**Finance Summary:**")
                st.write(f"- Symbols: {len(finance_df['symbol'].unique())}")
                st.write(f"- Total Records: {len(finance_df)}")
                st.write(f"- Date Range: {finance_df['datetime'].min().strftime('%Y-%m-%d')} to {finance_df['datetime'].max().strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    main()