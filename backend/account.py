import json
import os

# 用户名 密码 搜索记录 高频词
def read_userjson(account):
    if 'userdata' not in os.listdir('./'):
        os.mkdir('userdata')
    if f"{account}.json" in os.listdir("./userdata"):
        with open(f"./userdata/{account}.json","r") as f:
            data=json.load(f)
        return True,data
    else:
        return False,[]

def log_in(account,passwd):
    stat,userdata=read_userjson(account)
    if stat==False:
        return False,[]
    if passwd==userdata["password"]:
        return True,userdata
    else:
        return False,[]
    
def sign_up(account,passwd):
    if account+'.json' in os.listdir('./userdata'):
        return 2
    try:
        userdata=dict()
        userdata["password"]=passwd
        userdata["history"]=[]
        userdata["freq_word"]=[]
        with open(f"./userdata/{account}.json","w") as f:
            json.dump(userdata,f,indent=4)
        return 1
    except:
        return 0
    
if __name__=="__main__":
    while(True):
        print("1: sign up; 2: log in 3: quit")
        op=eval(input())
        if op==3:
            break
        elif op==2:
            print("Account:")
            account=input()
            print("Password:")
            passwd=input()
            ret,userdata=log_in(account=account,passwd=passwd)
            if ret==False:
                print("Error password")
            else:
                print("-"*50)
                print("Login successfully")               
                print(f"history: {userdata['history']}")
                print(f"frequent word: {userdata['freq_word']}")
                print("-"*50)
        elif op==1:
            print("Account:")
            account=input()
            while(True):
                print("Password:")
                passwd=input()
                print("Confirm password:")
                cpasswd=input()
                if passwd==cpasswd:
                    ret=sign_up(account=account,passwd=passwd)
                    if ret==0:
                        print('sign_up error')
                    elif ret==2:
                        print('Account already exists, retry')
                    break           
                print("Wrong password, retry")
        else:
            print("Wrong op, retry")