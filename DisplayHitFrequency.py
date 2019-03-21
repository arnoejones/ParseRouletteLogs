import os
import numpy as np
import pandas as pd
import glob
import PySimpleGUI as sg

pattern = r"  :*** Last 500 Win History: "

def find_newest_file(path):
    list_of_files = glob.glob(path + r'\*' + 'Last_500_Win_History_log.txt')
    latest_file = max(list_of_files, key=os.path.getctime)
    for file in list_of_files:
        print(file)
    print('Latest file is: ', latest_file)
    return latest_file

def open_read_hits_log(path, file):
    path_file = os.path.join(path, file)
    with open(path_file) as f:
        for line in reversed(f.readlines()):
            if 'Last 500 Win History' in line:
                numbers = (line.split(pattern))
                print(numbers[1])
                numbers_list = [numbers[1].split(',')]

                return numbers_list[0]

def frequency_chart(hits):
    three_dfs = []
    #filter out the non-valid numbers
    global df_splitted
    hits_parsed = [x for x in hits if int(x) < 255]
    #calculate the frequency of numbers hit
    frequency = [[x,hits_parsed.count(x)] for x in set(hits_parsed)]
    #convert to a dataframe
    df = pd.DataFrame(frequency)
    #add column headers
    df.columns = ['Number', 'Frequency']
    #sort from most to least hit numbers
    sorted_by_frequency_df = df.sort_values(by=['Frequency'], ascending=False)
    # split the dataframe into 3 dataframes
    df_split = np.array_split(sorted_by_frequency_df, 3)
    for df_splitted in df_split:
        three_dfs.append(df_splitted)
        print(df_splitted)
    return three_dfs
# this UI will have the path and file for input and a text box for output (or a plot)

layout = [
    [sg.Text('Find the Frequency of Hit Numbers, up to 500', size=(45, 1), font=("Helvetica", 20), text_color='blue')],
    [sg.Text('Path to Roulette logs:', size =(40,1)), sg.InputText(r'\\USNVR-W1005006\PublicShare\RouletteLogs', key='_LOGSDEST_', do_not_clear=True)],
    [sg.Text('Hit Count Summary: ', size=(15, 1)), sg.Multiline(key='_SUMMARY_1', size=(20, 14)), sg.Multiline(key='_SUMMARY_2', size=(20, 14)), sg.Multiline(key='_SUMMARY_3', size=(20, 14))],
    [sg.Submit('Create Stats File'), sg.Exit()]
]
window = sg.Window('Roulette Client Load Test Automation').Layout(layout)
while True:
    event, values = window.Read()

    if event is None or event == 'Exit':
        break

    if event == "Create Stats File":
        file = find_newest_file(values['_LOGSDEST_'])
        numbers = open_read_hits_log(values['_LOGSDEST_'], file)
        df_results = frequency_chart(numbers)
        window.FindElement('_SUMMARY_1').Update(df_results[0])
        window.FindElement('_SUMMARY_2').Update(df_results[1])
        window.FindElement('_SUMMARY_3').Update(df_results[2])
window.Close()


if __name__ == "__main__":
    path = r'\\USNVR-W1005006\PublicShare\RouletteLogs'

