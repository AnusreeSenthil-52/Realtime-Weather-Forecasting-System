from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

import requests
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import mean_squared_error
from datetime import datetime, timedelta
import pytz
import os

API_KEY = '3ca76942bb2502f8b1d6a69e204d4996'
BASE_URL = 'https://api.openweathermap.org/data/2.5/'


def get_current_weather(city):
    url = f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    return {
        'city': data['name'],
        'current_temp': round(data['main']['temp']),
        'feels_like': round(data['main']['feels_like']),
        'temp_min': round(data['main']['temp_min']),
        'temp_max': round(data['main']['temp_max']),
        'humidity': round(data['main']['humidity']),
        'description': data['weather'][0]['description'],
        'country': data['sys']['country'],
        'wind_gust_dir': data['wind']['deg'],
        'pressure': data['main']['pressure'],
        'Wind_Gust_Speed': data['wind']['speed'],
        'clouds': data['clouds']['all'],
        'visibility': data['visibility'],
    }

def get_forecast_weather(city):
    url = f"{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    forecast_list = data['list'][:5]  # next 5 intervals

    forecast_data = {}
    for i, item in enumerate(forecast_list, start=1):
        time_str = datetime.fromtimestamp(item['dt']).strftime('%I %p')
        forecast_data[f'time{i}'] = time_str
        forecast_data[f'temp{i}'] = round(item['main']['temp'])
        forecast_data[f'hum{i}'] = item['main']['humidity']

    return forecast_data


def read_historical_data(filename):
    df = pd.read_csv(filename)
    df = df.dropna()
    df = df.drop_duplicates()
    return df


def prepare_data(data):
    le = LabelEncoder()
    data['WindGustDir'] = le.fit_transform(data['WindGustDir'])
    data['RainTomorrow'] = le.fit_transform(data['RainTomorrow'])

    X = data[['MinTemp', 'MaxTemp', 'WindGustDir',
              'WindGustSpeed', 'Humidity', 'Pressure', 'Temp']]
    y = data['RainTomorrow']

    return X, y, le


def train_rain_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("Rain Model MSE:", mean_squared_error(y_test, y_pred))

    return model


def prepare_regression_data(data, feature):
    X, y = [], []

    for i in range(len(data) - 1):
        X.append(data[feature].iloc[i])
        y.append(data[feature].iloc[i + 1])

    return np.array(X).reshape(-1, 1), np.array(y)


def train_regression_model(X, y):
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model


def predict_future(model, current_value):
    predictions = [current_value]

    for _ in range(5):
        next_val = model.predict(np.array([[predictions[-1]]]))[0]
        predictions.append(next_val)

    return predictions[1:]


def weather_view(request):
    if request.method == 'POST':
        city = request.POST.get('city')
    else:
        city = "London"   # ✅ default city

    current_weather = get_current_weather(city)
    forecast_data = get_forecast_weather(city)

    csv_path = os.path.join(settings.BASE_DIR, 'weather.csv')
    historical_data = read_historical_data(csv_path)

    X, y, le = prepare_data(historical_data)
    rain_model = train_rain_model(X, y)

    rain_prediction = rain_model.predict(pd.DataFrame([{
        'MinTemp': current_weather['temp_min'],
        'MaxTemp': current_weather['temp_max'],
        'WindGustDir': 0,
        'WindGustSpeed': current_weather['Wind_Gust_Speed'],
        'Humidity': current_weather['humidity'],
        'Pressure': current_weather['pressure'],
        'Temp': current_weather['current_temp'],
    }]))[0]

    return render(request, 'weather.html', {
        'city': city,
        'country': current_weather['country'],
        'description': current_weather['description'],
        'current_temp': current_weather['current_temp'],
        'feels_like': current_weather['feels_like'],
        'humidity': current_weather['humidity'],
        'clouds': current_weather['clouds'],
        'pressure': current_weather['pressure'],
        'visibility': current_weather['visibility'],
        'wind': current_weather['Wind_Gust_Speed'],
        'MaxTemp': current_weather['temp_max'],
        'MinTemp': current_weather['temp_min'],
        'time': datetime.now().strftime('%d %b %Y, %I:%M %p'),
        **forecast_data,
    })
