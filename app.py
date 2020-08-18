from flask import Flask, request, jsonify
import requests as http
import csv
from io import StringIO
import datetime

from lib.countries import countries
from lib.date import getDate

app = Flask(__name__)

base_url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_daily_reports/"


def get_data(b_url, date):
    url = b_url + date + ".csv"
    res = http.get(url)

    if not res.ok:
        return None

    data = res.content.decode("ascii", "ignore")
    return StringIO(data)


def get_cases(url, date, countries):
    data = get_data(url, date)
    reader = csv.reader(data)
    cases = []

    if data is None:
        return None

    for row in reader:
        if row[0] == "FIPS":
            continue
        if row[3] in countries:
            cases.append(
                {
                    "UpdatedOn": row[4].split(" ")[0],
                    "Country": row[3],
                    "Confirmed": row[7],
                    "Deaths": row[8],
                    "Recoveries": row[9],
                    "Active": row[10],
                }
            )
    return cases


def get_case(url, date, country):
    data = get_data(url, date)

    if country.capitalize() not in countries or data is None:
        return None

    reader = csv.reader(data)

    for row in reader:
        if row[0] == "FIPS":
            continue
        if row[3].lower() == country.lower():
            return {
                "UpdatedOn": row[4].split(" ")[0],
                "Country": row[3],
                "Confirmed": row[7],
                "Deaths": row[8],
                "Recoveries": row[9],
                "Active": row[10],
            }
    return None


@app.route("/")
def index():
    country = request.args.get("country")
    date = request.args.get("date")

    if date is None and country is None:
        cases = get_cases(base_url, getDate(), countries)
        return {"cases": cases}

    if country is None and date is not None:
        cases = get_cases(base_url, date, countries)
        return {"cases": cases}

    if country is not None and date is None:
        case = get_case(base_url, getDate(), country)
        if case is None:
            res = jsonify({"error message": "country not found"})
            res.status_code = 404
            return res
        return {"case": case}

    case = get_case(base_url, date, country)
    if case is None:
        res = jsonify({"error message": "data not found"})
        res.status_code = 404
        return res
    return {"case": case}


if __name__ == "__main__":
    app.run(debug=True)
