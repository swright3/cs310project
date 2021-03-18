import sqlite3
import datetime
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from predictions import predictPercentage, predictPercentageScaledByFollowers
import statistics
import math

def plotAllPolls():
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    c.execute('SELECT date,con,lab,libdem,green FROM polls')
    polls = c.fetchall()
    conn.close()
    dateList = []
    yValuesCon = []
    yValuesLab = []
    yValuesLibdem = []
    yValuesGreen = []
    xValues = []
    for poll in polls:
        dateList.append(poll[0])
        yValuesCon.append(int(poll[1]))
        yValuesLab.append(int(poll[2]))
        yValuesLibdem.append(int(poll[3]))
        yValuesGreen.append(int(poll[4]))
    for date in dateList:
        xValues.append(datetime.datetime.strptime(date,"%Y-%m-%d").date())

    ax = plt.gca()

    formatter = mdates.DateFormatter("%Y-%m-%d")

    ax.xaxis.set_major_formatter(formatter)

    locator = mdates.YearLocator()

    ax.xaxis.set_major_locator(locator)
    plt.gcf().autofmt_xdate()

    plt.scatter(xValues, yValuesCon, c='blue', s=2, label='Con')
    plt.scatter(xValues, yValuesLab, c='red', s=2, label='Lab')
    plt.scatter(xValues, yValuesLibdem, c='yellow', s=2, label='Lib Dem')
    plt.scatter(xValues, yValuesGreen, c='green', s=2, label='Green')
    plt.show()

def plotRealVsCalculated(party):
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    c.execute('SELECT date,'+party+' FROM polls WHERE id > ?;',(2304,))
    polls = c.fetchall()
    conn.close()
    realPercents = []
    dates = []
    for poll in polls:
        realPercents.append(int(poll[1]))
        dates.append(poll[0])
    predictedPercents, modelMetrics = predictPercentage(party,dates)
    calculateAccuracyMetrics(realPercents,predictedPercents,modelMetrics)
    xValues = []
    for date in dates:
        xValues.append(datetime.datetime.strptime(date,"%Y-%m-%d").date())

    ax = plt.gca()

    formatter = mdates.DateFormatter("%Y-%m-%d")

    ax.xaxis.set_major_formatter(formatter)

    locator = mdates.DayLocator()

    ax.xaxis.set_major_locator(locator)
    plt.gcf().autofmt_xdate()
    plt.xlabel('Date of Poll')
    plt.ylabel('Percentage Vote')
    plt.title('Real (blue) against predicted (red) results for the '+party+' party (linear regression model)')
    plt.scatter(xValues, realPercents, c='blue', s=3, label='Actual')
    plt.scatter(xValues, predictedPercents, c='red', s=3, label='Predicted')
    plt.legend(loc="best")
    plt.show()

def plotRealVsCalculatedScaledByFollowers(party):
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    c.execute('SELECT date,'+party+' FROM polls WHERE id > ?;',(2304,))
    polls = c.fetchall()
    conn.close()
    realPercents = []
    dates = []
    for poll in polls:
        realPercents.append(int(poll[1]))
        dates.append(poll[0])
    predictedPercents, modelMetrics = predictPercentageScaledByFollowers(party,dates)
    calculateAccuracyMetrics(realPercents,predictedPercents,modelMetrics)
    xValues = []
    for date in dates:
        xValues.append(datetime.datetime.strptime(date,"%Y-%m-%d").date())

    ax = plt.gca()

    formatter = mdates.DateFormatter("%Y-%m-%d")

    ax.xaxis.set_major_formatter(formatter)

    locator = mdates.DayLocator()

    ax.xaxis.set_major_locator(locator)
    plt.gcf().autofmt_xdate()
    plt.xlabel('Date of Poll')
    plt.ylabel('Percentage Vote')
    plt.title('Real (blue) against predicted (red) results for the '+party+' party, sentiments\nscaled by number of twitter followers of person who posted each tweet (linear regression model)')
    plt.scatter(xValues, realPercents, c='blue', s=3, label='Actual')
    plt.scatter(xValues, predictedPercents, c='red', s=3, label='Predicted')
    plt.legend(loc="best")
    plt.show()

def calculateAccuracyMetrics(realPercents,predictedPercents,modelMetrics):
    rSquared = modelMetrics[0]
    intercept = modelMetrics[1]
    slope = modelMetrics[2]
    absoluteErrors = []
    for value in range(len(realPercents)):
        absoluteErrors.append(abs(realPercents[value]-predictedPercents[value][0]))
    absoluteErrorsSquared = []
    for value in absoluteErrors:
        absoluteErrorsSquared.append(value**2)
    MSE = statistics.mean(absoluteErrorsSquared)
    RMSE = math.sqrt(MSE)
    MAE = statistics.mean(absoluteErrors)
    print('Model Accuracy Metrics')
    print('R Squared: ' + str(rSquared))
    print('Y Intercept: ' + str(intercept))
    print('Gradient of slope: ' + str(slope))
    print('Root Mean Squared Error: ' + str(RMSE))
    print('Mean Absolute Error: ' + str(MAE))

if __name__ == '__main__':
    plotRealVsCalculated('green')
    plotRealVsCalculatedScaledByFollowers('green')
    