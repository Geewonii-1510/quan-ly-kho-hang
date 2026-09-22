/**
 * Reports page - Trang báo cáo thống kê
 * Inventory summary with date filters
 */

import { useState, useEffect } from 'react';
import api from '../api/client';
import { BarChart3, Download } from 'lucide-react';

export default function Reports() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const now = new Date();
  const [startDate, setStartDate] = useState(new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(now.toISOString().split('T')[0]);

  const loadReport = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/api/reports/inventory-summary?start_date=${startDate}&end_date=${endDate}`);
      setSummary(res.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadReport(); }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Báo cáo nhập xuất tồn / Inventory Report</h1>
          <p className="page-subtitle">Thống kê nhập xuất tồn kho theo thời gian / Inventory statistics by period</p>
        </div>
      </div>

      {/* Filters / Bộ lọc */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 16, alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Từ ngày / From</label>
            <input className="form-input" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </div>
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Đến ngày / To</label>
            <input className="form-input" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </div>
          <button className="btn btn-primary" onClick={loadReport} disabled={loading}>
            <BarChart3 size={16} /> {loading ? 'Đang tải...' : 'Xem báo cáo / View Report'}
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      {summary && (
        <div className="stats-grid" style={{ marginBottom: 20 }}>
          <div className="stat-card">
            <div className="stat-card-icon green"><BarChart3 size={22} /></div>
            <div>
              <div className="stat-card-value">{summary.total_imported}</div>
              <div className="stat-card-label">Tổng nhập / Total Imported</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-icon purple"><BarChart3 size={22} /></div>
            <div>
              <div className="stat-card-value">{summary.total_exported}</div>
              <div className="stat-card-label">Tổng xuất / Total Exported</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-icon blue"><BarChart3 size={22} /></div>
            <div>
              <div className="stat-card-value">{summary.items?.length || 0}</div>
              <div className="stat-card-label">Số SP / Products</div>
            </div>
          </div>
        </div>
      )}

      {/* Detail Table / Bảng chi tiết */}
      {summary?.items && (
        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Mã SP / Code</th>
                <th>Tên SP / Product</th>
                <th>Danh mục / Category</th>
                <th>Tồn đầu kỳ / Opening</th>
                <th>Nhập / Import</th>
                <th>Xuất / Export</th>
                <th>Tồn cuối kỳ / Closing</th>
                <th>Tồn TT / Min</th>
                <th>Trạng thái / Status</th>
              </tr>
            </thead>
            <tbody>
              {summary.items.map((item) => {
                const isLow = item.min_stock > 0 && item.closing_stock < item.min_stock;
                return (
                  <tr key={item.product_id} className={isLow ? 'alert-row' : ''}>
                    <td><strong>{item.product_code}</strong></td>
                    <td>{item.product_name}</td>
                    <td>{item.category_name}</td>
                    <td>{item.opening_stock}</td>
                    <td style={{ color: 'var(--accent-green)' }}>+{item.total_imported}</td>
                    <td style={{ color: 'var(--accent-red)' }}>-{item.total_exported}</td>
                    <td><strong>{item.closing_stock}</strong></td>
                    <td>{item.min_stock}</td>
                    <td>
                      {isLow
                        ? <span className="badge badge-red">⚠ Thiếu / Low</span>
                        : <span className="badge badge-green">✓ Đủ / OK</span>
                      }
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
