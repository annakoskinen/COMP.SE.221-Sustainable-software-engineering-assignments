from datetime import datetime
from datetime import timedelta
from fetch_data import get_data, modify_data
from create_chart import show_data

def get_dates():
    '''
    Get the starting date for data collection from user and based on it calculate the end date
    '''
    startDate = ""
    endDate = ""
    today = datetime.now()

    print("Input start in format YYYY-MM-DD")
    while True:
        start = input("Start date: ")

        # Try to transform input into datetime to check that the date is valid
        # and handle ValueError exception if input is invalid
        try: 
            startDate = datetime.fromisoformat(start)

            # Check that the starting date is not after the current date
            if(startDate > today):
                print("Error: start date can't be after the current date")
            else:
                # Calculate end date to be a week from start date
                endDate = startDate + timedelta(7)
                end = f"{endDate}"[:10]
                break
        except ValueError:
            print("Error: Invalid date")

    return start, end


def main():
    '''
    Get date range for data collection, fetch data from API and generate an chart from it
    '''

    # Starting info for user
    print("\n## Electricity consumption in Finland ##" \
        "\n# average and the highest value per day in a week from a chosen start date #\n")
    
    # Get dates
    start_date, end_date = get_dates()

    # Fetch data and if available create chart
    data = get_data(start_date, end_date)
    if data:
        dates, avgList, maxValues = modify_data(data)
        show_data(dates, avgList, maxValues)
    else:
        print('Failed to fetch electricity consumption data from Fingrid API.')

if __name__ == '__main__':
    main()