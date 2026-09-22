/**
 * Import Orders page - Trang phiếu nhập kho
 */

import { useState, useEffect } from 'react';
import api from '../api/client';
import { Plus, ArrowDownToLine, Eye } from 'lucide-react';

export default function ImportOrders() {
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showDetail, setShowDetail] = useState(null);
  const [form, setForm] = useState({ supplier_id: '', order_date: new Date().toISOString().split('T')[0], note: '', details: [{ product_id: '', quantity: 1, unit_price: 0 }] });

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [ordRes, prodRes, supRes] = await Promise.all([
        api.get('/api/import-orders/'),
        api.get('/api/products/'),
        api.get('/api/suppliers/'),
      ]);
      setOrders(ordRes.data);
      setProducts(prodRes.data);
      setSuppliers(supRes.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const addLine = () => setForm({ ...form, details: [...form.details, { product_id: '', quantity: 1, unit_price: 0 }] });
  const removeLine = (idx) => setForm({ ...form, details: form.details.filter((_, i) => i !== idx) });
  const updateLine = (idx, field, value) => {
    const newDetails = [...form.details];
    newDetails[idx] = { ...newDetails[idx], [field]: value };
    setForm({ ...form, details: newDetails });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = {
        supplier_id: Number(form.supplier_id),
        order_date: new Date(form.order_date).toISOString(),
        note: form.note,
        details: form.details.map(d => ({
          product_id: Number(d.product_id),
          quantity: Number(d.quantity),
          unit_price: Number(d.unit_price),
        })),
      };
      await api.post('/api/import-orders/', data);
      setShowModal(false);
      loadData();
    } catch (err) { alert(err.response?.data?.detail || 'Error'); }
  };

  const formatDate = (d) => new Date(d).toLocaleDateString('vi-VN');
  const formatMoney = (n) => new Intl.NumberFormat('vi-VN').format(n);

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Phiếu nhập kho / Import Orders</h1>
          <p className="page-subtitle">Quản lý nhập hàng vào kho / Manage warehouse imports</p>
        </div>
        <button className="btn btn-primary" onClick={() => {
          setForm({ supplier_id: suppliers[0]?.id || '', order_date: new Date().toISOString().split('T')[0], note: '', details: [{ product_id: products[0]?.id || '', quantity: 1, unit_price: 0 }] });
          setShowModal(true);
        }}>
          <Plus size={16} /> Tạo phiếu nhập / New Import
        </button>
      </div>

      <div className="data-table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Mã phiếu / Code</th>
              <th>Nhà cung cấp / Supplier</th>
              <th>Ngày nhập / Date</th>
              <th>Người tạo / Created By</th>
              <th>Tổng tiền / Total</th>
              <th>Trạng thái / Status</th>
              <th>Thao tác / Actions</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td><strong>{o.code}</strong></td>
                <td>{o.supplier_name}</td>
                <td>{formatDate(o.order_date)}</td>
                <td>{o.created_by_name}</td>
                <td>{formatMoney(o.total_amount)} đ</td>
                <td><span className="badge badge-green">Hoàn thành / Done</span></td>
                <td>
                  <button className="btn btn-ghost btn-sm" onClick={() => setShowDetail(o)}><Eye size={14} /> Chi tiết</button>
                </td>
              </tr>
            ))}
            {orders.length === 0 && <tr><td colSpan={7} className="empty-state"><ArrowDownToLine size={32} /><h3>Chưa có phiếu nhập / No import orders yet</h3></td></tr>}
          </tbody>
        </table>
      </div>

      {/* Create Modal / Tạo phiếu nhập */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" style={{ maxWidth: 750 }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Tạo phiếu nhập kho / New Import Order</h3>
              <button className="btn-ghost btn-icon" onClick={() => setShowModal(false)}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Nhà cung cấp / Supplier</label>
                    <select className="form-select" value={form.supplier_id} onChange={(e) => setForm({ ...form, supplier_id: e.target.value })} required>
                      {suppliers.map(s => <option key={s.id} value={s.id}>{s.code} - {s.name}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Ngày nhập / Import Date</label>
                    <input className="form-input" type="date" value={form.order_date} onChange={(e) => setForm({ ...form, order_date: e.target.value })} required />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Ghi chú / Notes</label>
                  <input className="form-input" value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} />
                </div>

                <label className="form-label" style={{ marginTop: 12 }}>Chi tiết phiếu nhập / Import Details</label>
                <table className="order-details-table">
                  <thead>
                    <tr>
                      <th>Sản phẩm / Product</th>
                      <th style={{ width: 100 }}>SL / Qty</th>
                      <th style={{ width: 140 }}>Đơn giá / Price</th>
                      <th style={{ width: 40 }}></th>
                    </tr>
                  </thead>
                  <tbody>
                    {form.details.map((d, idx) => (
                      <tr key={idx}>
                        <td>
                          <select className="form-select" value={d.product_id} onChange={(e) => updateLine(idx, 'product_id', e.target.value)} required>
                            <option value="">-- Chọn SP --</option>
                            {products.map(p => <option key={p.id} value={p.id}>{p.code} - {p.name}</option>)}
                          </select>
                        </td>
                        <td><input className="form-input" type="number" min="1" value={d.quantity} onChange={(e) => updateLine(idx, 'quantity', e.target.value)} required /></td>
                        <td><input className="form-input" type="number" min="0" value={d.unit_price} onChange={(e) => updateLine(idx, 'unit_price', e.target.value)} /></td>
                        <td>{form.details.length > 1 && <button type="button" className="btn btn-ghost btn-sm" onClick={() => removeLine(idx)} style={{ color: 'var(--accent-red)' }}>✕</button>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <button type="button" className="btn btn-secondary btn-sm" onClick={addLine} style={{ marginTop: 8 }}>
                  <Plus size={14} /> Thêm dòng / Add Line
                </button>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Hủy / Cancel</button>
                <button type="submit" className="btn btn-success">Tạo phiếu nhập / Create Import</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Detail Modal / Xem chi tiết */}
      {showDetail && (
        <div className="modal-overlay" onClick={() => setShowDetail(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Phiếu nhập {showDetail.code}</h3>
              <button className="btn-ghost btn-icon" onClick={() => setShowDetail(null)}>✕</button>
            </div>
            <div className="modal-body">
              <p><strong>NCC / Supplier:</strong> {showDetail.supplier_name}</p>
              <p><strong>Ngày / Date:</strong> {formatDate(showDetail.order_date)}</p>
              <p><strong>Người tạo / Created by:</strong> {showDetail.created_by_name}</p>
              {showDetail.note && <p><strong>Ghi chú / Note:</strong> {showDetail.note}</p>}
              <div style={{ marginTop: 16 }}>
                <table className="data-table">
                  <thead><tr><th>Sản phẩm</th><th>SL</th><th>Đơn giá</th><th>Thành tiền</th></tr></thead>
                  <tbody>
                    {showDetail.details.map((d, idx) => (
                      <tr key={idx}>
                        <td>{d.product_code} - {d.product_name}</td>
                        <td>{d.quantity}</td>
                        <td>{formatMoney(d.unit_price)} đ</td>
                        <td><strong>{formatMoney(d.quantity * d.unit_price)} đ</strong></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p style={{ marginTop: 12, textAlign: 'right', fontSize: 16 }}>
                <strong>Tổng / Total: {formatMoney(showDetail.total_amount)} đ</strong>
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
