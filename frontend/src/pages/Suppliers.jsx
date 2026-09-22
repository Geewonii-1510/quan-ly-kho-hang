/**
 * Suppliers page - Trang quản lý nhà cung cấp
 */

import { useState, useEffect } from 'react';
import api from '../api/client';
import { Plus, Search, Edit2, Trash2, Truck } from 'lucide-react';

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [form, setForm] = useState({ code: '', name: '', contact_person: '', phone: '', email: '', address: '' });

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const res = await api.get('/api/suppliers/');
      setSuppliers(res.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const filtered = suppliers.filter(s =>
    s.name.toLowerCase().includes(search.toLowerCase()) ||
    s.code.toLowerCase().includes(search.toLowerCase())
  );

  const openCreate = () => {
    setEditItem(null);
    setForm({ code: '', name: '', contact_person: '', phone: '', email: '', address: '' });
    setShowModal(true);
  };

  const openEdit = (s) => {
    setEditItem(s);
    setForm({ code: s.code, name: s.name, contact_person: s.contact_person || '', phone: s.phone || '', email: s.email || '', address: s.address || '' });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editItem) {
        await api.put(`/api/suppliers/${editItem.id}`, form);
      } else {
        await api.post('/api/suppliers/', form);
      }
      setShowModal(false);
      loadData();
    } catch (err) { alert(err.response?.data?.detail || 'Error'); }
  };

  const handleDelete = async (id) => {
    if (!confirm('Vô hiệu hóa NCC? / Deactivate this supplier?')) return;
    try { await api.delete(`/api/suppliers/${id}`); loadData(); }
    catch (err) { alert(err.response?.data?.detail || 'Error'); }
  };

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Nhà cung cấp / Suppliers</h1>
          <p className="page-subtitle">Quản lý thông tin nhà cung cấp / Manage supplier information</p>
        </div>
        <button className="btn btn-primary" onClick={openCreate}><Plus size={16} /> Thêm mới / Add New</button>
      </div>

      <div className="toolbar">
        <div className="search-box"><Search /><input placeholder="Tìm kiếm NCC..." value={search} onChange={(e) => setSearch(e.target.value)} /></div>
        <div className="toolbar-spacer" />
        <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>{filtered.length} nhà cung cấp / suppliers</span>
      </div>

      <div className="data-table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Mã NCC / Code</th>
              <th>Tên NCC / Supplier Name</th>
              <th>Người LH / Contact</th>
              <th>Điện thoại / Phone</th>
              <th>Email</th>
              <th>Trạng thái / Status</th>
              <th>Thao tác / Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((s) => (
              <tr key={s.id}>
                <td><strong>{s.code}</strong></td>
                <td>{s.name}</td>
                <td>{s.contact_person}</td>
                <td>{s.phone}</td>
                <td>{s.email}</td>
                <td><span className={`badge ${s.is_active ? 'badge-green' : 'badge-red'}`}>{s.is_active ? 'Hoạt động / Active' : 'Ngừng / Inactive'}</span></td>
                <td>
                  <div style={{ display: 'flex', gap: 4 }}>
                    <button className="btn btn-ghost btn-sm" onClick={() => openEdit(s)}><Edit2 size={14} /></button>
                    <button className="btn btn-ghost btn-sm" onClick={() => handleDelete(s.id)} style={{ color: 'var(--accent-red)' }}><Trash2 size={14} /></button>
                  </div>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && <tr><td colSpan={7} className="empty-state"><Truck size={32} /><h3>Không tìm thấy NCC / No suppliers found</h3></td></tr>}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">{editItem ? 'Sửa NCC / Edit Supplier' : 'Thêm NCC / Add Supplier'}</h3>
              <button className="btn-ghost btn-icon" onClick={() => setShowModal(false)}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-row">
                  <div className="form-group"><label className="form-label">Mã NCC / Code</label><input className="form-input" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} required disabled={!!editItem} /></div>
                  <div className="form-group"><label className="form-label">Người LH / Contact</label><input className="form-input" value={form.contact_person} onChange={(e) => setForm({ ...form, contact_person: e.target.value })} /></div>
                </div>
                <div className="form-group"><label className="form-label">Tên NCC / Supplier Name</label><input className="form-input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></div>
                <div className="form-row">
                  <div className="form-group"><label className="form-label">Điện thoại / Phone</label><input className="form-input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></div>
                  <div className="form-group"><label className="form-label">Email</label><input className="form-input" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></div>
                </div>
                <div className="form-group"><label className="form-label">Địa chỉ / Address</label><textarea className="form-textarea" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} /></div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Hủy / Cancel</button>
                <button type="submit" className="btn btn-primary">{editItem ? 'Cập nhật / Update' : 'Thêm / Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
