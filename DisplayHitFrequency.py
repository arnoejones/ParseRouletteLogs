import os
import pandas as pd

pattern = r"  :*** Last 500 Win History: "

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

    #filter out the non-valid numbers
    hits_parsed = [x for x in hits if int(x) < 255]
    #calculate the frequency of numbers hit
    frequency = [[x,hits_parsed.count(x)] for x in set(hits_parsed)]
    #convert to a dataframe
    df = pd.DataFrame(frequency)
    #add column headers
    df.columns = ['Number', 'Frequency']
    #sort from most to least hit numbers
    sorted_by_frequency_df = df.sort_values(by=['Frequency'], ascending=False)
    print(sorted_by_frequency_df)

if __name__ == "__main__":
    path = r'\\USNVR-W1005006\PublicShare\RouletteLogs'
    file = r'USNVR-W1009547_83540_Last_500_Win_History_log.txt'
    numbers = open_read_hits_log(path, file)
    frequency_chart(numbers)
