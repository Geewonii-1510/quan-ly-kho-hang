/**
 * Dashboard page - Trang bảng điều khiển
 * Overview stats, charts, and low-stock alerts
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import {
  Package, ArrowDownToLine, ArrowUpFromLine,
  AlertTriangle, Truck, TrendingUp
} from 'lucide-react';
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  BarElement, Title, Tooltip, Legend, Filler,
  ArcElement, PointElement, LineElement,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale, LinearScale, BarElement, Title,
  Tooltip, Legend, Filler, ArcElement, PointElement, LineElement
);

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, chartRes, alertsRes] = await Promise.all([
        api.get('/api/reports/dashboard'),
        api.get('/api/reports/chart?days=7'),
        api.get('/api/inventory/alerts'),
      ]);
      setStats(statsRes.data);
      setChartData(chartRes.data);
      setAlerts(alertsRes.data);
    } catch (err) {
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}>
        <div className="spinner" />
      </div>
    );
  }

  const statCards = [
    { icon: Package, label: 'Tổng sản phẩm / Total Products', value: stats?.total_products || 0, color: 'blue' },
    { icon: Truck, label: 'Nhà cung cấp / Suppliers', value: stats?.total_suppliers || 0, color: 'purple' },
    { icon: ArrowDownToLine, label: 'Nhập hôm nay / Imported Today', value: stats?.total_import_today || 0, color: 'green' },
    { icon: ArrowUpFromLine, label: 'Xuất hôm nay / Exported Today', value: stats?.total_export_today || 0, color: 'cyan' },
    { icon: AlertTriangle, label: 'Cảnh báo tồn kho / Low Stock Alerts', value: stats?.low_stock_count || 0, color: 'red' },
    { icon: TrendingUp, label: 'Phiếu trong tuần / Weekly Orders', value: (chartData?.import_data?.reduce((a, b) => a + b, 0) || 0) + (chartData?.export_data?.reduce((a, b) => a + b, 0) || 0), color: 'orange' },
  ];

  const barChartData = {
    labels: chartData?.labels || [],
    datasets: [
      {
        label: 'Nhập kho / Import',
        data: chartData?.import_data || [],
        backgroundColor: 'rgba(59, 130, 246, 0.7)',
        borderColor: '#3b82f6',
        borderWidth: 1,
        borderRadius: 6,
      },
      {
        label: 'Xuất kho / Export',
        data: chartData?.export_data || [],
        backgroundColor: 'rgba(139, 92, 246, 0.7)',
        borderColor: '#8b5cf6',
        borderWidth: 1,
        borderRadius: 6,
      },
    ],
  };

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top', labels: { color: '#8b8fa3', font: { size: 12 } } },
    },
    scales: {
      x: { ticks: { color: '#5c5f73' }, grid: { color: 'rgba(255,255,255,0.05)' } },
      y: { ticks: { color: '#5c5f73', stepSize: 1 }, grid: { color: 'rgba(255,255,255,0.05)' }, beginAtZero: true },
    },
  };

  const doughnutData = {
    labels: ['Bình thường / Normal', 'Tồn thấp / Low', 'Hết hàng / Out'],
    datasets: [{
      data: [
        Math.max(0, (stats?.total_products || 0) - (stats?.low_stock_count || 0)),
        stats?.low_stock_count || 0,
        0,
      ],
      backgroundColor: ['rgba(16, 185, 129, 0.8)', 'rgba(245, 158, 11, 0.8)', 'rgba(239, 68, 68, 0.8)'],
      borderWidth: 0,
    }],
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Tổng quan hệ thống kho / Warehouse Overview</p>
        </div>
      </div>

      {/* Stats Cards / Thẻ thống kê */}
      <div className="stats-grid">
        {statCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div key={idx} className="stat-card">
              <div className={`stat-card-icon ${card.color}`}>
                <Icon size={22} />
              </div>
              <div>
                <div className="stat-card-value">{card.value}</div>
                <div className="stat-card-label">{card.label}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts / Biểu đồ */}
      <div className="charts-grid">
        <div className="chart-card">
          <div className="card-header">
            <h3 className="card-title">Nhập/Xuất 7 ngày / Import/Export (7 days)</h3>
          </div>
          <div style={{ height: 280 }}>
            <Bar data={barChartData} options={barChartOptions} />
          </div>
        </div>

        <div className="chart-card">
          <div className="card-header">
            <h3 className="card-title">Trạng thái kho / Stock Status</h3>
          </div>
          <div style={{ height: 280, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Doughnut data={doughnutData} options={{
              responsive: true, maintainAspectRatio: false,
              plugins: { legend: { position: 'bottom', labels: { color: '#8b8fa3', padding: 16 } } },
              cutout: '60%',
            }} />
          </div>
        </div>
      </div>

      {/* Low Stock Alerts / Cảnh báo tồn kho thấp */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            ⚠️ Cảnh báo tồn kho thấp / Low Stock Alerts ({alerts.length})
          </h3>
          <button className="btn btn-sm btn-secondary" onClick={() => navigate('/inventory')}>
            Xem tồn kho / View Inventory
          </button>
        </div>

        {alerts.length > 0 ? (
          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Mã SP / Code</th>
                  <th>Tên SP / Product Name</th>
                  <th>Tồn hiện tại / Current</th>
                  <th>Tồn tối thiểu / Min Stock</th>
                  <th>Thiếu / Shortage</th>
                  <th>Trạng thái / Status</th>
                </tr>
              </thead>
              <tbody>
                {alerts.slice(0, 10).map((alert) => (
                  <tr key={alert.product_id} className="alert-row">
                    <td><strong>{alert.product_code}</strong></td>
                    <td>{alert.product_name}</td>
                    <td>
                      <span className={`badge ${alert.current_stock === 0 ? 'badge-red' : 'badge-orange'}`}>
                        {alert.current_stock}
                      </span>
                    </td>
                    <td>{alert.min_stock}</td>
                    <td><span className="badge badge-red">-{alert.shortage}</span></td>
                    <td>
                      <span className={`badge ${alert.current_stock === 0 ? 'badge-red' : 'badge-orange'}`}>
                        {alert.current_stock === 0 ? 'Hết hàng / Out' : 'Tồn thấp / Low'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <h3>✅ Tất cả sản phẩm đủ tồn kho</h3>
            <p>All products have sufficient stock</p>
          </div>
        )}
      </div>
    </div>
  );
}
