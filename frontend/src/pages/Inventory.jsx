/**
 * Inventory page - Trang tồn kho
 * View current stock levels with alerts
 */

import { useState, useEffect } from 'react';
import api from '../api/client';
import { Search, Warehouse, AlertTriangle } from 'lucide-react';

export default function Inventory() {
  const [inventory, setInventory] = useState([]);
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const res = await api.get('/api/inventory/');
      setInventory(res.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const filtered = inventory.filter(i => {
    const matchSearch = i.product_name.toLowerCase().includes(search.toLowerCase()) || i.product_code.toLowerCase().includes(search.toLowerCase());
    const matchStatus = filterStatus === 'all' || i.stock_status === filterStatus;
    return matchSearch && matchStatus;
  });

  const getStockBar = (qty, minStock) => {
    if (minStock === 0) return null;
    const pct = Math.min((qty / minStock) * 100, 100);
    const color = pct >= 100 ? 'green' : pct >= 50 ? 'orange' : 'red';
    return (
      <div className="stock-bar">
        <div className={`stock-bar-fill ${color}`} style={{ width: `${pct}%` }} />
      </div>
    );
  };

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}><div className="spinner" /></div>;

  const lowCount = inventory.filter(i => i.stock_status === 'low').length;
  const outCount = inventory.filter(i => i.stock_status === 'out_of_stock').length;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Tồn kho / Inventory</h1>
          <p className="page-subtitle">Theo dõi số lượng tồn kho hiện tại / Monitor current stock levels</p>
        </div>
        {(lowCount > 0 || outCount > 0) && (
          <div style={{ display: 'flex', gap: 8 }}>
            {lowCount > 0 && <span className="badge badge-orange"><AlertTriangle size={12} /> {lowCount} tồn thấp / low</span>}
            {outCount > 0 && <span className="badge badge-red"><AlertTriangle size={12} /> {outCount} hết hàng / out</span>}
          </div>
        )}
      </div>

      <div className="toolbar">
        <div className="search-box"><Search /><input placeholder="Tìm kiếm..." value={search} onChange={(e) => setSearch(e.target.value)} /></div>
        <div className="tabs">
          <button className={`tab ${filterStatus === 'all' ? 'active' : ''}`} onClick={() => setFilterStatus('all')}>Tất cả / All</button>
          <button className={`tab ${filterStatus === 'low' ? 'active' : ''}`} onClick={() => setFilterStatus('low')}>Tồn thấp / Low</button>
          <button className={`tab ${filterStatus === 'out_of_stock' ? 'active' : ''}`} onClick={() => setFilterStatus('out_of_stock')}>Hết hàng / Out</button>
        </div>
      </div>

      <div className="data-table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Mã SP / Code</th>
              <th>Tên SP / Product Name</th>
              <th>Danh mục / Category</th>
              <th>ĐVT / Unit</th>
              <th>Tồn kho / Stock</th>
              <th>Tồn TT / Min</th>
              <th>Mức tồn / Level</th>
              <th>Trạng thái / Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((item) => (
              <tr key={item.product_id} className={item.stock_status !== 'normal' ? 'alert-row' : ''}>
                <td><strong>{item.product_code}</strong></td>
                <td>{item.product_name}</td>
                <td>{item.category_name}</td>
                <td>{item.unit_name}</td>
                <td><strong style={{ fontSize: 15 }}>{item.quantity}</strong></td>
                <td>{item.min_stock}</td>
                <td style={{ minWidth: 100 }}>{getStockBar(item.quantity, item.min_stock)}</td>
                <td>
                  {item.stock_status === 'out_of_stock' && <span className="badge badge-red">Hết hàng / Out</span>}
                  {item.stock_status === 'low' && <span className="badge badge-orange">Tồn thấp / Low</span>}
                  {item.stock_status === 'normal' && <span className="badge badge-green">Bình thường / OK</span>}
                </td>
              </tr>
            ))}
            {filtered.length === 0 && <tr><td colSpan={8} className="empty-state"><Warehouse size={32} /><h3>Không có dữ liệu / No data</h3></td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
