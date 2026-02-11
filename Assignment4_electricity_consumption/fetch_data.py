import os
import requests
from dotenv import load_dotenv

def get_data(startDate, endDate):
    """
    Fetches electricity consumption data from the Fingrid API and adds the data to a dict
    
    :param startDate: Date from which data collection starts
    :param endDate: Date where data collection ends
    """
    # Get the API key from the .env file and add it to headers
    load_dotenv()
    API_key = os.getenv('FINGRID_API_KEY')
    headers = {'x-api-key': API_key}

    # Create url for API call
    start_time = startDate + 'T00:00:00.000Z'
    end_time = endDate + 'T00:00:00.000Z'
    url = 'https://data.fingrid.fi/api/datasets/124/data?startTime=' + start_time + '&endTime=' + end_time + '&sortOrder=asc&pageSize=5000'
    
    electricity_data = {}
    dateValue = {}

    # Try to get data from the API and catch exceptions
    try:
        response = requests.get(url, headers=headers)

        # Check that the response was successful
        if response.status_code == 200:
            # Get the response in JSON format
            data = response.json()
            dataset = data.get('data')

            # Loop through the data and extract the date and electricity consumption value
            for data_values in dataset:
                date = data_values.get('startTime')[:10]
                value = data_values.get('value')

                # Add date and value into electricity_data
                if (date not in electricity_data):
                    electricity_data[date] = []
                
                electricity_data[date].append(value)

            return electricity_data
        
        # If not successful, print error
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None
    
def modify_data(data):
    '''
    Modify the fetched data by calculating the daily averages and maximum values.
    
    :param data: Electricity consumption data fetched from the API
    '''
    # Initialize lists for values
    averages, dates, maxValues = [], [], []

    # Count the average and max value for each date and append the current date
    for values in data:
        dates.append(values)

        avg = round(sum(data[values]) / len(data[values]),2)
        averages.append(avg)

        maxVal = round(max(data[values]),2)
        maxValues.append(maxVal)

    return dates, averages, maxValues
