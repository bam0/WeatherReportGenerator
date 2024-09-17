# by Brian Mann

import json
import requests
import sys

# URLs
_wthr = "https://api.openweathermap.org/data/2.5/weather"
_dir = "http://api.openweathermap.org/geo/1.0/direct"
_zip = "http://api.openweathermap.org/geo/1.0/zip"
# API key
_api_key = "insert_key_here"

# This function checks that the request to the url is successful and returns a boolean value
def check_request(url, parameters):
    try:
        requests.get(url, params=parameters, timeout=5)
        # if successful, return True
        return True
    # catch exceptions from most to least specific
    except requests.exceptions.HTTPError as http_err:
        print("Http Error:", http_err)
    except requests.exceptions.ConnectionError as conn_err:
        print("Error Connecting:", conn_err)
    except requests.exceptions.Timeout as time_err:
        print("Timeout Error:", time_err)
    except requests.exceptions.RequestException as err:
        print("Something else has gone wrong:", err)
    # if there is an error, return False
    return False

# This function asks the user if they would like to continue using the program
# If they would, it returns nothing. If they would not, it exits the program
def keep_going():
    choice = input("Would you like to continue using the program? (y/n)\n").strip().lower()
    while choice not in ["y", "n"]:
        choice = input("Error: Enter \'y\' for yes or \'n\' for no.\n").strip().lower()
    if choice == "y":
        return
    else:
        print("Thank you for using the program!")
        sys.exit()

# This function gathers a city and state entered by the user and returns them
def get_city_state():
    city = input("Please enter the city:\n").strip().capitalize()
    state = input("In which state is the city located?\n").strip().capitalize()
    return city, state

# This function returns a zip code entered by the user
def get_zip_code():
    zip_code = input("Please enter the zip code:\n").strip()
    while True:
        try:
            zip_code = int(zip_code)
        except ValueError:
            # if the input is not numeric, tell the user
            zip_code = input("Error: Please enter a numeric value.\n").strip()
            continue
        # also check that the zip code is five digits long
        if zip_code < 10000 or zip_code > 99999:
            zip_code = input("Error: Invalid zip code. Please enter a 5-digit number.\n").strip()
            continue
        break
    return zip_code

# This function asks the user which temperature units to use throughout the program
def get_units():
    # make a dictionary of the three choices the units could be, as provided by the API
    units = {"1": "standard", "2": "metric", "3": "imperial"}
    choice = input("How would you like temperature to be displayed?\n"
                   + "\'1\' Kelvin. \'2\' Celsius. \'3\' Fahrenheit\n").strip()
    while choice not in ["1", "2", "3"]:
        choice = input("Error: Please enter a number from 1-3.\n").strip()
    return units[choice]

# This function takes in the latitude, longitude and units of temperature and returns
# the weather data retrieved by the API.
def get_weather_data(lat, lon, units):
    parameters = {"lat": lat, "lon": lon, "appid": _api_key, "units": units}
    # first check if the connection was successful
    is_successful = check_request(_wthr, parameters)
    # if it is, return the data
    if is_successful:
        wthr_req = requests.get(_wthr, parameters)
        return json.loads(wthr_req.text)
    # otherwise, tell the user there was an error
    else:
        print("Error: Data retrieval unsuccessful.")
        return None

# This function takes in a city and state and returns the corresponding latitude and longitude
# of that location.
def city_state_to_coords(city, state):
    parameters = {"q": f"{city},{state},us", "appid": _api_key}
    # here, we again check to make sure the connection was successful
    is_successful = check_request(_dir, parameters)
    if is_successful:
        geo_req = requests.get(_dir, params=parameters)
        geo_data = json.loads(geo_req.text)
        # check that the given data was actually retrieved. return None if it is not.
        if len(geo_data) == 0:
            print("Error: Unable to retrieve data based on city and state entered.\n")
            return None
        # extract the dictionary from the given list
        geo_data = geo_data[0]
        # return the latitude and longitude
        return geo_data["lat"], geo_data["lon"]
    else:
        # tell the user if there was an issue
        print("Error: Unable to retrieve data based on city and state entered.\n")
        return None

# This function takes in a zip code and returns the corresponding latitude and longitude
def zip_to_coords(zip_code):
    parameters = {"zip": f"{zip_code},US", "appid": _api_key}
    is_successful = check_request(_zip, parameters)
    if is_successful:
        geo_req = requests.get(_zip, params=parameters)
        geo_data = json.loads(geo_req.text)
        # check if the result contains the desired data
        if "lat" not in geo_data:
            print("Error: Unable to retrieve data based on zip code entered.\n")
            return None
        # if successful, return the latitude and longitude
        return geo_data["lat"], geo_data["lon"]
    else:
        print("Error: Unable to retrieve data based on zip code entered.\n")
        return None

# This function takes in json weather data and prints some of the information
# in a report easily readable by the user.
def generate_report(data):
    # store the desired pieces of weather data in variables
    loc, desc = data["name"], data["weather"][0]["description"]
    t_curr, t_feels = data["main"]["temp"], data["main"]["feels_like"]
    t_min, t_max = data["main"]["temp_min"], data["main"]["temp_max"]
    pres, humi, clds = data["main"]["pressure"], data["main"]["humidity"], data["clouds"]["all"]
    # print the result in the form of a report
    print("\n" + "*"*50)
    print(f"Current Weather in {loc}")
    print("-"*50)
    print(f"There is currently {desc} with {clds}% cloud coverage.\n"
          + f"The current temperature is {t_curr}, and it feels like {t_feels}.\n"
          + f"Today's high is {t_max}, with a low of {t_min}.\n"
          + f"Humidity is {humi}%, and the current outside pressure is {pres} hPa.")
    print("*"*50 + "\n")

# This function asks the user for locations and returns the corresponding weather report
def main():
    # welcome the user and explain the program
    print("Welcome to the weather app!\n"
          + "This app will give you current U.S. weather data based on the locations you provide.\n"
          + "You can search by city and state, or by zip code.\n"
          + "Simply follow the prompts below.\n")
    # determine the units of temperature for each report
    print("First off, let us know your preferred unit of temperature.\n")
    units = get_units()
    # use a loop to allow the user to input multiple locations before exiting the program
    while True:
        choice = input("Where would you like to know the weather?\n"
                       + "\'1\' Enter a city & state. \'2\' Enter a zip code. \'3\' Exit the program\n").strip()
        while choice not in ["1", "2", "3"]:
            choice = input("Error: Please enter a number from 1-3.\n").strip()
        # allow the user to exit the program
        if choice == "3":
            print("Thank you for using the program!")
            sys.exit()
        # define a variable for the coordinates
        coords = (0, 0)
        # generate coordinates based on city and state
        if choice == "1":
            city, state = get_city_state()
            coords = city_state_to_coords(city, state)
            # if no data is collectd, continue
            if coords is None:
                continue
        # generate coordinates based on zip code
        if choice == "2":
            zip_code = get_zip_code()
            coords = zip_to_coords(zip_code)
            # again, if there is no data, continue to another iteration of the loop
            if coords is None:
                continue
        # get the weather data and generate a report
        wthr_data = get_weather_data(*coords, units)
        generate_report(wthr_data)
        # ask the user if they would like to continue using the program
        keep_going()

# This calls the function 'main' and runs the program
if __name__ == "__main__":
    main()
