

import asyncio
import math
import aiohttp
import pandas as pd
import re

HOST = "https://bt2stag.boataround.com" #Website URL
HOST_API = "https://stag-api.boataround.com" #Api
FILTER_LOCATION = "split"
CHECK_IN = ""
CHECK_OUT = ""


def extractBoatDataJSON(boats, city, check_in, check_out):
    boat_info = []
    for boat in boats:
        if re.search(city,boat.get('city', '').lower(), re.IGNORECASE) :
            print("Location: ", boat.get('city'))
            charter_name = boat.get('charter', 'Unknown')
            boat_name = boat.get('title', 'Unknown')
            boat_length = boat.get('parameters', {}).get('length', 'Unknown')
            price_eur = boat.get('price', 0)

            boat_info.append({
                'Charter Name': charter_name,
                'Boat Name': boat_name,
                'Boat Length': str(boat_length) + " m",
                'Price in EUR': price_eur,
                'Check-In': check_in,
                'Check-Out': check_out
            })

    return boat_info
async def fetchDataApi(check_in, check_out, session, currency="EUR", page=1, location="split-1"):
    URI = f"{HOST_API}/v1/search?destinations={location}&page={{}}&checkIn={check_in}&checkOut={check_out}&lang=en_EN&sort=rank&currency={currency}&loggedIn=0&ab=20231127_1"
    boatDataJSON = []
    task = await session.get(f"{URI.format(1)}")
    boatDataJSON.append(await task.json())
    pages = math.ceil(boatDataJSON[-1]["data"][0]["totalBoats"]) // int(boatDataJSON[-1]["data"][0]["totalResults"])
    # List to store the final data
    searchItemDetails = []
    # Requesting Data from the HOST
    for i in range(2,pages):

        print(URI.format(i))
        task = await session.get(f"{URI.format(i)}")
        boatDataJSON.append(await task.json())
    dataBoats = []
    for data in boatDataJSON:
        print("Processing...")
        dataBoats += extractBoatDataJSON(data["data"][0]["data"],FILTER_LOCATION, check_in, check_out)
    return dataBoats

async def processData():

    from datetime import datetime, timedelta

    # Define the start and end dates
    start_date = datetime(2024, 5, 1)
    end_date = datetime(2024, 9, 30)

    # Function to find the next Saturday from a given date
    def nextSaturday(date):
        return date + timedelta(days=(5 - date.weekday() + 7) % 7)

    # Find the first Saturday in the range
    first_saturday = nextSaturday(start_date)

    # Generate all Saturdays between the start and end dates
    saturdays = []
    current_saturday = first_saturday
    while current_saturday <= end_date:
        saturdays.append(current_saturday.strftime("%Y-%m-%d"))
        current_saturday += timedelta(days=7)
    boatData = []
    session = aiohttp.ClientSession()
    for date in range(0, len(saturdays), 2):
        boatData += await fetchDataApi(saturdays[date], saturdays[date+1], session=session)
    boatDataPD = pd.DataFrame(boatData)
    with pd.ExcelWriter("boatData.xlsx", mode="w") as file:
        boatDataPD.to_excel(file)
    await session.close()
if __name__ == '__main__':
    asyncio.run(processData())