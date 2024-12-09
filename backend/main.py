import os
import json
import logging
from flask import Flask,request,jsonify
from flask_cors import CORS

from account import read_userjson,log_in,sign_up
from do_search import conduct_query

userdata=[]

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())


@app.route('/login', methods=['POST','OPTIONS'])
def login():
    if request.method=='OPTIONS':
        response=app.make_default_options_response()
        response.headers['Access-Control-Allow-Methods']='POST'
        response.headers['Access-Control-Allow-Headers']='Content-Type'
        response.headers['Access-Control-Allow-Origin']='*'# 允许所有来源
        return response
        
    data = request.get_json()
    account = data.get('account')
    password = data.get('password')
    print(account,password)
    if not account or not password:
        return jsonify({"success": False, "message": "账号和密码不能为空"}), 400

    status,userdata=log_in(account, password)
    if status:
        return jsonify({"success": True, "message": "登录成功", "userdata": userdata}), 200
    else:
        return jsonify({"success": False, "message": "账号或密码错误"}), 401

@app.route('/signup', methods=['POST','OPTIONS'])
def signup():
    if request.method=='OPTIONS':
        response=app.make_default_options_response()
        response.headers['Access-Control-Allow-Methods']='POST'
        response.headers['Access-Control-Allow-Headers']='Content-Type'
        response.headers['Access-Control-Allow-Origin']='*'
        return response
        
    data = request.get_json()
    account = data.get('account')
    password = data.get('password')
    c_pwd=data.get('confirm_pwd')
    print(account,password,c_pwd)
    
    if not account or not password or not c_pwd:
        return jsonify({"success": False, "message": "账号和密码不能为空"}), 400
    
    if password!=c_pwd:
        return jsonify({"success": False, "message": "密码输入不一致"}), 400
    
    status=sign_up(account, password)
    if status==1:
        return jsonify({"success": True, "message": "登录成功", "userdata": userdata}), 200
    elif status==2:
        return jsonify({"success": False, "message": "用户已存在"}), 401
    else:
        return jsonify({"success": False, "message": "注册时发生错误，请重试"}), 400

@app.route('/search', methods=['POST','OPTIONS'])
def dosearch():
    if request.method=='OPTIONS':
        response=app.make_default_options_response()
        response.headers['Access-Control-Allow-Methods']='POST'
        response.headers['Access-Control-Allow-Headers']='Content-Type'
        response.headers['Access-Control-Allow-Origin']='*'
        return response
        
    data = request.get_json()
    account = data.get('account')
    password = data.get('password')
    c_pwd=data.get('confirm_pwd')
    print(account,password,c_pwd)
    
    status=sign_up(account, password)
    if status==1:
        return jsonify({"success": True, "message": "登录成功", "userdata": userdata}), 200
    elif status==2:
        return jsonify({"success": False, "message": "用户已存在"}), 401
    else:
        return jsonify({"success": False, "message": "注册时发生错误，请重试"}), 400
    
if __name__ == '__main__':
    app.run(debug=True)