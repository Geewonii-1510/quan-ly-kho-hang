/**
 * AI Assistant page - Trang trợ lý AI
 * Full chat interface with free-form questions and quick suggestions
 * Giao diện chat đầy đủ với câu hỏi tự do và gợi ý nhanh
 */

import { useState, useEffect, useRef } from 'react';
import api from '../api/client';
import Markdown from 'react-markdown';
import {
  Bot, Send, Sparkles, Trash2, User,
  FileText, ShoppingCart, AlertTriangle,
} from 'lucide-react';

const STORAGE_KEY = 'wms_ai_chat_history';

const QUICK_SUGGESTIONS = [
  {
    icon: FileText,
    label: 'Báo cáo kho',
    message: 'Hãy tạo báo cáo tổng quan tình trạng kho hàng hiện tại, bao gồm sản phẩm cần chú ý và nhận xét.',
  },
  {
    icon: ShoppingCart,
    label: 'Gợi ý nhập hàng',
    message: 'Sản phẩm nào cần nhập hàng gấp? Hãy gợi ý số lượng và sắp xếp theo mức độ ưu tiên.',
  },
  {
    icon: AlertTriangle,
    label: 'Phát hiện bất thường',
    message: 'Phân tích và phát hiện các biến động bất thường trong kho hàng, bao gồm xuất đột biến, hàng tồn lâu.',
  },
];

export default function AIAssistant() {
  /* ---------- State ---------- */
  const [messages, setMessages] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  /* ---------- Persist to localStorage ---------- */
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  /* ---------- Auto-scroll to bottom ---------- */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  /* ---------- Auto-resize textarea ---------- */
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  }, [input]);

  /* ---------- Send message ---------- */
  const sendMessage = async (text) => {
    const trimmed = (text || input).trim();
    if (!trimmed || loading) return;

    const userMsg = { role: 'user', content: trimmed };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      // Gửi tối đa 10 tin nhắn gần nhất làm lịch sử (tránh payload quá lớn)
      const history = newMessages.slice(-10).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res = await api.post('/api/ai/chat', {
        message: trimmed,
        history: history.slice(0, -1), // Không gửi tin nhắn hiện tại trong history
      });

      const botMsg = {
        role: 'model',
        content: res.data.reply,
        generated_at: res.data.generated_at,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errorMsg = {
        role: 'model',
        content:
          '⚠️ **Lỗi:** ' +
          (err.response?.data?.detail ||
            'Không thể kết nối AI. Vui lòng kiểm tra GEMINI_API_KEY trong file backend/.env'),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  };

  /* ---------- Handle keyboard ---------- */
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  /* ---------- Clear chat ---------- */
  const clearChat = () => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  /* ---------- Render ---------- */
  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Trợ lý AI / AI Assistant</h1>
          <p className="page-subtitle">
            Chat trực tiếp với AI để phân tích kho hàng
          </p>
        </div>
        {messages.length > 0 && (
          <button className="btn btn-secondary" onClick={clearChat}>
            <Trash2 size={16} />
            Xóa chat
          </button>
        )}
      </div>

      <div className="ai-chat-container">
        {/* Header */}
        <div className="ai-panel-header">
          <Sparkles size={20} />
          <h3>AI Warehouse Analyst — Powered by Google Gemini</h3>
        </div>

        {/* Messages Area */}
        <div className="chat-messages">
          {messages.length === 0 && !loading && (
            <div className="chat-welcome">
              <div className="chat-welcome-icon">
                <Bot size={48} />
              </div>
              <h3>Xin chào! Tôi là trợ lý AI kho hàng</h3>
              <p>
                Hãy hỏi bất kỳ câu hỏi nào về kho hàng, hoặc chọn một gợi ý
                bên dưới để bắt đầu.
              </p>

              {/* Quick suggestions */}
              <div className="chat-suggestions">
                {QUICK_SUGGESTIONS.map((s, i) => {
                  const Icon = s.icon;
                  return (
                    <button
                      key={i}
                      className="chat-suggestion-chip"
                      onClick={() => sendMessage(s.message)}
                    >
                      <Icon size={16} />
                      <span>{s.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`chat-bubble-row ${msg.role === 'user' ? 'user' : 'bot'}`}
            >
              {msg.role !== 'user' && (
                <div className="chat-avatar bot-avatar">
                  <Bot size={18} />
                </div>
              )}
              <div
                className={`chat-bubble ${msg.role === 'user' ? 'user' : 'bot'} ${msg.isError ? 'error' : ''}`}
              >
                {msg.role === 'user' ? (
                  <p>{msg.content}</p>
                ) : (
                  <div className="markdown-content">
                    <Markdown>{msg.content}</Markdown>
                  </div>
                )}
                {msg.generated_at && (
                  <span className="chat-time">
                    {new Date(msg.generated_at).toLocaleTimeString('vi-VN', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="chat-avatar user-avatar">
                  <User size={18} />
                </div>
              )}
            </div>
          ))}

          {/* Typing indicator */}
          {loading && (
            <div className="chat-bubble-row bot">
              <div className="chat-avatar bot-avatar">
                <Bot size={18} />
              </div>
              <div className="chat-bubble bot">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick suggestion chips (shown when messages exist) */}
        {messages.length > 0 && (
          <div className="chat-suggestions-bar">
            {QUICK_SUGGESTIONS.map((s, i) => {
              const Icon = s.icon;
              return (
                <button
                  key={i}
                  className="chat-suggestion-chip small"
                  onClick={() => sendMessage(s.message)}
                  disabled={loading}
                >
                  <Icon size={14} />
                  <span>{s.label}</span>
                </button>
              );
            })}
          </div>
        )}

        {/* Input area */}
        <div className="chat-input-area">
          <textarea
            ref={textareaRef}
            className="chat-textarea"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhập câu hỏi về kho hàng... (Enter để gửi, Shift+Enter xuống dòng)"
            rows={1}
            disabled={loading}
          />
          <button
            className="chat-send-btn"
            onClick={() => sendMessage()}
            disabled={!input.trim() || loading}
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
