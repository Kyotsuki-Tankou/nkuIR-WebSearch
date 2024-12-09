// src/components/Login.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [account, setAccount] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ account, password }),
      });
      const data = await response.json();
      if (data.success) {
        navigate('/search');
      } else {
        alert('登录失败: ' + data.message);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };
  
  const handleSignup=()=>{
    navigate('/signup')
  }

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
      <button onClick={handleLogin}>登录</button>
      <button onClick={handleSignup}>注册</button>
    </div>
  );
};

export default Login;
