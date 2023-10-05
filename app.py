import json
import os

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, send

from lan.lan_con import LanConstants
from model.config_model import ConfigModel
from model.response_model import ResponseModel

app = Flask(__name__)

# 当前文件路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 默认的语言
lan = 0
# 英文
en = {}
# 中文
zh = {}


# 初始化语言数据
def init_lan():
    global en, zh
    with open(f'{current_dir}/lan/en.json', 'r', encoding='utf-8') as f:
        en = json.load(f)
    with open(f'{current_dir}/lan/zh.json', 'r', encoding='utf-8') as f:
        zh = json.load(f)


init_lan()


def get_lan(key):
    if lan != 0:
        return en.get(key)
    else:
        return zh.get(key)


# 跨域支持
def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers[
        'Access-Control-Allow-Headers'] = 'Content-Type,Access-Token,Lan'
    # 允许HTTP请求的方法
    resp.headers['Access-Control-Allow-Methods'] = 'OPTIONS,DELETE,GET,PUT,POST'
    return resp


def before_request():
    global lan
    if request.headers.__contains__('lan'):
        lan = int(request.headers.get('lan'))


app.after_request(after_request)
app.before_request(before_request)
socketio = SocketIO()
socketio.init_app(app, cors_allowed_origins='*')


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/config/save', methods=['POST'])
def save_config():
    try:
        config_model = ConfigModel()
        # 通过这种方式获取POST提交的json数据（拿到的是字节数据）
        request_data = request.get_data()
        # 将拿到的数据转为json
        request_data_json = json.loads(request_data)
        # 将拿到的数据转换为model
        config_model.toConfigModel(request_data_json)
        # 校验数据的准确性
        # 校验是否为git地址
        if str(config_model.source_code_path).startswith('https') | str(config_model.source_code_path).startswith(
                'http') | str(config_model.source_code_path).startswith('git'):
            if str(config_model.source_code_path).endswith('.git'):
                return ResponseModel(0, None, get_lan(LanConstants.source_code_path_incorrect.value)).toJson()
        # 校验是否为文件夹路径
        else:
            if not os.path.exists(str(config_model.source_code_path)):
                return ResponseModel(0, None, get_lan(LanConstants.source_code_path_incorrect.value)).toJson()
        config_folder = f'{current_dir}/config'
        config_path = f'{config_folder}/default.json'
        if not os.path.exists(config_folder):
            os.makedirs(config_folder)  # makedirs 创建文件时如果路径不存在会创建这个路径
        config_file = open(config_path, 'w')
        config_file.write(json.dumps(request_data_json))
        config_file.close()
        return ResponseModel(1, get_lan(LanConstants.save_success.value), None).toJson()
    except Exception as exception:
        return ResponseModel(1, str(exception), None).toJson()


# 读取配置信息
@app.route('/config/fetch', methods=['GET'])
def fetch_config():
    try:
        config_folder = f'{current_dir}/config'
        config_path = f'{config_folder}/default.json'
        if os.path.exists(config_folder) is not True or os.path.exists(config_path) is not True or os.path.getsize(
                config_path) == 0:
            return ResponseModel(0, None, None).toJson()
        else:
            config_file = open(config_path, 'r', encoding='utf-8')
            json_config = json.load(config_file)
            config_file.close()
            return ResponseModel(1, json_config, None).toJson()
    except Exception as exception:
        return ResponseModel(1, str(exception), None).toJson()


@socketio.on('connect')
def connect():
    print('client connect')


@socketio.on('disconnect')
def disconnect_msg():
    print('client disconnect')


# 房间的概念，加入房间
@socketio.on('join')
def join(*data):
    user_id = data[0]
    room = data[1]
    join_room(room)
    # send为内置普通事件，客户端必须使用event='message'去接收消息
    # 向房间号所有的用户发消息，不包括自己
    print(f'{user_id} user has entered the room')
    send(f'{user_id} user has entered the room', to=room, include_self=False)


# 房间的概念，离开房间
@socketio.on('leave')
def leave(*data):
    user_id = data[0]
    room = data[1]
    leave_room(room)
    # send为内置普通事件，客户端必须使用event='message'去接收消息
    # 向房间号所有的用户发消息，不包括自己
    print(f'{user_id} user has left the room')
    send(f'{user_id} user has left the room', to=room)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=9000, debug=True)
