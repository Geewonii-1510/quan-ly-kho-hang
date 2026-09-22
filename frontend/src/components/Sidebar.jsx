/**
 * Sidebar component - Thanh điều hướng bên
 * Navigation links with active state and role-based visibility
 */

import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  LayoutDashboard, Package, Truck, Users, BarChart3,
  ArrowDownToLine, ArrowUpFromLine, Warehouse, Bot, LogOut,
  ClipboardList
} from 'lucide-react';

const navItems = [
  {
    section: 'TỔNG QUAN / OVERVIEW',
    items: [
      { path: '/', icon: LayoutDashboard, label: 'Dashboard', labelVi: 'Bảng điều khiển' },
    ]
  },
  {
    section: 'QUẢN LÝ / MANAGEMENT',
    items: [
      { path: '/products', icon: Package, label: 'Sản phẩm / Products' },
      { path: '/suppliers', icon: Truck, label: 'Nhà cung cấp / Suppliers' },
      { path: '/import-orders', icon: ArrowDownToLine, label: 'Nhập kho / Import' },
      { path: '/export-orders', icon: ArrowUpFromLine, label: 'Xuất kho / Export' },
      { path: '/inventory', icon: Warehouse, label: 'Tồn kho / Inventory' },
    ]
  },
  {
    section: 'PHÂN TÍCH / ANALYTICS',
    items: [
      { path: '/reports', icon: BarChart3, label: 'Báo cáo / Reports' },
      { path: '/ai-assistant', icon: Bot, label: 'Trợ lý AI / AI Assistant' },
    ]
  },
  {
    section: 'HỆ THỐNG / SYSTEM',
    items: [
      { path: '/users', icon: Users, label: 'Người dùng / Users', adminOnly: true },
    ]
  },
];

export default function Sidebar() {
  const { user, logout, isAdmin } = useAuth();
  const location = useLocation();

  const getRoleLabel = (roleName) => {
    const labels = {
      'admin': 'Quản trị viên / Admin',
      'warehouse_keeper': 'Thủ kho / Warehouse Keeper',
      'accountant': 'Kế toán / Accountant',
    };
    return labels[roleName] || roleName;
  };

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="logo-icon">📦</div>
        <div>
          <h1>WMS</h1>
          <span>Warehouse Management</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {navItems.map((section, idx) => (
          <div key={idx}>
            <div className="sidebar-section-title">{section.section}</div>
            {section.items.map((item) => {
              if (item.adminOnly && !isAdmin) return null;

              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={`sidebar-link ${isActive ? 'active' : ''}`}
                >
                  <Icon />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </div>
        ))}
      </nav>

      {/* User Info */}
      <div className="sidebar-user">
        <div className="sidebar-user-avatar">
          {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
        </div>
        <div className="sidebar-user-info">
          <div className="sidebar-user-name">{user?.full_name || 'User'}</div>
          <div className="sidebar-user-role">
            {user?.role ? getRoleLabel(user.role.name) : ''}
          </div>
        </div>
        <button className="btn-ghost btn-icon" onClick={logout} title="Đăng xuất / Logout">
          <LogOut size={16} />
        </button>
      </div>
    </aside>
  );
}
