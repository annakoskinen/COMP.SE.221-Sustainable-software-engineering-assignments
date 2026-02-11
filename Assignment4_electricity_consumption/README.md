Idea of application
-  The application creates a daily electricity consumption chart of a week containing the average
    and maximum values for each day. The consumption values are fetched from Fingrid API and the
    user can choose a start date and the data of the following week is collected. The chart is created as an image and saved to the project folder for viewing. 

API key
- Data is obtained from the Fingrid Open API and instructions for API key generation can be found
    from the site https://data.fingrid.fi/en/instructions.
- API key is added to .env file to a FINGRID_API_KEY variable.

Installation and running
- The required libraries that need to be installed can be found in requirements.txt.
- The application can be run with the command: 'python main.py'

An example run
- The application first prints some info about it
- Then start date is asked as an input from the user and the chart is saved as an image

"## Electricity consumption in Finland ##"
"# average and the highest value per day in a week from a chosen start date #"

Input start in format YYYY-MM-DD
Start date: 2026-02-01
Chart saved as electricity_consumption.png

![Example run chart](electricity_consumption.png)