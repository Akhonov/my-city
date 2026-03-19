import React, { useState } from 'react';

export default function AuthModal({ onLogin }) {
  const [isReg, setIsReg] = useState(false);
  const [form, setForm] = useState({ username: '', password: '' });

  const handleAction = async () => {
    try {
      const endpoint = isReg ? '/register' : '/login';
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      const data = await res.json();

      if (res.ok) {
        onLogin(data.username);
      } else {
        alert(data.detail || "Ошибка доступа");
      }
    } catch (err) {
      alert("Бэкенд не отвечает. Проверь, запущен ли main.py");
    }
  };

  return (
    <div style={modalOverlayStyle}>
      <div style={authBoxStyle}>
        <h2 style={{ color: '#2c3e50', marginBottom: '20px' }}>
          {isReg ? 'Создать профиль' : 'Вход в систему'}
        </h2>

        <input
          style={inputStyle}
          placeholder="Твой логин"
          onChange={e => setForm({...form, username: e.target.value})}
        />
        <input
          style={inputStyle}
          type="password"
          placeholder="Пароль"
          onChange={e => setForm({...form, password: e.target.value})}
        />

        <button style={buttonStyle} onClick={handleAction}>
          {isReg ? 'Зарегистрироваться' : 'Войти'}
        </button>

        <p style={{ marginTop: '15px', cursor: 'pointer', color: '#3498db' }}
           onClick={() => setIsReg(!isReg)}>
          {isReg ? 'Уже есть аккаунт? Войти' : 'Нет аккаунта? Регистрация'}
        </p>
      </div>
    </div>
  );
}

// Простые стили для хакатона
const modalOverlayStyle = {
  position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
  backgroundColor: 'rgba(0,0,0,0.8)', display: 'flex', justifyContent: 'center',
  alignItems: 'center', zIndex: 1000
};

const authBoxStyle = {
  backgroundColor: 'white', padding: '40px', borderRadius: '12px',
  textAlign: 'center', width: '350px', boxShadow: '0 10px 25px rgba(0,0,0,0.2)'
};

const inputStyle = {
  width: '100%', padding: '12px', margin: '10px 0',
  borderRadius: '6px', border: '1px solid #ddd', boxSizing: 'border-box'
};

const buttonStyle = {
  width: '100%', padding: '12px', backgroundColor: '#2ecc71',
  color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer',
  fontSize: '16px', fontWeight: 'bold'
};