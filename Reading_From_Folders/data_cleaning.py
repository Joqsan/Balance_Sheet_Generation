import re
import pandas as pd
import numpy as np
import calendar
import locale

locale.setlocale(locale.LC_ALL,'es_ES.UTF-8')

months = list(calendar.month_abbr)
months = list(map(lambda x: x.capitalize(), months))

def sort_index(df):
    month_categories = pd.CategoricalIndex(df.index.get_level_values(0), categories=months[1:], ordered=True)
    df.index = [month_categories, df.index.get_level_values(1)]
    df = df.sort_index(level=0)
    return df

def transpose_data(df, month, name):
    df = df.transpose()
    df.columns = df.iloc[0, :]
    df = df.drop(0, axis=0)
    df = df.set_index([[month], [name]])

    return df

def afp_data_cleaning(dfs):

    part1 = dfs[0].df.copy()
    period = part1.iloc[0, 1]
    month_str = re.match(r"(?P<month>[0-9]{2})", period).group('month')
    month_id = int(re.sub(r'0([0-9])', r'\1', month_str))
    month = months[month_id]


    part2 = dfs[1].df.copy()
    part2 = part2.drop([0, 1])
    part2.loc[:3, 0] = part2.loc[:3, 0].str.replace('Cotización', 'SC')
    part2.iloc[-1, 0] = 'Total A Pagar SC'
    part2.reset_index(drop=True, inplace=True)

    part3 = dfs[2].df.copy()
    afp_name = part3.iloc[-1, 0].split(' ')[-1]
    part3 = part3.drop([0, 1, 10, 13])
    part3.iloc[0, 0] = 'Total Imponible'
    part3.iloc[-1, 0] = 'Total A Pagar A AFP'

    afp = pd.concat([part3, part2], ignore_index=True)
    afp.iloc[:, [1]] = afp.iloc[:, [1]].apply(lambda x: x.str.replace('.', '')).astype(int)

    afp = transpose_data(afp, month, afp_name)

    return afp


def fonasa_data_cleaning(dfs):

    part1 = dfs[0].df.copy()
    month_str = part1.iloc[1, 0]
    month_id = int(re.sub(r'0([0-9])', r'\1', month_str))
    month = months[month_id]


    part2 = dfs[1].df.copy()
    part2.drop(0, inplace=True)
    part2.drop(1, axis=1, inplace=True)
    part2.iloc[-1, 0] = 'Total A Pagar'


    part2.iloc[:, [1]] = part2.iloc[:, [1]].apply(lambda x: x.str.replace('.', '')).astype(int)

    fonasa = transpose_data(part2, month, 'FONASA')

    return fonasa


def isapre_data_cleaning(dfs):

    df = dfs[0].df.copy()

    month = df.iloc[3, 5].split(' ')[0][:3]
    isapre_name = df.iloc[-1, 0].split(' ')[-1]

    if isapre_name == 'S.A.':
        isapre_name = 'Cruz Blanca'

    df = df.iloc[:, [0, 3]].copy()

    df.iloc[-1, 0] = 'Total A Pagar'

    df[0] = df[0].apply(lambda x: x.title())

    df.iloc[:, [1]] = df.iloc[:, [1]].apply(lambda x: x.str.replace('.', '')).astype(int)

    isapre = transpose_data(df, month, isapre_name)

    return isapre

def mutual_data_cleaning(dfs):

    df = dfs[0].df.copy()

    month = df.iloc[6, 4].split(' ')[0][:3]

    df = df.iloc[[5,7], [0, 3]].copy()
    df.iloc[:, 0] = ['Total Remuneraciones', 'Total A Pagar']
    df.iloc[:, [1]] = df.iloc[:, [1]].apply(lambda x: x.str.replace('.', '')).astype(int)

    mutual = transpose_data(df, month, 'Mutual')

    return mutual

def ccaf_data_cleaning(dfs):

    part1 = dfs[0].df.copy()
    month = part1.iloc[4, 0].split(' ')[0][:3]

    part2 = dfs[1].df.copy()
    part2.drop([0,1, 7], inplace=True)
    part2.loc[[6, 13], 0:2] = part2.loc[[6, 13], 0:2].shift(-2, axis=1)
    part2.iloc[:, 0] = part2.iloc[:, 0].str.title()
    part2 = part2.iloc[:, [0, 4]].copy()
    part2.iloc[-1, 0] = 'Total A Pagar A Caja'

    part2.iloc[:, [1]] = part2.iloc[:, [1]].apply(lambda x: x.str.replace('.', '')).astype(int)

    ccaf = transpose_data(part2, month, 'CCAF')

    return ccaf
