import requests
import socket
import random
import json
import requests_cache
import pandas as pd
import openmeteo_requests
from retry_requests import retry
from newsapi import NewsApiClient

timezone = ''

current_temp = 0
current_feels_like_temp = 0
current_rain_global = 0

daily_temperature_max = 0
daily_temperature_min = 0

# -----------

headlines = []
source_name = []
headline_description = []
headline_url = []

# -----------

currencies = ['EUR', 'JPY', 'EGP', 'KWD', 'SAR']
currency_pairs = []
currency_pairs_values = []


def fetch_weather_api():
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 30.0626,
        "longitude": 31.2497,
        "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "rain", "wind_speed_10m"],
        "hourly": "visibility",
        "daily": ["temperature_2m_max", "temperature_2m_min", "daylight_duration", "sunshine_duration"],
        "timezone": "Africa/Cairo"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Current values. The order of variables needs to be the same as requested.
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_relative_humidity_2m = current.Variables(1).Value()
    current_apparent_temperature = current.Variables(2).Value()
    current_rain = current.Variables(3).Value()
    current_wind_speed_10m = current.Variables(4).Value()

    print(f"Current time {current.Time()}")
    print(f"Current temperature_2m {current_temperature_2m}")
    print(f"Current relative_humidity_2m {current_relative_humidity_2m}")
    print(f"Current apparent_temperature {current_apparent_temperature}")
    print(f"Current rain {current_rain}")
    print(f"Current wind_speed_10m {current_wind_speed_10m}")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min

    daily_dataframe = pd.DataFrame(data = daily_data)

    # Data
    timezone = str(str(response.Timezone()) + " " + str(response.TimezoneAbbreviation()))

    # Current weather data
    global current_temp, current_feels_like_temp, current_rain_global
    current_temp = str(int(current_temperature_2m))
    current_feels_like_temp = str(int(current_apparent_temperature))
    current_rain_global = current_rain

    # Hourly weather data
    #hourly_visibility = hourly_visibility

    # Daily weather data
    global daily_temperature_max, daily_temperature_min
    daily_temperature_max = str(int(daily_temperature_2m_max[0]))
    daily_temperature_min = str(int(daily_temperature_2m_min[0]))

    print(daily_dataframe)
    
def fetch_news_api():

    # The lists will store all obtained data. However, in the home page we will just add 5 headlines
    # A new tab may be created just for news only, where all pulled links will be displayed

    newsapi = NewsApiClient(api_key='e7cd2f47dd01455aae2935faa073bc32')
    top_headlines = newsapi.get_top_headlines(sources='bbc-news, cnn, the-verge')
    top_headlines = json.dumps(top_headlines)
    data = json.loads(top_headlines)
    #print(top_headlines)
    with open("headlines.txt", "w") as file:
        json.dump(top_headlines, file, indent=4)

    for news in data['articles']:
        headlines.append(news['title'])
        source_name.append(news['source']['name'])
        headline_description.append(news['description'])
        headline_url.append(news['url'])

    print("HEADLINES: -----------> " + str(headlines))
    #print(headline_description)

def fetch_stocks_api():
    import requests
    stocks = ['APPL', 'TSLA', 'AMZN']
    currencies = ['EUR', 'JPY', 'EGP', 'KWD', 'SAR']
    primary_currency = 'USD'
    secondary_currency = random.choice(currencies)

    api_key = 'VRY3M2RWH7KZW48N'
    url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE& \
        from_currency={primary_currency}&to_currency={secondary_currency}&apikey={api_key}'
    r = requests.get(url)
    data = r.json()

    with open("finance.txt", "w") as file:
        json.dump(data, file, indent=4)

    exchange_rate_symbol = data['Realtime Currency Exchange Rate']['1. From_Currency Code'] + '/' + data['Realtime Currency Exchange Rate']['3. To_Currency Code']
    exchange_rate_value = data['Realtime Currency Exchange Rate']['5. Exchange Rate']

    print(data)


def fetch_forex_api():
    primary_currency = 'USD'
    api_key = 'VRY3M2RWH7KZW48N'

    for currency in currencies:

        url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={primary_currency}&to_currency={currency}&apikey={api_key}'
        r = requests.get(url)
        data = r.json()

        with open("finance.txt", "w") as file:
            json.dump(data, file, indent=4)

        #exchange_rate_symbol = data['Realtime Currency Exchange Rate']['1. From_Currency Code'] + '/' + data['Realtime Currency Exchange Rate']['3. To_Currency Code']
        #exchange_rate_value = float(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])

        #currency_pairs.append(exchange_rate_symbol)
        #currency_pairs_values.append(exchange_rate_value)


    #print(currency_pairs)
    #print(currency_pairs_values)

#fetch_weather_api()
#fetch_news_api()
#fetch_forex_api()