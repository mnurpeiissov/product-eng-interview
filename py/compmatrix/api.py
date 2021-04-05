from flask import request, jsonify, Flask
import data_utils

def parse_json(json_content):
    ids = json_content['ids']
    return ids

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/sdks/all', methods=['GET'])
def get_all_sdks():
    sdk_ids = comp_matrix.columns
    return data_utils.get_updated_data_from_df(sdk_ids, comp_matrix).to_json()

@app.route('/sdks', methods=['GET'])
def get_selected_sdks():
    sdk_ids = request.args.to_dict(flat=False)
    sdk_ids = parse_json(sdk_ids)
    return data_utils.get_updated_data_from_df([sdk_ids], comp_matrix).to_json()

@app.route('/used_apps', methods=['GET'])
def get_used_apps():
    sdk_ids = request.args.to_dict(flat=False)
    sdk_ids = parse_json(sdk_ids)
    return data_utils.get_updated_used_apps(sdk_ids, apps).to_json()


if __name__ == '__main__':
    comp_matrix, apps, df_app = data_utils.get_competitive_matrix()
    app.run()