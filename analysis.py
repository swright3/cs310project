import sqlite3
import datetime
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from predictions import predictPercentage, predictPercentageScaledByFollowers
import statistics
import math
import numpy as np

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

def plotRealVsCalculated(party,polynomial,degree):
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
    predictedPercents, modelMetrics = predictPercentage(party,dates,polynomial,degree)
    calculateAccuracyMetrics(realPercents,predictedPercents,modelMetrics,polynomial)
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
    plt.title('Real (blue) against predicted (red) results for the '+party+' party (polynomial regression model order 3)')
    plt.scatter(xValues, realPercents, c='blue', s=3, label='Actual')
    plt.scatter(xValues, predictedPercents, c='red', s=3, label='Predicted')
    plt.legend(loc="best")
    plt.show()

def plotRealVsCalculatedScaledByFollowers(party,polynomial,degree):
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
    predictedPercents, modelMetrics = predictPercentageScaledByFollowers(party,dates,polynomial,degree)
    calculateAccuracyMetrics(realPercents,predictedPercents,modelMetrics,polynomial)
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
    plt.title('Real (blue) against predicted (red) results for the '+party+' party, sentiments\nscaled by number of twitter followers of person who posted each tweet (polynomial regression model order 3)')
    plt.scatter(xValues, realPercents, c='blue', s=3, label='Actual')
    plt.scatter(xValues, predictedPercents, c='red', s=3, label='Predicted')
    plt.legend(loc="best")
    plt.show()

def calculateAccuracyMetrics(realPercents,predictedPercents,modelMetrics,polynomial):
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
    if not polynomial:
        print('Gradient of slope: ' + str(slope))
    else:
        print('Coefficients: ' + str(slope))
    print('Root Mean Squared Error: ' + str(RMSE))
    print('Mean Absolute Error: ' + str(MAE))

def plotRegressionModels():
    xValues = [8.98608108,3.32517432,5.13626997,8.02841886,7.3368986,7.3368986]
    yValues = [45,42,45,43,45,43]
    x1 = np.linspace(-1,10,140)
    x2 = np.linspace(-1,10,140)
    x3 = np.linspace(-1,10,140)
    y1 = 0.2835592280798959*x1 + 41.935861719529356
    y2 = -0.10235748825451998*(x2**2) + 1.526133790624896*x2 + 38.57347458990624
    y3 = 0.16576495*(x3**3) - 3.21396146*(x3**2) + 19.90218758*x3 + 5.233629073170825

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.spines['left'].set_position(('data', 0))
    ax.spines['bottom'].set_position('center')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.xlabel('(sum of sentiments/number of tweets)*100')
    plt.ylabel('Percentage Vote')
    plt.title('Regression model for the con party')

    plt.scatter(xValues, yValues, c='blue', s=5, label='Samples')
    plt.plot(x1,y1,label='Linear model')
    plt.plot(x2,y2,label='Polynomial model (order 2)')
    plt.plot(x3,y3,label='Polynomial model (order 3)')
    ax.legend(loc='lower center',fancybox=True, shadow=True, ncol=2)
    plt.show()

if __name__ == '__main__':
    plotRealVsCalculated('libdem',True,2)
    #plotRealVsCalculatedScaledByFollowers('con',True,2)
    #plotRegressionModels()
    