// src/components/Login.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Signup = () => {
  const [account, setAccount] = useState('');
  const [password, setPassword] = useState('');
  const [confirm_pwd, setConfirmPwd] = useState('');
  const navigate = useNavigate();

  const handleSignup = async () => {
    // navigate('/login');
    console.log('account:',account);
    console.log('password:',password);
    console.log('c_password:',confirm_pwd);
    try{
        const response=await fetch('http://127.0.0.1:5000/signup',{
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify({account,password,confirm_pwd}),
        });
        const data=await response.json();
        if(data.success){
            alert('注册成功！')
            navigate('/login');
        }
        else{
            alert('注册失败：'+data.message);
        }
    }
    catch(error)
    {
        console.error('Error:',error)
    }
};

  return (
    <div>
      <h2>登录</h2>
      <input
        type="text"
        placeholder="用户名"
        value={account}
        onChange={(e) => setAccount(e.target.value)}
      />
      <input
        type="password"
        placeholder="密码"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <input
        type="password"
        placeholder="确认密码"
        value={confirm_pwd}
        onChange={(e) => setConfirmPwd(e.target.value)}
      />
      <button onClick={handleSignup}>注册</button>
    </div>
  );
};

export default Signup;
