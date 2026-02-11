import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import numpy as np

def add_labels(x, y, pos):
    """
    Add labels to the bars in the bar chart
    
    :param x: x-axis data
    :param y: y-axis data
    :param pos: position of the label regards to the bar
    """
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha=pos)

def show_data(dates, avgs, max):
    """
    Generate bar chart for the data gathered and calculated from Fingrid API and save it as an image
    
    :param dates: Dates for which the data is shown
    :param avgs: Daily averages of the electricity consumption data
    :param max: Daily maximum values of the electricity consumption data 
    """
    fig = plt.subplots(figsize =(12, 8))

    # Width and size for x-axis and values for y-axis
    w, x = 0.4, np.arange(len(avgs))
    y = avgs
    y2 = max

    # Bars for both y-axis datasets, dates for the x-axis labels
    plt.bar(x - w/2, y, w, color='violet', edgecolor='white', label='Average')
    plt.bar(x + w/2, y2, w, color='grey', edgecolor='white', label='Maximum')
    plt.xticks(x, dates)

    # Adding the value labels to the bars
    add_labels(x, y, 'right')
    add_labels(x, y2, 'left')

    # Title and axis labels
    plt.title("Daily average and maximum electricity consumption (MWh/h) in a week")
    plt.ylabel("Electricity consumption (MWh/h)")
    plt.xlabel("Date")

    plt.legend()
    plt.savefig("electricity_consumption.png")
    print("Chart saved as electricity_consumption.png")