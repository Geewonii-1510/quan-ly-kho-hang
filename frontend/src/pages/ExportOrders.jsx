/**
 * Export Orders page - Trang phiếu xuất kho
 */

import { useState, useEffect } from 'react';
import api from '../api/client';
import { Plus, ArrowUpFromLine, Eye } from 'lucide-react';

export default function ExportOrders() {
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showDetail, setShowDetail] = useState(null);
  const [form, setForm] = useState({ recipient: '', order_date: new Date().toISOString().split('T')[0], note: '', details: [{ product_id: '', quantity: 1, reason: '' }] });
  const [error, setError] = useState('');

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [ordRes, prodRes] = await Promise.all([
        api.get('/api/export-orders/'),
        api.get('/api/products/'),
      ]);
      setOrders(ordRes.data);
      setProducts(prodRes.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const addLine = () => setForm({ ...form, details: [...form.details, { product_id: '', quantity: 1, reason: '' }] });
  const removeLine = (idx) => setForm({ ...form, details: form.details.filter((_, i) => i !== idx) });
  const updateLine = (idx, field, value) => {
    const newDetails = [...form.details];
    newDetails[idx] = { ...newDetails[idx], [field]: value };
    setForm({ ...form, details: newDetails });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const data = {
        recipient: form.recipient,
        order_date: new Date(form.order_date).toISOString(),
        note: form.note,
        details: form.details.map(d => ({
          product_id: Number(d.product_id),
          quantity: Number(d.quantity),
          reason: d.reason,
        })),
      };
      await api.post('/api/export-orders/', data);
      setShowModal(false);
      loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error');
    }
  };

  const formatDate = (d) => new Date(d).toLocaleDateString('vi-VN');

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Phiếu xuất kho / Export Orders</h1>
          <p className="page-subtitle">Quản lý xuất hàng khỏi kho / Manage warehouse exports</p>
        </div>
        <button className="btn btn-primary" onClick={() => {
          setForm({ recipient: '', order_date: new Date().toISOString().split('T')[0], note: '', details: [{ product_id: products[0]?.id || '', quantity: 1, reason: '' }] });
          setError('');
          setShowModal(true);
        }}>
          <Plus size={16} /> Tạo phiếu xuất / New Export
        </button>
      </div>

      <div className="data-table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Mã phiếu / Code</th>
              <th>Người nhận / Recipient</th>
              <th>Ngày xuất / Date</th>
              <th>Người tạo / Created By</th>
              <th>Trạng thái / Status</th>
              <th>Thao tác / Actions</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td><strong>{o.code}</strong></td>
                <td>{o.recipient}</td>
                <td>{formatDate(o.order_date)}</td>
                <td>{o.created_by_name}</td>
                <td><span className="badge badge-blue">Hoàn thành / Done</span></td>
                <td><button className="btn btn-ghost btn-sm" onClick={() => setShowDetail(o)}><Eye size={14} /> Chi tiết</button></td>
              </tr>
            ))}
            {orders.length === 0 && <tr><td colSpan={6} className="empty-state"><ArrowUpFromLine size={32} /><h3>Chưa có phiếu xuất / No export orders</h3></td></tr>}
          </tbody>
        </table>
      </div>

      {/* Create Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" style={{ maxWidth: 700 }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Tạo phiếu xuất kho / New Export Order</h3>
              <button className="btn-ghost btn-icon" onClick={() => setShowModal(false)}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Người nhận / Recipient</label>
                    <input className="form-input" value={form.recipient} onChange={(e) => setForm({ ...form, recipient: e.target.value })} placeholder="Phòng ban / Khách hàng..." required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Ngày xuất / Export Date</label>
                    <input className="form-input" type="date" value={form.order_date} onChange={(e) => setForm({ ...form, order_date: e.target.value })} required />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Ghi chú / Notes</label>
                  <input className="form-input" value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} />
                </div>

                {error && <div style={{ color: 'var(--accent-red)', fontSize: 13, marginBottom: 12, padding: '10px 14px', background: 'rgba(239,68,68,0.1)', borderRadius: 8 }}>⚠️ {error}</div>}

                <label className="form-label" style={{ marginTop: 12 }}>Chi tiết phiếu xuất / Export Details</label>
                <table className="order-details-table">
                  <thead><tr><th>Sản phẩm / Product</th><th style={{ width: 80 }}>Tồn / Stock</th><th style={{ width: 90 }}>SL / Qty</th><th style={{ width: 140 }}>Lý do / Reason</th><th style={{ width: 40 }}></th></tr></thead>
                  <tbody>
                    {form.details.map((d, idx) => {
                      const selectedProd = products.find(p => p.id === Number(d.product_id));
                      return (
                        <tr key={idx}>
                          <td>
                            <select className="form-select" value={d.product_id} onChange={(e) => updateLine(idx, 'product_id', e.target.value)} required>
                              <option value="">-- Chọn SP --</option>
                              {products.map(p => <option key={p.id} value={p.id}>{p.code} - {p.name}</option>)}
                            </select>
                          </td>
                          <td><span className={`badge ${selectedProd && selectedProd.current_stock < Number(d.quantity) ? 'badge-red' : 'badge-green'}`}>{selectedProd?.current_stock ?? '-'}</span></td>
                          <td><input className="form-input" type="number" min="1" value={d.quantity} onChange={(e) => updateLine(idx, 'quantity', e.target.value)} required /></td>
                          <td><input className="form-input" value={d.reason} onChange={(e) => updateLine(idx, 'reason', e.target.value)} placeholder="Lý do..." /></td>
                          <td>{form.details.length > 1 && <button type="button" className="btn btn-ghost btn-sm" onClick={() => removeLine(idx)} style={{ color: 'var(--accent-red)' }}>✕</button>}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                <button type="button" className="btn btn-secondary btn-sm" onClick={addLine} style={{ marginTop: 8 }}><Plus size={14} /> Thêm dòng / Add Line</button>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Hủy / Cancel</button>
                <button type="submit" className="btn btn-success">Tạo phiếu xuất / Create Export</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showDetail && (
        <div className="modal-overlay" onClick={() => setShowDetail(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Phiếu xuất {showDetail.code}</h3>
              <button className="btn-ghost btn-icon" onClick={() => setShowDetail(null)}>✕</button>
            </div>
            <div className="modal-body">
              <p><strong>Người nhận / Recipient:</strong> {showDetail.recipient}</p>
              <p><strong>Ngày / Date:</strong> {formatDate(showDetail.order_date)}</p>
              <p><strong>Người tạo / Created by:</strong> {showDetail.created_by_name}</p>
              {showDetail.note && <p><strong>Ghi chú / Note:</strong> {showDetail.note}</p>}
              <div style={{ marginTop: 16 }}>
                <table className="data-table">
                  <thead><tr><th>Sản phẩm</th><th>SL</th><th>Lý do</th></tr></thead>
                  <tbody>
                    {showDetail.details.map((d, idx) => (
                      <tr key={idx}><td>{d.product_code} - {d.product_name}</td><td>{d.quantity}</td><td>{d.reason}</td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
