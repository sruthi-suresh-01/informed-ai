import json
import time
from typing import Any
import requests
import schedule


def get_weather_alerts(zone_id: str) -> Any:
    """Fetch weather alerts using latitude and longitude."""
    url = f"https://api.weather.gov/alerts/active/zone/{zone_id}"
    response = requests.get(url).json()

    if "features" in response:
        return response["features"]
    else:
        return []


def extract_alert_info(alert_features: list) -> list:
    # Compile pattern to extract sentences
    allowed_keys = ["event", "headline", "description", "instruction"]
    extracted_features = []
    for feature in alert_features:
        filtered_alert_info = {
            key: feature["properties"][key]
            for key in allowed_keys
            if key in feature["properties"]
        }
        extracted_features.append(filtered_alert_info)
    return extracted_features


def storeAlertsInDB(zip: str, features: list) -> None:
    url = "http://localhost:8000/weather/add"
    data = {"zip_code": zip, "weather_conditions": json.dumps(features)}

    headers = {
        "Content-Type": "application/json",
        "Cookie": "session_token=86mnYqBfx_34Cuy2dqC1JVmr4Y6tzrryDpnXfsSQrug",
    }

    response = requests.post(url, json=data, headers=headers).json()

    print(response)


def main(zip_zones: dict) -> None:
    alerts_by_zip = {}
    for zip, zone in zip_zones.items():

        alert = get_weather_alerts(zone)
        extracted_features = extract_alert_info(alert)
        alerts_by_zip[zip] = extracted_features
        if len(extracted_features) > 0:
            print(zip)
            storeAlertsInDB(zip, extracted_features)

    print("Alerts stored successfully.")


zip_zones = {
    "92507": "CAZ065",
    "91701": "CAZ560",
    "91708": "CAZ560",
    "91709": "CAZ560",
    "91710": "CAZ560",
    "91729": "CAZ560",
    "91730": "CAZ560",
    "91737": "CAZ560",
    "91739": "CAZ560",
    "91743": "CAZ560",
    "91758": "CAZ560",
    "91759": "CAZ560",
    "91761": "CAZ560",
    "91762": "CAZ560",
    "91763": "CAZ560",
    "91764": "CAZ560",
    "91784": "CAZ560",
    "91785": "CAZ560",
    "91786": "CAZ560",
    "91798": "CAZ560",
    "92242": "CAZ560",
    "92252": "CAZ560",
    "92256": "CAZ560",
    "92267": "CAZ560",
    "92268": "CAZ560",
    "92277": "CAZ560",
    "92278": "CAZ560",
    "92280": "CAZ560",
    "92284": "CAZ560",
    "92285": "CAZ560",
    "92286": "CAZ560",
    "92301": "CAZ560",
    "92304": "CAZ560",
    "92305": "CAZ560",
    "92307": "CAZ560",
    "92308": "CAZ560",
    "92309": "CAZ560",
    "92310": "CAZ560",
    "92311": "CAZ560",
    "92312": "CAZ560",
    "92313": "CAZ560",
    "92314": "CAZ560",
    "92315": "CAZ560",
    "92316": "CAZ560",
    "92317": "CAZ560",
    "92318": "CAZ560",
    "92321": "CAZ560",
    "92322": "CAZ560",
    "92323": "CAZ560",
    "92324": "CAZ560",
    "92325": "CAZ560",
    "92326": "CAZ560",
    "92327": "CAZ560",
    "92329": "CAZ560",
    "92331": "CAZ560",
    "92332": "CAZ560",
    "92333": "CAZ560",
    "92334": "CAZ560",
    "92335": "CAZ560",
    "92336": "CAZ560",
    "92337": "CAZ560",
    "92338": "CAZ560",
    "92339": "CAZ560",
    "92340": "CAZ560",
    "92341": "CAZ560",
    "92342": "CAZ560",
    "92344": "CAZ560",
    "92345": "CAZ560",
    "92346": "CAZ560",
    "92347": "CAZ560",
    "92350": "CAZ560",
    "92352": "CAZ560",
    "92354": "CAZ560",
    "92356": "CAZ560",
    "92357": "CAZ560",
    "92358": "CAZ560",
    "92359": "CAZ560",
    "92363": "CAZ560",
    "92364": "CAZ560",
    "92365": "CAZ560",
    "92366": "CAZ560",
    "92368": "CAZ560",
    "92369": "CAZ560",
    "92371": "CAZ560",
    "92372": "CAZ560",
    "92373": "CAZ560",
    "92374": "CAZ560",
    "92375": "CAZ560",
    "92376": "CAZ560",
    "92377": "CAZ560",
    "92378": "CAZ560",
    "92382": "CAZ560",
    "92385": "CAZ560",
    "92386": "CAZ560",
    "92391": "CAZ560",
    "92392": "CAZ560",
    "92393": "CAZ560",
    "92394": "CAZ560",
    "92395": "CAZ560",
    "92397": "CAZ560",
    "92398": "CAZ560",
    "92399": "CAZ560",
    "92401": "CAZ560",
    "92402": "CAZ560",
    "92403": "CAZ560",
    "92404": "CAZ560",
    "92405": "CAZ560",
    "92406": "CAZ560",
    "92407": "CAZ560",
    "92408": "CAZ560",
    "92410": "CAZ560",
    "92411": "CAZ560",
    "92412": "CAZ560",
    "92413": "CAZ560",
    "92414": "CAZ560",
    "92415": "CAZ560",
    "92418": "CAZ560",
    "92423": "CAZ560",
    "92424": "CAZ560",
    "92427": "CAZ560",
    "93558": "CAZ560",
    "93562": "CAZ560",
    "92222": "CAZ562",
    "92227": "CAZ562",
    "92231": "CAZ562",
    "92232": "CAZ562",
    "92233": "CAZ562",
    "92243": "CAZ562",
    "92244": "CAZ562",
    "92249": "CAZ562",
    "92250": "CAZ562",
    "92251": "CAZ562",
    "92257": "CAZ562",
    "92259": "CAZ562",
    "92266": "CAZ562",
    "92273": "CAZ562",
    "92275": "CAZ562",
    "92281": "CAZ562",
    "92283": "CAZ562",
    "91752": "CAZ563",
    "92201": "CAZ563",
    "92202": "CAZ563",
    "92203": "CAZ563",
    "92210": "CAZ563",
    "92211": "CAZ563",
    "92220": "CAZ563",
    "92223": "CAZ563",
    "92225": "CAZ563",
    "92226": "CAZ563",
    "92230": "CAZ563",
    "92234": "CAZ563",
    "92235": "CAZ563",
    "92236": "CAZ563",
    "92239": "CAZ563",
    "92240": "CAZ563",
    "92241": "CAZ563",
    "92247": "CAZ563",
    "92248": "CAZ563",
    "92253": "CAZ563",
    "92254": "CAZ563",
    "92255": "CAZ563",
    "92258": "CAZ563",
    "92260": "CAZ563",
    "92261": "CAZ563",
    "92262": "CAZ563",
    "92263": "CAZ563",
    "92264": "CAZ563",
    "92270": "CAZ563",
    "92274": "CAZ563",
    "92276": "CAZ563",
    "92282": "CAZ563",
    "92292": "CAZ563",
    "92320": "CAZ563",
    "92501": "CAZ563",
    "92502": "CAZ563",
    "92503": "CAZ563",
    "92504": "CAZ563",
    "92505": "CAZ563",
    "92506": "CAZ563",
    "92508": "CAZ563",
    "92509": "CAZ563",
    "92513": "CAZ563",
    "92514": "CAZ563",
    "92515": "CAZ563",
    "92516": "CAZ563",
    "92517": "CAZ563",
    "92518": "CAZ563",
    "92519": "CAZ563",
    "92521": "CAZ563",
    "92522": "CAZ563",
    "92530": "CAZ563",
    "92531": "CAZ563",
    "92532": "CAZ563",
    "92536": "CAZ563",
    "92539": "CAZ563",
    "92543": "CAZ563",
    "92544": "CAZ563",
    "92545": "CAZ563",
    "92546": "CAZ563",
    "92548": "CAZ563",
    "92549": "CAZ563",
    "92551": "CAZ563",
    "92552": "CAZ563",
    "92553": "CAZ563",
    "92554": "CAZ563",
    "92555": "CAZ563",
    "92556": "CAZ563",
    "92557": "CAZ563",
    "92561": "CAZ563",
    "92562": "CAZ563",
    "92563": "CAZ563",
    "92564": "CAZ563",
    "92567": "CAZ563",
    "92570": "CAZ563",
    "92571": "CAZ563",
    "92572": "CAZ563",
    "92581": "CAZ563",
    "92582": "CAZ563",
    "92583": "CAZ563",
    "92584": "CAZ563",
    "92585": "CAZ563",
    "92586": "CAZ563",
    "92587": "CAZ563",
    "92589": "CAZ563",
    "92590": "CAZ563",
    "92591": "CAZ563",
    "92592": "CAZ563",
    "92593": "CAZ563",
    "92595": "CAZ563",
    "92596": "CAZ563",
    "92599": "CAZ563",
    "92860": "CAZ563",
    "92877": "CAZ563",
    "92878": "CAZ563",
    "92879": "CAZ563",
    "92880": "CAZ563",
    "92881": "CAZ563",
    "92882": "CAZ563",
    "92883": "CAZ563",
}

file_path = "zip_zone.json"
with open(file_path) as json_file:
    data = json.load(json_file)

main(data)
# Schedule the job every 4 hours
schedule.every(4).hours.do(main, zip_zones)

# Run the scheduling in a loop
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute to run the scheduled task
