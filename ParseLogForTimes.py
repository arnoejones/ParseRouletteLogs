# -----------------------------------------------------------------------
# <copyright file = "ParseLogForTimes.py" company = "IGT">
#     Copyright © 2019 IGT.  All rights reserved.
# </copyright>
# -----------------------------------------------------------------------

import os
import re
import pandas as pd
from datetime import datetime
import PySimpleGUI as sg
import numpy as np

# sample line for the following regex to match: Log Entry : 9:50:13 AM 09:50:13.902
pattern = r"([0-9]+:[0-9]+:[0-9]+.[0-9]+)|(\d+(/|-){1}\d+(/|-){1}\d{2,4}|([0-9]+:[0-9]+:[0-9]+\s[A|P]M))"

max_seconds = ''
min_seconds = ''
sum_elapsed = ''
mean_seconds = ''
std_deviation = ''
cnt_samples = ''

timeFormat = '%H:%M:%S.%f'

time_differences = []

files_read = []


def create_empty_folder(folder_name):
    if not os.path.exists(folder_name):
        print("creating", folder_name)
        os.makedirs(folder_name)


outliers = []


def detect_outlier(data_1, date, time):
    threshold = 3
    mean_1 = np.mean(data_1)
    std_1 = np.std(data_1)

    for y in data_1:
        z_score = (y - mean_1) / std_1
        if np.abs(z_score) > threshold:
            outliers.append(y)
    return outliers


def load_engine(raw_logs_location, logs_results_location):
    # for filename in os.listdir(raw_logs_location):
    files = (file for file in os.listdir(raw_logs_location) if os.path.isfile(os.path.join(raw_logs_location, file)))
    for filename in files:
        files_read.append(filename)
        print(filename)
        old = '00:00:00.000'
        temp_list = []
        with open(raw_logs_location + '/' + filename) as f:
            fileContents = f.read()
            counter = 0
            matches = re.findall(pattern, fileContents, re.MULTILINE)

            for matchNum, match in enumerate(matches):
                log_entry_date = matches[counter + 0][1]
                log_entry_time = matches[counter + 1][1]
                game_event_timestamp = matches[counter + 2][0]

                new = game_event_timestamp
                deltaT = datetime.strptime(new, timeFormat) - datetime.strptime(old, timeFormat)

                deltaTinSeconds = deltaT.total_seconds()

                old = new
                temp_list.append([filename, log_entry_date, log_entry_time, deltaTinSeconds])

                if matchNum < len(matches) / 3 - 1:  # 3 elements per match -1 for index out of range
                    counter += 3
                else:
                    for i in range(2):
                        try:
                            temp_list.pop(
                                0)  # delete the entry that subtracts current time from 0, as that's meaningless.
                        except IndexError:
                            print("Not enough game states to calculate (requires at least 2 complete game cycles.)")
                    break
            time_differences.append(temp_list)

    df = pd.DataFrame(item for sublist in time_differences for item in sublist)  # convert list of lists into dataframe

    df.columns = ['Client EGM', 'Log Entry Date', 'Log Entry Time', 'Elapsed Time']

    # find and print the outliers
    outlier_datapoints = detect_outlier(df['Elapsed Time'], df['Log Entry Time'], df['Log Entry Date'])
    print('Outliers: ', outlier_datapoints)

    # find the outliers and remove them from the dataset
    df2 = df[np.abs(df['Elapsed Time'] - df['Elapsed Time'].mean()) <= (3 * df['Elapsed Time'].std())]

    global max_seconds
    global min_seconds
    global sum_elapsed
    global mean_seconds
    global std_deviation
    global cnt_samples

    max_seconds = float("{0:.2f}".format(df2['Elapsed Time'].max()))
    min_seconds = float("{0:.2f}".format(df2['Elapsed Time'].min()))
    sum_elapsed = float("{0:.2f}".format(df2['Elapsed Time'].sum()))
    mean_seconds = float("{0:.2f}".format(df2['Elapsed Time'].mean()))
    std_deviation = float("{0:.2f}".format(df2['Elapsed Time'].std()))
    cnt_samples = float("{0:.2f}".format(df2['Elapsed Time'].count()))

    print('MAX seconds', df2['Elapsed Time'].max())
    print('MIN seconds', df2['Elapsed Time'].min())
    print('SUM of all seconds', float("{0:.2f}".format(df2['Elapsed Time'].sum())))
    print('MEAN time of the delta Ts', float("{0:.2f}".format(df2['Elapsed Time'].mean())))
    print('STANDARD DEVIATION ', float("{0:.2f}".format(df2['Elapsed Time'].std())))
    print('COUNT of samples', df2['Elapsed Time'].count())

    current_time = str(datetime.now().date())

    # --- write to summary file --- #
    # see if dir exists.  if not, create it.
    create_empty_folder(logs_results_location)

    with open(logs_results_location + '\\' + current_time + '_RouletteStats.txt', 'w+') as f:
        f.writelines(str(len(files_read)) + ' log files read.' + '\r\n\r\n')
        f.write('MAX seconds: ' + str(df2['Elapsed Time'].max()) + '\r\n')
        f.write('MIN seconds: ' + str(df2['Elapsed Time'].min()) + '\r\n')
        f.write('SUM of all elapsed times: ' + str(df2['Elapsed Time'].sum()) + '\r\n')
        f.write('MEAN seconds: ' + str(df2['Elapsed Time'].mean()) + '\r\n')
        f.write('STANDARD DEVIATION: ' + str(df2['Elapsed Time'].std()) + '\r\n')
        f.write('COUNT of all samples: ' + str(df2['Elapsed Time'].count()) + '\r\n')
        f.write('\r\n')
        for file in files_read:
            f.write('Log file read: ' + file + '\r\n')

    # --- write to a csv log --- #
    if not os.path.exists(logs_results_location):
        os.makedirs(logs_results_location)

    df2.to_csv(logs_results_location + '\\' + current_time + '_LogsReport.csv')


# https://pysimplegui.readthedocs.io/#how-do-i
layout = [
    [sg.Text('Generate Statistics From Roulette Client Simulator', size=(45, 1), font=("Helvetica", 20),
             text_color='blue')],
    # [sg.Text('IP Address of target Roulette server:', size=(35, 1)), sg.InputText('10.213.133.65', key='_IP_', do_not_clear=True)],
    # [sg.Text('Port address of Roulette server:', size=(35, 1)), sg.InputText('4456', key='_PORT_', do_not_clear=True)],
    [sg.Text('Logs location, full path:', size=(40, 1)),
     sg.InputText(r'\\USNVR-W1005006\PublicShare\RouletteLogs', key='_LOGSDEST_', do_not_clear=True)],
    [sg.Text('Statistics and csv file destination:', size=(40, 1)),
     sg.InputText(r'\\USNVR-W1005006\PublicShare\RouletteLogsCSV', key='_CSVDEST_', do_not_clear=True)],
    # [sg.Text('How many processes to launch: ', size=(35, 1)), sg.InputText('4', key='_NUMOFPROCS_', do_not_clear=True)],
    [sg.Text('Statistics summary: ', size=(35, 1)), sg.Multiline(key='_SUMMARY_', size=(55, 6))],
    [sg.Submit('Create Stats File'), sg.Exit()]
]

window = sg.Window('Roulette Client Load Test Automation').Layout(layout)

while True:
    event, values = window.Read()

    if event is None or event == 'Exit':
        break

    if event == 'Create Stats File':
        # do the stuff here
        load_engine(values['_LOGSDEST_'], values['_CSVDEST_'])
        window.FindElement('_SUMMARY_').Update(
            'MAX (seconds): {}\n'
            'MIN (seconds): {}\n'
            'TOTAL client-seconds: {} {}\n'
            'MEAN (seconds): {}\n'
            'STANDARD DEVIATION: {}\n'
            'SAMPLE COUNT: {}'.format(max_seconds,
                                      min_seconds,
                                      sum_elapsed, ("(" + str("{0:.2f}".format(sum_elapsed / 3600)) + " Hours)"),
                                      mean_seconds,
                                      std_deviation,
                                      cnt_samples))

window.Close()
# print(values['_IP_'])
# print(values['_PORT_'])
# print(values['_LOGSDEST_'])
# print(values['_CSVDEST_'])
# # print(values['_NUMOFPROCS_'])
# print(values['_SUMMARY_'])
