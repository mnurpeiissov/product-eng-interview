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

def select_all_tables(conn):
    # Read data to pandas dataframe
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

def get_competitive_matrix():
    conn = create_connection('../../data.db')
    df_app, df_sdk, df_app_sdk = select_all_tables(conn)

    # I assumed that table {app : sdk} is chronologically sorted, i.e, if on row 1 app used sdk 0 and on row 10 this app
    # used sdk 4, it is assumed that app is using sdk 0 and then churned to sdk 4.
    apps_history = {}
    for row in df_app_sdk.iterrows():
        if row[1]['app_id'] in apps_history.keys():
            apps_history[row[1]['app_id']] += [(row[1]['sdk_id'])]
        else:
            apps_history[row[1]['app_id']] = [row[1]['sdk_id']]

    sdk_id_to_name = create_mapping(df_sdk)
    # we store here our competitive matrix
    competitive_matrix = np.zeros((len(sdk_id_to_name)+1, len(sdk_id_to_name)+1))
    # here we store the used apps
    used_apps = [[[] for _ in range(len(sdk_id_to_name)+1)] for _ in range(len(sdk_id_to_name)+1)]
    # each index in competitive matrix will correspond to SDK
    sdk_to_index = {sdk_id : idx for sdk_id, idx in zip(sdk_id_to_name.keys(), range(len(sdk_id_to_name)))}
    sdk_names = [sdk_id_to_name[int(idx)] for idx in sdk_to_index.keys()]

    # we go with every app and see its history, and compute competitive matrix
    for key, values in apps_history.items():
        if len(values) > 1:
            for i, value in enumerate(values):
                if i == 0:
                    idx = sdk_to_index[(value)]
                    competitive_matrix[idx][idx] += 1
                    used_apps[idx][idx] += [key]
                    old_idx = idx
                else:
                    idx = sdk_to_index[(value)]
                    competitive_matrix[idx][idx] += 1
                    used_apps[idx][idx] += [key]

                    competitive_matrix[old_idx][idx] += 1
                    used_apps[old_idx][idx] += [key]

                    competitive_matrix[old_idx][old_idx] -= 1
                    used_apps[old_idx][old_idx].pop()
                    old_idx = idx
            old_idx = None
        elif len(values) == 1:
            idx = sdk_to_index[(value)]
            competitive_matrix[idx][idx] += 1
    competitive_matrix = pd.DataFrame(competitive_matrix, columns=sdk_names + ['None'], index=sdk_names + ['None'])
    apps = pd.DataFrame(used_apps, columns=sdk_names + ['None'], index=sdk_names + ['None'])
    return competitive_matrix, apps, df_app


def get_updated_data_from_df(col_names_chosen, input_data_original):
    copy_of_data = input_data_original.copy(deep=True)
    for col_name in col_names_chosen:
        copy_of_data.loc[col_name]['None'] = sum(input_data_original.loc[col_name, ~input_data_original.columns.isin(col_names_chosen)].values)
        copy_of_data.loc['None'][col_name] = sum(input_data_original.loc[~input_data_original.columns.isin(col_names_chosen), col_name].values)

    for col_name in input_data_original.columns:
        if col_name in col_names_chosen or col_name == 'None':
            continue
        copy_of_data.loc['None']['None'] += input_data_original.loc[col_name][col_name]
    return copy_of_data

def get_updated_used_apps(col_names_chosen, input_data):
    copy_of_data = input_data.copy(deep=True)
    for col_name in col_names_chosen:
        copy_of_data.loc[col_name]['None'] = np.concatenate((input_data.loc[col_name, ~input_data.columns.isin(col_names_chosen)]))
        copy_of_data.loc['None'][col_name] = np.concatenate((input_data.loc[~input_data.columns.isin(col_names_chosen), col_name]))
    for col_name in input_data.columns:
        if col_name in col_names_chosen or col_name == 'None':
            continue
        copy_of_data.loc['None']['None'] = np.concatenate((copy_of_data.loc['None']['None'],input_data.loc[col_name][col_name]))
    return copy_of_data


def z_to_text(z):
    result = np.zeros(z.shape)
    for i in range(len(z)):
        for j in range(len(z)):
            result[i][j] = (str(z[i][j]))
    return result


def normalize_by_row(data):
    for row in range(len(data)):
        data[row][:] /= sum(data[row][:])
        data[row][:] *= 100
        data[row][:] = np.round(data[row][:])
    return data


if __name__ == '__main__':
    #conn = create_connection('data.db')
    #df1, df2, df3 = select_all_tasks(conn)
    #df1['release_date'] = pd.to_datetime(df1['release_date'])
    comp, apps, df = get_competitive_matrix()


