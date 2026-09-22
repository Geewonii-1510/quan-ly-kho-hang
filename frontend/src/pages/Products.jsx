/**
 * Products page - Trang quản lý sản phẩm
 * CRUD with search, categories, and stock status
 */

import { useState, useEffect } from 'react';
import api from '../api/client';
import { Plus, Search, Edit2, Trash2, Package } from 'lucide-react';

export default function Products() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [units, setUnits] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editProduct, setEditProduct] = useState(null);
  const [form, setForm] = useState({ code: '', name: '', category_id: '', unit_id: '', min_stock: 0, description: '' });

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [prodRes, catRes, unitRes] = await Promise.all([
        api.get('/api/products/'),
        api.get('/api/products/categories'),
        api.get('/api/products/units'),
      ]);
      setProducts(prodRes.data);
      setCategories(catRes.data);
      setUnits(unitRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = products.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.code.toLowerCase().includes(search.toLowerCase())
  );

  const openCreate = () => {
    setEditProduct(null);
    setForm({ code: '', name: '', category_id: categories[0]?.id || '', unit_id: units[0]?.id || '', min_stock: 0, description: '' });
    setShowModal(true);
  };

  const openEdit = (p) => {
    setEditProduct(p);
    setForm({ code: p.code, name: p.name, category_id: p.category_id, unit_id: p.unit_id, min_stock: p.min_stock, description: p.description || '' });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = { ...form, category_id: Number(form.category_id), unit_id: Number(form.unit_id), min_stock: Number(form.min_stock) };
      if (editProduct) {
        await api.put(`/api/products/${editProduct.id}`, data);
      } else {
        await api.post('/api/products/', data);
      }
      setShowModal(false);
      loadData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Vô hiệu hóa sản phẩm này? / Deactivate this product?')) return;
    try {
      await api.delete(`/api/products/${id}`);
      loadData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error');
    }
  };

  const getStockBadge = (status) => {
    if (status === 'out_of_stock') return <span className="badge badge-red">Hết hàng / Out</span>;
    if (status === 'low') return <span className="badge badge-orange">Tồn thấp / Low</span>;
    return <span className="badge badge-green">Bình thường / OK</span>;
  };

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Sản phẩm / Products</h1>
          <p className="page-subtitle">Quản lý danh mục sản phẩm hàng hóa / Manage product catalog</p>
        </div>
        <button className="btn btn-primary" onClick={openCreate}>
          <Plus size={16} /> Thêm mới / Add New
        </button>
      </div>

      <div className="toolbar">
        <div className="search-box">
          <Search />
          <input placeholder="Tìm kiếm sản phẩm... / Search products..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <div className="toolbar-spacer" />
        <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>{filtered.length} sản phẩm / products</span>
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
              <th>Trạng thái / Status</th>
              <th>Thao tác / Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((p) => (
              <tr key={p.id} className={p.stock_status !== 'normal' ? 'alert-row' : ''}>
                <td><strong>{p.code}</strong></td>
                <td>{p.name}</td>
                <td>{p.category?.name || ''}</td>
                <td>{p.unit?.abbreviation || ''}</td>
                <td><strong>{p.current_stock}</strong></td>
                <td>{p.min_stock}</td>
                <td>{getStockBadge(p.stock_status)}</td>
                <td>
                  <div style={{ display: 'flex', gap: 4 }}>
                    <button className="btn btn-ghost btn-sm" onClick={() => openEdit(p)}><Edit2 size={14} /></button>
                    <button className="btn btn-ghost btn-sm" onClick={() => handleDelete(p.id)} style={{ color: 'var(--accent-red)' }}><Trash2 size={14} /></button>
                  </div>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={8} className="empty-state"><Package size={32} /><h3>Không tìm thấy sản phẩm / No products found</h3></td></tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal / Hộp thoại */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">{editProduct ? 'Sửa sản phẩm / Edit Product' : 'Thêm sản phẩm / Add Product'}</h3>
              <button className="btn-ghost btn-icon" onClick={() => setShowModal(false)}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Mã SP / Code</label>
                    <input className="form-input" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} required disabled={!!editProduct} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Tồn tối thiểu / Min Stock</label>
                    <input className="form-input" type="number" min="0" value={form.min_stock} onChange={(e) => setForm({ ...form, min_stock: e.target.value })} />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Tên SP / Product Name</label>
                  <input className="form-input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Danh mục / Category</label>
                    <select className="form-select" value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })} required>
                      {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Đơn vị tính / Unit</label>
                    <select className="form-select" value={form.unit_id} onChange={(e) => setForm({ ...form, unit_id: e.target.value })} required>
                      {units.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Mô tả / Description</label>
                  <textarea className="form-textarea" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Hủy / Cancel</button>
                <button type="submit" className="btn btn-primary">{editProduct ? 'Cập nhật / Update' : 'Thêm / Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
