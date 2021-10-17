import os
import csv

signs = []
count_bad = 0
count_good = 0


with open('unprocessed/recipeData.csv', mode='r', encoding='latin-1') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if(row['BeerID'] == '228'):
            print(row['Style'])

        '''
        for col in row:
            if(sign in row[col]):
                count_bad = count_bad + 1
                continue
        count_good = count_good + 1
        '''
