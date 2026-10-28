/**
 * StockCard page - Trang Thẻ kho & Tra cứu lịch sử nhập xuất
 * Tra cứu theo hàng hóa, thời gian, nhà cung cấp (Yêu cầu mục 3.1 & 5 của Đề tài 07)
 */

import { useState, useEffect } from 'react';
import api from '../api/client';
import {
  ClipboardList, Search, Calendar, Filter,
  ArrowDownToLine, ArrowUpFromLine, Download, RefreshCw
} from 'lucide-react';

export default function StockCard() {
  const [products, setProducts] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [selectedSupplierId, setSelectedSupplierId] = useState('');

  const now = new Date();
  const past30Days = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  const [startDate, setStartDate] = useState(past30Days.toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(now.toISOString().split('T')[0]);

  const [stockCardData, setStockCardData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Load danh mục sản phẩm và nhà cung cấp
  useEffect(() => {
    const initData = async () => {
      try {
        const [prodRes, supRes] = await Promise.all([
          api.get('/api/products/'),
          api.get('/api/suppliers/'),
        ]);
        setProducts(prodRes.data);
        setSuppliers(supRes.data);
        if (prodRes.data.length > 0) {
          setSelectedProductId(prodRes.data[0].id);
        }
      } catch (err) {
        console.error('Lỗi tải danh mục ban đầu:', err);
      }
    };
    initData();
  }, []);

  // Tự động load thẻ kho khi đã có selectedProductId
  useEffect(() => {
    if (selectedProductId) {
      loadStockCard();
    }
  }, [selectedProductId]);

  const loadStockCard = async () => {
    if (!selectedProductId) return;
    setLoading(true);
    setErrorMsg('');
    try {
      let url = `/api/inventory/stock-card?product_id=${selectedProductId}&start_date=${startDate}&end_date=${endDate}`;
      if (selectedSupplierId) {
        url += `&supplier_id=${selectedSupplierId}`;
      }
      const res = await api.get(url);
      setStockCardData(res.data);
    } catch (err) {
      console.error('Lỗi tải thẻ kho:', err);
      setErrorMsg(err.response?.data?.detail || 'Không thể tải dữ liệu thẻ kho');
    } finally {
      setLoading(false);
    }
  };

  // Xuất file CSV Thẻ kho
  const exportStockCardCSV = () => {
    if (!stockCardData) return;

    const headers = [
      'STT',
      'Ngày chứng từ',
      'Mã chứng từ',
      'Loại giao dịch',
      'Đối tác (NCC/Người nhận)',
      'Số lượng nhập',
      'Số lượng xuất',
      'Tồn lũy kế',
      'Ghi chú / Lý do',
      'Người thực hiện'
    ];

    const rows = stockCardData.transactions.map((t, idx) => [
      idx + 1,
      new Date(t.date).toLocaleDateString('vi-VN'),
      t.document_code,
      t.order_type === 'import' ? 'Nhập kho' : 'Xuất kho',
      `"${(t.partner_name || '').replace(/"/g, '""')}"`,
      t.quantity_in || 0,
      t.quantity_out || 0,
      t.balance,
      `"${(t.note || '').replace(/"/g, '""')}"`,
      `"${(t.created_by_name || '').replace(/"/g, '""')}"`
    ]);

    const csvContent = [
      `THẺ KHO: ${stockCardData.product_code} - ${stockCardData.product_name}`,
      `Thời gian: ${startDate} đến ${endDate}`,
      `Tồn đầu kỳ: ${stockCardData.opening_balance} | Tổng nhập: ${stockCardData.total_import} | Tổng xuất: ${stockCardData.total_export} | Tồn cuối kỳ: ${stockCardData.closing_balance}`,
      '',
      headers.join(','),
      ...rows.map(r => r.join(','))
    ].join('\r\n');

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `The_kho_${stockCardData.product_code}_${startDate}_${endDate}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Thẻ kho & Lịch sử nhập xuất / Stock Card</h1>
          <p className="page-subtitle">
            Tra cứu biến động nhập xuất tồn chi tiết theo hàng hóa, thời gian và nhà cung cấp
          </p>
        </div>
        {stockCardData && (
          <button className="btn btn-secondary" onClick={exportStockCardCSV}>
            <Download size={16} /> Xuất Thẻ kho (CSV)
          </button>
        )}
      </div>

      {/* Bộ lọc tra cứu */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 16, alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div className="form-group" style={{ margin: 0, minWidth: 260 }}>
            <label className="form-label">Chọn Hàng Hóa / Product</label>
            <select
              className="form-input"
              value={selectedProductId}
              onChange={(e) => setSelectedProductId(Number(e.target.value))}
            >
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.code} - {p.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Từ ngày / From</label>
            <input
              className="form-input"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>

          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Đến ngày / To</label>
            <input
              className="form-input"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>

          <div className="form-group" style={{ margin: 0, minWidth: 220 }}>
            <label className="form-label">Nhà cung cấp / Supplier (Tùy chọn)</label>
            <select
              className="form-input"
              value={selectedSupplierId}
              onChange={(e) => setSelectedSupplierId(e.target.value)}
            >
              <option value="">-- Tất cả NCC & Xuất --</option>
              {suppliers.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <button className="btn btn-primary" onClick={loadStockCard} disabled={loading}>
            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
            {loading ? 'Đang tra cứu...' : 'Tra cứu / Search'}
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="alert alert-danger" style={{ marginBottom: 20 }}>
          {errorMsg}
        </div>
      )}

      {/* Thống kê thẻ kho */}
      {stockCardData && (
        <>
          <div className="stats-grid" style={{ marginBottom: 20 }}>
            <div className="stat-card">
              <div className="stat-card-icon blue"><ClipboardList size={22} /></div>
              <div>
                <div className="stat-card-value">{stockCardData.opening_balance}</div>
                <div className="stat-card-label">Tồn đầu kỳ / Opening Stock</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-card-icon green"><ArrowDownToLine size={22} /></div>
              <div>
                <div className="stat-card-value" style={{ color: 'var(--accent-green)' }}>
                  +{stockCardData.total_import}
                </div>
                <div className="stat-card-label">Tổng nhập trong kỳ / Imports</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-card-icon red"><ArrowUpFromLine size={22} /></div>
              <div>
                <div className="stat-card-value" style={{ color: 'var(--accent-red)' }}>
                  -{stockCardData.total_export}
                </div>
                <div className="stat-card-label">Tổng xuất trong kỳ / Exports</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-card-icon purple"><ClipboardList size={22} /></div>
              <div>
                <div className="stat-card-value">{stockCardData.closing_balance}</div>
                <div className="stat-card-label">Tồn cuối kỳ / Closing Stock</div>
              </div>
            </div>
          </div>

          {/* Bảng chi tiết dòng giao dịch thẻ kho */}
          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Ngày chứng từ</th>
                  <th>Mã chứng từ</th>
                  <th>Loại giao dịch</th>
                  <th>Đối tác / Người nhận</th>
                  <th>Nhập</th>
                  <th>Xuất</th>
                  <th>Tồn lũy kế</th>
                  <th>Người lập</th>
                  <th>Ghi chú</th>
                </tr>
              </thead>
              <tbody>
                {/* Dòng tồn đầu kỳ */}
                <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.03)', fontStyle: 'italic' }}>
                  <td>{startDate}</td>
                  <td><strong>---</strong></td>
                  <td><span className="badge badge-blue">Số dư đầu kỳ</span></td>
                  <td>Số dư mang sang</td>
                  <td>-</td>
                  <td>-</td>
                  <td><strong>{stockCardData.opening_balance}</strong></td>
                  <td>Hệ thống</td>
                  <td>Tồn kho trước ngày {startDate}</td>
                </tr>

                {stockCardData.transactions.length === 0 ? (
                  <tr>
                    <td colSpan={9} style={{ textAlign: 'center', padding: '30px 0', color: 'var(--text-muted)' }}>
                      Không có giao dịch nhập xuất nào trong khoảng thời gian này
                    </td>
                  </tr>
                ) : (
                  stockCardData.transactions.map((t, idx) => (
                    <tr key={idx}>
                      <td>{new Date(t.date).toLocaleDateString('vi-VN')} {new Date(t.date).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}</td>
                      <td><strong>{t.document_code}</strong></td>
                      <td>
                        {t.order_type === 'import' ? (
                          <span className="badge badge-green">
                            <ArrowDownToLine size={12} style={{ marginRight: 4 }} /> Nhập kho
                          </span>
                        ) : (
                          <span className="badge badge-red">
                            <ArrowUpFromLine size={12} style={{ marginRight: 4 }} /> Xuất kho
                          </span>
                        )}
                      </td>
                      <td>{t.partner_name}</td>
                      <td style={{ color: 'var(--accent-green)', fontWeight: t.quantity_in > 0 ? 600 : 'normal' }}>
                        {t.quantity_in > 0 ? `+${t.quantity_in}` : '-'}
                      </td>
                      <td style={{ color: 'var(--accent-red)', fontWeight: t.quantity_out > 0 ? 600 : 'normal' }}>
                        {t.quantity_out > 0 ? `-${t.quantity_out}` : '-'}
                      </td>
                      <td>
                        <strong style={{ fontSize: 14 }}>{t.balance}</strong>
                      </td>
                      <td>{t.created_by_name || 'N/A'}</td>
                      <td>{t.note || '-'}</td>
                    </tr>
                  ))
                )}

                {/* Dòng tồn cuối kỳ */}
                <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.04)', fontWeight: 600 }}>
                  <td colSpan={4} style={{ textAlign: 'right' }}>
                    TỔNG CỘNG PHÁT SINH & TỒN CUỐI KỲ:
                  </td>
                  <td style={{ color: 'var(--accent-green)' }}>+{stockCardData.total_import}</td>
                  <td style={{ color: 'var(--accent-red)' }}>-{stockCardData.total_export}</td>
                  <td style={{ fontSize: 15, color: 'var(--accent-blue)' }}>{stockCardData.closing_balance}</td>
                  <td colSpan={2}></td>
                </tr>
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
