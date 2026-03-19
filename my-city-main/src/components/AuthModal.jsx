import React, { useState } from 'react';

import { API_BASE_URL } from '../api';

export default function AuthModal({ onLogin }) {
  const [isReg, setIsReg] = useState(false);
  const [form, setForm] = useState({ username: '', password: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleAction = async () => {
    if (!form.username.trim() || !form.password.trim()) {
      alert('Введите логин и пароль.');
      return;
    }

    setIsSubmitting(true);

    try {
      const endpoint = isReg ? '/register' : '/login';
      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: form.username.trim(),
          password: form.password,
        }),
      });

      // Сначала получаем текст ответа, чтобы не упасть на [object Object]
      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch (e) {
        data = { detail: text }; // Если сервер прислал не JSON, а текст/HTML
      }

      if (res.ok) {
        // Проверяем, что бэкенд прислал поле username
        onLogin(data.username || form.username.trim());
      } else {
        // Выводим конкретную ошибку из FastAPI
        alert(typeof data.detail === 'string' ? data.detail : JSON.stringify(data));
      }
    } catch (err) {
      console.error("Ошибка запроса:", err);
      alert('Бэкенд не отвечает. Убедись, что запущен Uvicorn на порту 8000.');
    } finally {
      setIsSubmitting(false);
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
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
        />
        <input
          style={inputStyle}
          type="password"
          placeholder="Пароль"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />

        <button style={buttonStyle} onClick={handleAction} disabled={isSubmitting}>
          {isSubmitting ? 'Подождите...' : (isReg ? 'Зарегистрироваться' : 'Войти')}
        </button>

        <p
          style={{ marginTop: '15px', cursor: 'pointer', color: '#3498db' }}
          onClick={() => setIsReg(!isReg)}
        >
          {isReg ? 'Уже есть аккаунт? Войти' : 'Нет аккаунта? Регистрация'}
        </p>
      </div>
    </div>
  );
}

const modalOverlayStyle = {
  position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
  backgroundColor: 'rgba(0,0,0,0.8)', display: 'flex', justifyContent: 'center',
  alignItems: 'center', zIndex: 1000,
};

const authBoxStyle = {
  backgroundColor: 'white', padding: '40px', borderRadius: '12px',
  textAlign: 'center', width: '350px', boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
};

const inputStyle = {
  width: '100%', padding: '12px', margin: '10px 0',
  borderRadius: '6px', border: '1px solid #ddd', boxSizing: 'border-box',
};

const buttonStyle = {
  width: '100%', padding: '12px', backgroundColor: '#2ecc71',
  color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer',
  fontSize: '16px', fontWeight: 'bold',
};
