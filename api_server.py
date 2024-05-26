import requests
import socket
import random
import json
import requests_cache
import pandas as pd
import openmeteo_requests
from retry_requests import retry
from newsapi import NewsApiClient
import threading

timezone = ''

# -----------

current_temp = 0
current_feels_like_temp = 0
current_rain_global = 0

daily_temperature_max = 0
daily_temperature_min = 0

# -----------

trending_topics = []

# -----------

headlines = []
source_name = []
headline_description = []
headline_url = []

# -----------

currencies = ['EUR', 'JPY', 'EGP']
currency_pairs = []
currency_pairs_values = []
currency_dict = {}

# -----------

image_title = ''
image_description = ''

# -----------

number_fact = ''

# -----------

dog_fact = ''
cat_fact = ''

# -----------

match_teams = []
match_date = []
match_time = []
match_stadium = []

# -----------

job_titles = []
job_company = []
job_location = []


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
    
def fetch_twitter_api():
    global trending_topics
    url = "https://twitter154.p.rapidapi.com/trends/"

    querystring = {"woeid":"1"}

    headers = {
        "X-RapidAPI-Key": "f35d6cc549msh5379362dc0450acp14361bjsn793713a82508",
        "X-RapidAPI-Host": "twitter154.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    response_text = response.content.decode("utf-8")
    data_string = response_text[1:-1]   # remove [] from json
    data = json.loads(data_string)

    with open('response.json', 'w') as outfile:
        json.dump(data, outfile)

    with open('response.json') as infile:
        data = json.load(infile)

    trending_topics = [trend["name"] for trend in data['trends']]
    return trending_topics

def fetch_news_api():

    # The lists will store all obtained data. However, in the home page we will just add 5 headlines
    # A new tab may be created just for news only, where all pulled links will be displayed

    newsapi = NewsApiClient(api_key='e7cd2f47dd01455aae2935faa073bc32')
    top_headlines = newsapi.get_top_headlines(sources='bbc-news, cnn, the-verge')
    top_headlines = json.dumps(top_headlines)
    data = json.loads(top_headlines)
    #print(top_headlines)
    with open("headlines.json", "w") as file:
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
    global currency_dict

    url = "https://currency-conversion-and-exchange-rates.p.rapidapi.com/latest"
    #querystring = {"from":"EUR", "to":"EUR,JPY,EGP"}
    headers = {
        "X-RapidAPI-Key": "f35d6cc549msh5379362dc0450acp14361bjsn793713a82508",
        "X-RapidAPI-Host": "currency-conversion-and-exchange-rates.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    usd_value = data["rates"].get("USD")
    jpy_value = data["rates"].get("JPY")
    eur_value = data["rates"].get("EGP")

    currency_dict = {'EUR/USD': usd_value, 'EUR/JPY': jpy_value, 'EUR/EGP': eur_value}

    return currency_dict

def fetch_image_of_the_day():
    api_key = 'olPDz85SxHhuZfK7vSAY7vocjSQhnrIlglY64O7N'
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"

    response = requests.get(url)
    data = response.json()
    
    image_url = data["url"]
    image_title = data["title"]
    image_description = data["explanation"]
    
    print(f"Image URL: {image_url}")
    print(f"Title: {image_title}")
    print(f"Explanation: {image_description}")

    response = requests.get(image_url)
    image_data = response.content

    with open("image_of_the_day.jpg", "wb") as file:
        file.write(image_data)

    print(f"Image downloaded successfully as 'image_of_the_day.jpg'")

    return image_title, image_description

def fetch_number_fact_of_the_day():
    api_url = "http://numbersapi.com/random/trivia?json"
    response = requests.get(api_url)
    data = response.json()
    number_fact = data.get("text")
    return number_fact

def fetch_random_famous_quote():
    url = "https://twitter154.p.rapidapi.com/user/details"

    headers = {
        "X-RapidAPI-Key": "f35d6cc549msh5379362dc0450acp14361bjsn793713a82508",
        "X-RapidAPI-Host": "twitter154.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    print(response.json())

def fetch_football_api():

    from datetime import date, timedelta

    today = date.today()
    one_week_from_today = today + timedelta(days=3)

    api_key = "2b69fb2e142a35a9304bd95df97f1958f2aa8184e2ff4f8121219ed0f91a18c5"
    url = f"https://apiv2.allsportsapi.com/football/?met=Fixtures&APIkey={api_key}&from={today}&to={one_week_from_today}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for item in data["result"]:
            match_date.append(item["event_date"])
            match_time.append(item["event_time"])
            match_stadium.append(item["event_stadium"])
            match_teams.append(f"{item['event_home_team']} VS {item['event_away_team']}")
        
        return match_teams, match_date, match_time, match_stadium
    else:
        print("Error:", response.status_code)

def fetch_random_dog_cat_fact():
    url = "https://random-dog-facts.p.rapidapi.com/"

    headers = {
        "X-RapidAPI-Key": "f35d6cc549msh5379362dc0450acp14361bjsn793713a82508",
        "X-RapidAPI-Host": "random-dog-facts.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    fact = response.json()
    if "fact" in fact:
        dog_fact = fact["fact"]
    else:
        dog_fact = fact.get("message", "Error retrieving dog fact.")

    url = "https://random-cat-fact.p.rapidapi.com/"

    headers = {
        "X-RapidAPI-Key": "f35d6cc549msh5379362dc0450acp14361bjsn793713a82508",
        "X-RapidAPI-Host": "random-cat-fact.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    fact = response.json()
    if "fact" in fact:
        cat_fact = fact["fact"]
    else:
        cat_fact = fact.get("message", "Error retrieving cat fact.")

    return dog_fact, cat_fact

def fetch_linkedIn_jobs():
    url = "https://linkedin-bulk-data-scraper.p.rapidapi.com/search_jobs"

    querystring = {"query":"internship","location":"Egypt","page":"1"}

    headers = {
        "X-RapidAPI-Key": "f35d6cc549msh5379362dc0450acp14361bjsn793713a82508",
        "X-RapidAPI-Host": "linkedin-bulk-data-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()

    for job in data["response"]["jobs"]:
        job_titles.append(job["title"])
        job_company.append(job["primaryDescription"])
        job_location.append(job["secondaryDescription"])

    with open('linkedin_response.json', 'w') as outfile:
        json.dump(data, outfile)

    return job_titles, job_company, job_location

def save_variables_to_file(exclude_imports=True):

    from types import ModuleType

    with open("variables.py", "w", encoding="utf-8") as file:

        for var_name, var_value in globals().items():
            if exclude_imports and isinstance(var_value, (type, ModuleType)) or var_name in ("threads", "thread"):
                continue  # Skip imported modules
            if not var_name.startswith('__') and not callable(var_value):
                file.write(f"{var_name} = {repr(var_value)}\n")

        print("# Generated file with variables and their values\n")

def send_variables_file():
    HOST = '127.0.0.1'
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        print("Server is listening for connections...")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection established with {client_address}")

            try:
                with open("variables.py", "rb") as file:
                    file_data = file.read()

                client_socket.sendall(file_data)
                print("File sent successfully to the client.")

                client_socket.close()

            except Exception as e:
                print(f"Error occurred while sending file: {e}")

if __name__ == "__main__":

    image_title, image_description = fetch_image_of_the_day()

    threads = [
        threading.Thread(target=fetch_weather_api),
        threading.Thread(target=fetch_twitter_api),
        threading.Thread(target=fetch_news_api),
        threading.Thread(target=fetch_forex_api),
        #threading.Thread(target=fetch_image_of_the_day),
        threading.Thread(target=fetch_random_dog_cat_fact),
        threading.Thread(target=fetch_football_api),
        threading.Thread(target=fetch_linkedIn_jobs),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    save_variables_to_file()
    send_variables_file()

    