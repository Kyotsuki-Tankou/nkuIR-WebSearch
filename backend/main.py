import os
import json
import logging
from elasticsearch import Elasticsearch
from flask import Flask,request,jsonify
from flask_cors import CORS

from account import read_userjson,log_in,sign_up
from do_search import conduct_query,word_proc
from query_gen import get_index

have_login=False
userdata=None
es = Elasticsearch(
        hosts=["http://localhost:9200"],
        http_auth=('elastic', '123456')
    )
index_name,index_body=get_index()
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
    global have_login
    global userdata
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
        have_login=True
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
        global have_login
        global userdata
        if have_login==False:
            return jsonify({"success": False, "message": "请先登陆"}), 400
    # try:
        if request.method=='OPTIONS':
            response=app.make_default_options_response()
            response.headers['Access-Control-Allow-Methods']='POST'
            response.headers['Access-Control-Allow-Headers']='Content-Type'
            response.headers['Access-Control-Allow-Origin']='*'
            return response
            
        data=request.get_json()
        query_term=data.get('exactSearch')
        query_phrase=data.get('fuzzySearch')
        query_regex=data.get('regexSearch')
        #process query list
        query_word_term=word_proc(query_term)
        query_word_phrase=word_proc(query_phrase)
        query_word_regex=word_proc(query_regex)
        query_domain=data.get('domainSearch')
        print(f'term: {query_word_term}, phrase:{query_word_phrase}, regex:{query_word_regex}')
        query_size=20
        try:
            query_size=eval(data.get('querySize'))
        except:
            query_size=20
        frequent_token=userdata['freq_word']
        #conduct query
        query_cnt,query_list,result_list=conduct_query(
            query_word_term=query_word_term,
            query_word_phrase=query_word_phrase,
            query_word_regex=query_word_regex,
            query_domain=query_domain,
            frequent_token=frequent_token,
            es=es,
            index_name=index_name,
            fields=['title','anchor','content','url'],
            query_size=query_size
            )
        #conduct recommend based on fuzzy search
        rec1_cnt,rec1_list,rec1_res=conduct_query(
            query_word_term=[],
            query_word_phrase=query_word_phrase+query_word_term+query_word_regex,
            query_word_regex=[],
            query_domain=query_domain,
            frequent_token=frequent_token,
            es=es,
            index_name=index_name,
            fields=['title','anchor','content','url'],
            query_size=10
            )
        
        #update history
        history={
            'exact':query_term,
            'fuzzy':query_phrase,
            'regex':query_regex,
            'domain':query_domain,
            'size':query_size}
        userdata['history'].append(history)
        if len(userdata['history'])>=10:
            userdata['history'].pop(0)
        
        #update freq_list
        sorted_querylist=sorted(query_list,key=lambda k:query_list[k],reverse=True)
        freq_cnt=0
        for freq in sorted_querylist:
            freq_cnt+=1
            if freq_cnt>5:
                break
            if freq in userdata['freq_word']:
                userdata['freq_word']=[item for item in userdata['freq_word'] if item!=freq]
            userdata['freq_word'].append(freq)
            if len(userdata['freq_word'])>=10:
                userdata['freq_word'].pop(0)
        #update user file
        with open(f"./userdata/{userdata['account']}.json","w") as f:
            json.dump(userdata,f,indent=4)
        #generate return json
        return jsonify({'success':True,'res_list':result_list,'res_cnt':query_cnt,'rec1_list':rec1_res,'rec1_cnt':rec1_cnt,'rec2_list':rec1_res,'rec2_cnt':rec1_cnt}),200
    # except:
    #     return jsonify({'success': False,"message":"发生错误"}),400
    
if __name__ == '__main__':
    app.run(debug=True)