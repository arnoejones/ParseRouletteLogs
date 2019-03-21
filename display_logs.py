import os
import re
import pandas as pd
from datetime import datetime
import PySimpleGUI as sg
import numpy as np

# sample line for the following regex to match: Log Entry : 9:50:13 AM 09:50:13.902
pattern = r"([0-9]+:[0-9]+:[0-9]+.[0-9]+)|(\d+(/|-){1}\d+(/|-){1}\d{2,4}|([0-9]+:[0-9]+:[0-9]+\s[A|P]M))"

files_read = []

def create_empty_folder(folder_name):
    if not os.path.exists(folder_name):
        print("creating", folder_name)
        os.makedirs(folder_name)

def load_engine(raw_logs_location, logs_results_location):
    for filename in os.listdir(raw_logs_location):
        files_read.append(filename)
        print(filename)
        temp_list = []
        with open(raw_logs_location + '/' + filename) as f:
            fileContents = f.read()
            counter = 0
            matches = re.findall(pattern, fileContents, re.MULTILINE)

            for matchNum, match in enumerate(matches):
                log_entry_date = matches[counter + 0][1]
                log_entry_time = matches[counter + 1][1]
                game_event_timestamp = matches[counter + 2][0]

                # new = game_event_timestamp
                # deltaT = datetime.strptime(new, timeFormat) - datetime.strptime(old, timeFormat)

                # deltaTinSeconds = deltaT.total_seconds()

                # old = new
                # temp_list.append([filename, log_entry_date, log_entry_time, deltaTinSeconds])

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
            # time_differences.append(temp_list)

def create_empty_dataset():
    arr = np.empty((0, 3), int)
    arr = np.append(arr, np.array([['Number', 'Hit Count', 'DTD']]), axis=0)
    for item in range(1, 37):
        arr = np.append(arr, np.array([[str(item), np.nan, np.nan]]), axis=0)

    df = pd.DataFrame(arr)

    # add 0, 00, 000 to the list of numbers
    df.loc[37] = ['0', np.nan, np.nan]
    df.loc[38] = ['00', np.nan, np.nan]
    df.loc[39] = ['000', np.nan, np.nan]

    print(df)





    # col_1 = [i for i in range(1,14)]
    # col_2 = [i for i in range(14, 27)]
    # col_3 = [i for i in range(27, 37)]
    # col_3.append('0')
    # col_3.append('00')
    # col_3.append('000')
    #
    # all_columns = [col_1, col_2, col_3]
    # df = pd.DataFrame(all_columns)
    #
    #
    # print(df)

if __name__ == "__main__":
    create_empty_dataset()
    # tmp paths - for testing only
    raw_logs_location = r'\\USNVR-W1005006\PublicShare\RouletteLogs'
    logs_results_location = r'\\USNVR-W1005006\PublicShare\RouletteLogsCSV'
    load_engine(raw_logs_location, logs_results_location)