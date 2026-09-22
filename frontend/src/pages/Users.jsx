/**
 * Users page - Trang quản lý người dùng (Admin only)
 */

import { useState, useEffect } from 'react';
import api from '../api/client';
import { Users as UsersIcon, Shield } from 'lucide-react';

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const res = await api.get('/api/users/');
      setUsers(res.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const getRoleBadge = (role) => {
    if (!role) return null;
    const colors = { admin: 'badge-purple', warehouse_keeper: 'badge-blue', accountant: 'badge-green' };
    const labels = { admin: 'Quản trị viên / Admin', warehouse_keeper: 'Thủ kho / Warehouse', accountant: 'Kế toán / Accountant' };
    return <span className={`badge ${colors[role.name] || 'badge-blue'}`}><Shield size={10} /> {labels[role.name] || role.name}</span>;
  };

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Người dùng / Users</h1>
          <p className="page-subtitle">Quản lý tài khoản và phân quyền / User accounts & permissions</p>
        </div>
      </div>

      <div className="data-table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Tên đăng nhập / Username</th>
              <th>Họ tên / Full Name</th>
              <th>Email</th>
              <th>Vai trò / Role</th>
              <th>Trạng thái / Status</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.id}</td>
                <td><strong>{u.username}</strong></td>
                <td>{u.full_name}</td>
                <td>{u.email}</td>
                <td>{getRoleBadge(u.role)}</td>
                <td><span className={`badge ${u.is_active ? 'badge-green' : 'badge-red'}`}>{u.is_active ? 'Hoạt động / Active' : 'Khóa / Locked'}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
