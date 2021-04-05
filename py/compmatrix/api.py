from flask import request, jsonify, Flask
from data_utils import get_competitive_matrix

def get_sdks_from_db(sdk_ids):
    print(comp_matrix)
    return []


app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/sdks', methods=['GET'])
def get_sdks():
    sdk_ids = request.args.to_dict(flat=False)
    print(sdk_ids)
    data = get_sdks_from_db(sdk_ids)
    return jsonify(data)

if __name__ == '__main__':
    comp_matrix = get_competitive_matrix()
    app.run()