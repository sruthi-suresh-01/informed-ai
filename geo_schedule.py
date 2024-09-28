import sqlite3
import time

import requests
import schedule


def get_zip_code(lat, lon, api_key):
    """Fetch zip code using OpenCage Geocoder API."""
    url = f"https://api.opencagedata.com/geocode/v1/json?q={lat}+{lon}&key={api_key}"
    response = requests.get(url).json()
    if response["results"]:
        return response["results"][0]["components"].get("postcode")
    else:
        return "Zip code not found"


def update_database(ip_address, geo_data, alerts):
    connection = sqlite3.connect("weather_alerts.db")
    cursor = connection.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY,
                        ip_address TEXT,
                        country TEXT,
                        city TEXT,
                        zip_code TEXT,
                        latitude REAL,
                        longitude REAL,
                        alerts_count INTEGER)"""
    )
    cursor.execute(
        """INSERT INTO alerts (ip_address, country, city, zip_code, latitude, longitude, alerts_count)
                      VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            ip_address,
            geo_data["country"],
            geo_data["city"],
            geo_data["zip"],
            geo_data["lat"],
            geo_data["lon"],
            len(alerts),
        ),
    )
    connection.commit()
    connection.close()


def update_alerts_file(ip_address, geo_data, alerts):
    with open("alerts.txt", "w") as file:
        file.write(f"IP Address: {ip_address}\n")
        file.write("Geographical Information:\n")
        file.write(f"  Country: {geo_data['country']}\n")
        file.write(f"  Country Code: {geo_data['countryCode']}\n")
        file.write(f"  Region: {geo_data['regionName']}\n")
        file.write(f"  City: {geo_data['city']}\n")
        file.write(f"  Zip Code: {geo_data['zip']}\n")
        file.write(f"  Latitude: {geo_data['lat']}\n")
        file.write(f"  Longitude: {geo_data['lon']}\n")
        file.write(f"  Timezone: {geo_data['timezone']}\n")
        file.write(f"  ISP: {geo_data['isp']}\n")
        file.write(f"  AS: {geo_data['as']}\n")
        file.write("\n")
        file.write("Alerts Details:\n")
        for alert in alerts:
            file.write(f"Headline: {alert['properties']['headline']}\n")
            file.write(f"Area: {alert['properties']['areaDesc']}\n")
            file.write(f"Description: {alert['properties']['description']}\n")
            file.write("\n")


def fetch_data():
    ip_address = requests.get("http://api.ipify.org").text
    geo_data = requests.get(f"http://ip-api.com/json/{ip_address}").json()
    lat, lon = geo_data["lat"], geo_data["lon"]
    zip_code = geo_data["zip"] or get_zip_code(
        lat, lon, "c7cca7e08657441a8b6de18c87f21a2f"
    )
    geo_data["zip"] = zip_code
    response = requests.get(f"https://api.weather.gov/alerts?point={lat},{lon}").json()
    alerts = response["features"]
    update_database(ip_address, geo_data, alerts)
    update_alerts_file(ip_address, geo_data, alerts)
    print("Database and alerts file updated successfully.")


# Schedule the job every 4 hours
schedule.every(4).hours.do(fetch_data)

# Run the scheduling in a loop
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute to run the scheduled task
