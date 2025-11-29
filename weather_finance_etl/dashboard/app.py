import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys

# Ensure the parent directory is in the path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Attempt to import custom modules
    from api_client.openweathermap_client import OpenWeatherClient
    from api_client.alphavantage_client import AlphaVantageClient
    from analysis.finance_analysis import plot_stock
    from analysis.weather_analysis import plot_temperature
except ImportError as e:
    # This block handles the case where the user's custom imports fail (necessary for execution)
    st.error(f"Import error: {e}. Make sure all modules are properly set up. Using placeholders for demonstration.")
    
    # Placeholder classes/functions to prevent the app from crashing on missing imports
    class OpenWeatherClient:
        def fetch_current_weather(self, city):
            return None
    class AlphaVantageClient:
        def fetch_daily(self, symbol):
            return None
        def fetch_intraday(self, symbol, interval):
            return None
    def plot_stock(*args):
        st.warning("Placeholder: Stock plot function not available.")
    def plot_temperature(*args):
        st.warning("Placeholder: Temperature plot function not available.")


# Page configuration
st.set_page_config(
    page_title="Weather & Finance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced custom CSS for modern styling - FIX APPLIED HERE
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(120deg, #1f77b4 0%, #ff7f0e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        color: white;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    
    /* Weather card */
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        color: white;
        margin: 1rem 0;
    }
    
    /* Finance card */
    .finance-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        color: white;
        margin: 1rem 0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #667eea;
        padding: 0.75rem;
    }
    
    /* Metric value styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        color: black;
        background-color: #f0f2f6;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: black; 
    }
    
    /* Info box styling */
    .info-box {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #ff7f0e;
        margin: 1rem 0;
    }
    
    /* Success box styling */
    .success-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* FIX FOR DISABLED CURSOR AND TEXT SELECTION */
    /* Target common display elements */
    .main .stText, .main .stMarkdown, .main h1, .main h2, .main h3, .main p, .main .stAlert {
        user-select: none;          /* Prevent text selection */
        -webkit-user-select: none;  /* For Safari */
        -moz-user-select: none;     /* For Firefox */
        -ms-user-select: none;      /* For IE/Edge */
        cursor: default !important; /* Ensure cursor is a pointer, not text I-beam */
    }
    
    /* Specifically re-enable inputs and buttons to allow user interaction */
    .stTextInput>div>div>input, .stSelectbox, .stButton>button, .stExpander {
        user-select: auto;
        cursor: auto !important;
    }
</style>
""", unsafe_allow_html=True)

# --- API CLIENT INITIALIZATION AND CACHING ---

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
@st.cache_data(ttl=300)
def get_cached_weather(city):
    try:
        client = get_weather_client()
        # Using only city name as per the previous request
        return client.fetch_current_weather(city)
    except Exception as e:
        st.error(f"Weather API error: {e}")
        return None

@st.cache_data(ttl=300)
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

# --- DATA TRANSFORMATION FUNCTIONS ---

def transform_weather_data(raw_data):
    if not raw_data:
        return None
    
    def kelvin_to_celsius(temp_k):
        return temp_k - 273.15 if temp_k else None
    
    try:
        df = pd.DataFrame([{
            "city": raw_data.get("name"),
            # Removed country code field from transformation output to simplify dashboard view
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

# Enhanced visualization functions
def plot_weather_metrics(weather_df):
    if weather_df is None or weather_df.empty:
        return None
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temp = weather_df['temp_c'].iloc[0]
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=temp,
            title={'text': "Temperature (°C)", 'font': {'size': 20, 'color': '#667eea'}},
            delta={'reference': weather_df['feels_like_c'].iloc[0], 'suffix': '°C'},
            gauge={
                'axis': {'range': [-10, 45], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#667eea"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [-10, 0], 'color': '#b3d9ff'},
                    {'range': [0, 15], 'color': '#99ccff'},
                    {'range': [15, 25], 'color': '#ffe066'},
                    {'range': [25, 35], 'color': '#ffb366'},
                    {'range': [35, 45], 'color': '#ff6666'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 38
                }
            }
        ))
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        humidity = weather_df['humidity'].iloc[0]
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=humidity,
            title={'text': "Humidity (%)", 'font': {'size': 20, 'color': '#667eea'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#4ecdc4"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 30], 'color': '#ffebcc'},
                    {'range': [30, 60], 'color': '#cce5ff'},
                    {'range': [60, 100], 'color': '#99ccff'}
                ],
            }
        ))
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        wind_speed = weather_df['wind_speed'].iloc[0]
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=wind_speed,
            title={'text': "Wind Speed (m/s)", 'font': {'size': 20, 'color': '#667eea'}},
            gauge={
                'axis': {'range': [0, 25], 'tickwidth': 1},
                'bar': {'color': "#ff6b6b"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 5], 'color': '#d4f1f4'},
                    {'range': [5, 10], 'color': '#ffd93d'},
                    {'range': [10, 15], 'color': '#ffb366'},
                    {'range': [15, 25], 'color': '#ff6b6b'}
                ],
            }
        ))
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

def plot_stock_advanced(df, symbol):
    if df is None or df.empty:
        return None
    
    tab1, tab2, tab3 = st.tabs(["📈 Candlestick Chart", "📊 Price Trends", "📉 Returns Analysis"])
    
    with tab1:
        fig = go.Figure(data=[go.Candlestick(
            x=df['datetime'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol,
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        )])
        fig.update_layout(
            title={
                'text': f"**{symbol}** - Candlestick Chart",
                'font': {'size': 24, 'color': '#667eea'}
            },
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            xaxis_rangeslider_visible=False,
            hovermode='x unified',
            plot_bgcolor='#f8f9fa',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        df = df.sort_values('datetime')
        df['MA_7'] = df['close'].rolling(window=7).mean()
        df['MA_20'] = df['close'].rolling(window=20).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['datetime'], 
            y=df['close'], 
            name='Close Price',
            line=dict(color='#667eea', width=3),
            fill='tonexty'
        ))
        fig.add_trace(go.Scatter(
            x=df['datetime'], 
            y=df['MA_7'], 
            name='7-Day MA',
            line=dict(color='#f093fb', width=2, dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=df['datetime'], 
            y=df['MA_20'], 
            name='20-Day MA',
            line=dict(color='#f5576c', width=2, dash='dot')
        ))
        
        fig.update_layout(
            title={
                'text': f"**{symbol}** - Price with Moving Averages",
                'font': {'size': 24, 'color': '#667eea'}
            },
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode='x unified',
            plot_bgcolor='#f8f9fa',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        df['daily_return'] = df['close'].pct_change() * 100
        returns = df['daily_return'].dropna()
        
        if not returns.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.histogram(
                    returns, 
                    nbins=40, 
                    title="Daily Returns Distribution",
                    color_discrete_sequence=['#667eea']
                )
                fig.update_layout(
                    xaxis_title="Daily Return (%)", 
                    yaxis_title="Frequency",
                    plot_bgcolor='#f8f9fa',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 📊 Statistics")
                # Removed delta from mean return as it should be compared to a reference, not itself
                st.metric("Mean Return", f"{returns.mean():.4f}%") 
                st.metric("Volatility (Std Dev)", f"{returns.std():.4f}%") # Clarified name
                st.metric("Max Return", f"{returns.max():.4f}%")
                st.metric("Min Return", f"{returns.min():.4f}%")

# Main application
def main():
    st.markdown('<h1 class="main-header">🌤️ Weather & Finance Dashboard 📈</h1>', unsafe_allow_html=True)
    
    # Sidebar with enhanced styling
    with st.sidebar:
        st.markdown("### 🎯 Navigation")
        app_mode = st.selectbox(
            "Choose Dashboard",
            ["🏠 Home", "🌤️ Weather", "📈 Finance", "🔄 Combined Analysis"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### ⚙️ Configuration")
        st.info("📡 Real-time data from **OpenWeatherMap** and **Alpha Vantage** APIs. Data refreshes every 5 minutes.")
        
        st.markdown("---")
        st.markdown("### 📊 Quick Status")
        if 'weather_data' in st.session_state:
            st.success("✅ Weather data loaded")
        if 'finance_data' in st.session_state:
            st.success("✅ Finance data loaded")
    
    if app_mode == "🏠 Home":
        home_dashboard()
    elif app_mode == "🌤️ Weather":
        weather_dashboard()
    elif app_mode == "📈 Finance":
        finance_dashboard()
    else:
        combined_dashboard()

def home_dashboard():
    st.markdown("## Welcome to Your Personal Dashboard! 👋")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="weather-card">
            <h2>🌤️ Weather Dashboard</h2>
            <p>Get current weather for any city, including temperature, humidity, and wind speed. Start exploring now!</p>
            <ul>
                <li>Current temperature and conditions</li>
                <li>Humidity and pressure data</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="finance-card">
            <h2>📈 Finance Dashboard</h2>
            <p>Track your favorite stocks with advanced charts like Candlesticks and Moving Averages.</p>
            <ul>
                <li>Price Trends and Moving Averages</li>
                <li>Volatility and Returns Analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("## 🚀 Getting Started")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### Step 1: Navigate
        Select the **Weather** or **Finance** dashboard from the sidebar on the left.
        """)
    
    with col2:
        st.markdown("""
        ### Step 2: Input
        Enter your search parameters: **City Name** (Weather) or **Stock Symbol** (Finance).
        """)
    
    with col3:
        st.markdown("""
        ### Step 3: Analyze
        Click the button to fetch and instantly visualize the interactive data.
        """)

def weather_dashboard():
    st.markdown("## 🌤️ Weather Dashboard")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🔍 Search Weather")
        # Removed Country Code input
        city = st.text_input("Enter City Name (e.g., Tokyo, Berlin)", "London", key="weather_city_input")
        
        st.markdown("")
        if st.button("🌡️ Get Weather Data", type="primary", use_container_width=True):
            with st.spinner("🔄 Fetching weather data..."):
                # Pass only the city name to the API
                raw_data = get_cached_weather(city)
                
                if raw_data:
                    weather_df = transform_weather_data(raw_data)
                    
                    if weather_df is not None:
                        st.session_state.weather_data = weather_df
                        st.session_state.weather_city = city
                        st.success(f"✅ Weather data loaded for **{city}**!")
                    else:
                        st.error("❌ Failed to transform weather data")
                else:
                    st.error(f"❌ Could not fetch weather data for **{city}**. Please check the city name.")
        
        if 'weather_data' in st.session_state:
            st.markdown("---")
            st.markdown("### 📍 Current Location")
            st.info(f"**{st.session_state.get('weather_city', 'Unknown')}**")
    
    with col2:
        if 'weather_data' in st.session_state:
            weather_df = st.session_state.weather_data
            city = st.session_state.get('weather_city', 'Unknown')
            
            st.markdown(f"### Current Weather in **{city}**")
            
            # Weather condition with large display
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     padding: 2rem; border-radius: 20px; text-align: center; color: white;'>
                    <h1 style='font-size: 4rem; margin: 0;'>{weather_df['temp_c'].iloc[0]:.1f}°C</h1>
                    <p style='font-size: 1.5rem; margin: 0.5rem 0;'>{weather_df['description'].iloc[0].title()}</p>
                    <p style='font-size: 1rem; opacity: 0.9;'>Feels like {weather_df['feels_like_c'].iloc[0]:.1f}°C</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_b:
                st.metric("Min Temp", f"{weather_df['temp_min_c'].iloc[0]:.1f}°C")
                st.metric("Max Temp", f"{weather_df['temp_max_c'].iloc[0]:.1f}°C")
                st.metric("Pressure", f"{weather_df['pressure'].iloc[0]} hPa")
            
            st.markdown("---")
            
            # Interactive weather gauges
            st.markdown("### 📊 Detailed Metrics")
            plot_weather_metrics(weather_df)
            
            # Additional info
            with st.expander("📋 View Detailed Data"):
                st.dataframe(weather_df, use_container_width=True)

def finance_dashboard():
    st.markdown("## 📈 Finance Dashboard")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🔍 Search Stocks")
        symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA)", "AAPL", key="stock_symbol_input").upper()
        interval = st.selectbox("Time Interval", ["Daily", "Intraday"])
        
        st.markdown("")
        if st.button("📊 Get Stock Data", type="primary", use_container_width=True):
            with st.spinner("🔄 Fetching stock data..."):
                raw_data = get_cached_stock_data(symbol, interval)
                
                if raw_data:
                    finance_df = transform_finance_data(raw_data, symbol)
                    
                    if finance_df is not None:
                        st.session_state.finance_data = finance_df
                        st.session_state.finance_symbol = symbol
                        st.success(f"✅ Stock data loaded for **{symbol}**!")
                    else:
                        st.error("❌ Failed to transform finance data")
                else:
                    st.error(f"❌ Could not fetch data for **{symbol}**. Please check the symbol.")
        
        if 'finance_data' in st.session_state:
            st.markdown("---")
            st.markdown("### 📍 Current Symbol")
            st.info(f"**{st.session_state.get('finance_symbol', 'Unknown')}**")
    
    with col2:
        if 'finance_data' in st.session_state:
            finance_df = st.session_state.finance_data
            symbol = st.session_state.get('finance_symbol', 'Unknown')
            
            st.markdown(f"### Stock Data for **{symbol}**")
            
            # Display summary metrics
            latest_data = finance_df.iloc[-1]
            prev_data = finance_df.iloc[-2] if len(finance_df) > 1 else latest_data
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                price_change = latest_data['close'] - prev_data['close']
                pct_change = (price_change / prev_data['close'] * 100) if prev_data['close'] != 0 else 0
                st.metric(
                    "Current Price", 
                    f"${latest_data['close']:.2f}", 
                    f"{price_change:+.2f} ({pct_change:+.2f}%)"
                )
            
            with col2:
                st.metric("Open", f"${latest_data['open']:.2f}")
            
            with col3:
                st.metric("High", f"${latest_data['high']:.2f}")
            
            with col4:
                vol_formatted = f"{latest_data['volume']/1e6:.2f}M" if latest_data['volume'] > 1e6 else f"{latest_data['volume']:,}"
                st.metric("Volume", vol_formatted)
            
            st.markdown("---")
            
            # Interactive charts
            plot_stock_advanced(finance_df, symbol)
            
            # Raw data
            with st.expander("📋 View Raw Stock Data"):
                st.dataframe(finance_df, use_container_width=True)

def combined_dashboard():
    st.markdown("## 🔄 Combined Analysis Dashboard")
    
    st.info("📊 This section displays comprehensive data from both **Weather** and **Finance** APIs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌤️ Weather Summary")
        if 'weather_data' in st.session_state:
            weather_df = st.session_state.weather_data
            city = st.session_state.get('weather_city', 'Unknown')
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                 padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 1rem;'>
                <h3 style='margin: 0;'>📍 {city}</h3>
                <h2 style='margin: 0.5rem 0;'>{weather_df['temp_c'].iloc[0]:.1f}°C</h2>
                <p style='margin: 0;'>{weather_df['description'].iloc[0].title()}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.dataframe(weather_df, use_container_width=True)
        else:
            st.warning("⚠️ No weather data loaded. Visit the **Weather** dashboard first.")
    
    with col2:
        st.markdown("### 📈 Finance Summary")
        if 'finance_data' in st.session_state:
            finance_df = st.session_state.finance_data
            symbol = st.session_state.get('finance_symbol', 'Unknown')
            latest_data = finance_df.iloc[-1]
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                 padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 1rem;'>
                <h3 style='margin: 0;'>📊 {symbol}</h3>
                <h2 style='margin: 0.5rem 0;'>${latest_data['close']:.2f}</h2>
                <p style='margin: 0;'>Latest closing price</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.dataframe(finance_df.tail(10), use_container_width=True)
        else:
            st.warning("⚠️ No finance data loaded. Visit the **Finance** dashboard first.")
    
    # Summary statistics
    if 'weather_data' in st.session_state or 'finance_data' in st.session_state:
        st.markdown("---")
        st.markdown("## 📊 Overall Summary Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'weather_data' in st.session_state:
                weather_df = st.session_state.weather_data
                st.markdown("### 🌤️ Weather Overview")
                
                metrics_col1, metrics_col2 = st.columns(2)
                with metrics_col1:
                    st.metric("Avg Temperature", f"{weather_df['temp_c'].mean():.1f}°C")
                    st.metric("Avg Humidity", f"{weather_df['humidity'].mean():.1f}%")
                with metrics_col2:
                    st.metric("Avg Wind Speed", f"{weather_df['wind_speed'].mean():.1f} m/s")
                    st.metric("Avg Pressure", f"{weather_df['pressure'].mean():.1f} hPa")
        
        with col2:
            if 'finance_data' in st.session_state:
                finance_df = st.session_state.finance_data
                st.markdown("### 📈 Financial Overview")
                
                # Calculate metrics for the finance data
                finance_df['daily_return'] = finance_df['close'].pct_change() * 100
                returns = finance_df['daily_return'].dropna()
                
                metrics_col1, metrics_col2 = st.columns(2)
                with metrics_col1:
                    st.metric("Total Records", f"{len(finance_df):,}")
                    st.metric("Mean Return", f"{returns.mean():.4f}%")
                with metrics_col2:
                    st.metric("Max Price", f"${finance_df['high'].max():.2f}")
                    st.metric("Volatility", f"{returns.std():.4f}%")
                    

if __name__ == "__main__":
    main()