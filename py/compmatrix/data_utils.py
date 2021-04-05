import sqlite3
import pandas as pd
import numpy as np


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except:
        print('could not connect')
    return conn

def select_all_tasks(conn):

    #cur = conn.cursor()

    # extract the names
    # cur.execute("SELECT name FROM sqlite_master WHERE type='table';")

    #app = cur.execute("SELECT * FROM sdk;")

    df_app = pd.read_sql_query("SELECT * FROM app", conn)
    df_sdk = pd.read_sql_query("SELECT * FROM sdk", conn)
    df_app_sdk = pd.read_sql_query("SELECT * FROM app_sdk", conn)

    return df_app, df_sdk, df_app_sdk


def create_mapping(df):
    sdk_mapping_id_to_name = {}
    ids = df['id']
    names = df['name']
    for i, id in enumerate(ids):
        sdk_mapping_id_to_name[id] = names[i]
    return sdk_mapping_id_to_name


def get_by_year(grouped_df, year):
    assert 2007 < year < 2021, "Data is available for 2007-2020 years"
    df_of_year = grouped_df.get_group(year)
    app_ids = df_of_year['id'].values
    return app_ids


def get_stats(sdks, sdk_names):
    sdks_in_this_year = set(sdks['sdk_id'].values)
    to_return = {}
    for sdk in sdks_in_this_year:
        print(sdk)
        to_return[sdk_names[sdk]] = len(sdks[sdks['sdk_id'] == sdk])

    return to_return


def get_competitive_matrix():
    conn = create_connection('../../data.db')
    df1, df2, df3 = select_all_tasks(conn)
    df1['release_date'] = pd.to_datetime(df1['release_date'])

    some_dict = {}
    for row in df3.iterrows():
        if row[1]['app_id'] in some_dict.keys():
            some_dict[row[1]['app_id']] += [(row[1]['sdk_id'])]
        else:
            some_dict[row[1]['app_id']] = [row[1]['sdk_id']]

    competitive_matrix = np.zeros((15, 15))
    used_apps = [[[] for _ in range(14)] for _ in range(14)]

    sdk_id_to_name = create_mapping(df2)

    sdk_to_index = {'131': 0, '33': 1, '262': 2, '18': 3, '51': 4, '1029': 5, '30': 6, '6075': 7,
                    '2081': 8, '8': 9, '5323': 10, '5720': 11, '875': 12, '13': 13}
    sdk_names = [sdk_id_to_name[int(idx)] for idx in sdk_to_index.keys()]

    for key, values in some_dict.items():
        if len(values) > 1:
            for i, value in enumerate(values):
                if i == 0:
                    idx = sdk_to_index[str(value)]
                    competitive_matrix[idx][idx] += 1
                    used_apps[idx][idx] += [key]
                    old_idx = idx
                else:
                    idx = sdk_to_index[str(value)]
                    competitive_matrix[idx][idx] += 1
                    used_apps[idx][idx] += [key]

                    competitive_matrix[old_idx][idx] += 1
                    used_apps[old_idx][idx] += [key]

                    competitive_matrix[old_idx][old_idx] -= 1
                    used_apps[old_idx][old_idx].pop()
                    old_idx = idx
            old_idx = None
        elif len(values) == 1:
            idx = sdk_to_index[str(value)]
            competitive_matrix[idx][idx] += 1
    competitive_matrix = pd.DataFrame(competitive_matrix, columns=sdk_names + ['None'], index=sdk_names + ['None'])
    apps = pd.DataFrame(used_apps, columns=sdk_names, index=sdk_names)
    return competitive_matrix, apps, df1



if __name__ == '__main__':
    #conn = create_connection('data.db')
    #df1, df2, df3 = select_all_tasks(conn)
    #df1['release_date'] = pd.to_datetime(df1['release_date'])
    comp, apps, df = get_competitive_matrix()
    app_ids = [529479190, 431946152, 553834731, 506627515]
    print(df[df['id'].isin(app_ids)])

    #print(comp[['PayPal', 'Stripe']].loc[['PayPal', 'Stripe']])

