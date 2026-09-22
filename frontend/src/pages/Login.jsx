/**
 * Login page - Trang đăng nhập
 * Glassmorphism login card with bilingual labels
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LogIn, Eye, EyeOff } from 'lucide-react';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Lỗi đăng nhập / Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">
          <div className="logo-icon">📦</div>
          <h2>WMS Login</h2>
          <p>Hệ thống Quản lý Kho hàng / Warehouse Management System</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Tên đăng nhập / Username</label>
            <input
              type="text"
              className="form-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Nhập tên đăng nhập..."
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label">Mật khẩu / Password</label>
            <div style={{ position: 'relative' }}>
              <input
                type={showPassword ? 'text' : 'password'}
                className="form-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Nhập mật khẩu..."
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)',
                  background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer',
                }}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {error && (
            <div style={{ color: 'var(--accent-red)', fontSize: 13, marginBottom: 12, textAlign: 'center' }}>
              {error}
            </div>
          )}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? (
              <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
            ) : (
              <>
                <LogIn size={16} />
                Đăng nhập / Login
              </>
            )}
          </button>
        </form>

        <div style={{
          marginTop: 24, padding: '12px 16px',
          background: 'var(--bg-glass)', borderRadius: 'var(--radius-sm)',
          fontSize: 12, color: 'var(--text-muted)',
        }}>
          <div style={{ fontWeight: 600, marginBottom: 4, color: 'var(--text-secondary)' }}>
            Tài khoản demo / Demo accounts:
          </div>
          <div>👤 admin / 123456 (Quản trị viên)</div>
          <div>👤 thuho / 123456 (Thủ kho)</div>
          <div>👤 ketoan / 123456 (Kế toán)</div>
        </div>
      </div>
    </div>
  );
}
