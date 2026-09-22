/**
 * Layout component - Bố cục chính
 * Wraps pages with Sidebar and Header
 */

import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from './Sidebar';
import { Bell } from 'lucide-react';

export default function Layout() {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
        <div className="spinner" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">
        <header className="header">
          <div className="header-title">
            Hệ thống Quản lý Kho / Warehouse Management System
          </div>
          <div className="header-actions">
            <button className="btn-ghost btn-icon" title="Thông báo / Notifications">
              <Bell size={18} />
            </button>
          </div>
        </header>
        <div className="page-content">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
