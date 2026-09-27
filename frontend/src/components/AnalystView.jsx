import React, { useState, useEffect, useRef } from 'react';
import { Bot, MessageSquare, AlertCircle, RefreshCw, Trash2 } from 'lucide-react';
import {
  createConversation,
  getConversations,
  getConversation,
  sendMessage,
  deleteConversation,
  getAnalystSuggestions,
} from '../services/api';
import { AnalystMessage } from './AnalystMessage';
import { AnalystInput } from './AnalystInput';
import { AnalystSuggestions } from './AnalystSuggestions';

export function AnalystView({ datasetId }) {
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [versionMismatch, setVersionMismatch] = useState(null);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversationsAndSuggestions = async () => {
    setLoading(true);
    setError(null);
    try {
      const [convs, suggs] = await Promise.all([
        getConversations(datasetId),
        getAnalystSuggestions(datasetId),
      ]);

      setConversations(convs || []);
      setSuggestions(suggs.suggestions || []);

      if (convs && convs.length > 0) {
        const fullConv = await getConversation(datasetId, convs[0].id);
        setActiveConversation(fullConv);
        setMessages(fullConv.messages || []);
      } else {
        const newConv = await createConversation(datasetId);
        setActiveConversation(newConv);
        setMessages(newConv.messages || []);
      }
    } catch (err) {
      setError(err.message || 'Failed to initialize analyst session.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversationsAndSuggestions();
  }, [datasetId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, sending]);

  const handleSendMessage = async (text) => {
    if (!activeConversation || sending) return;
    setSending(true);
    setError(null);
    setVersionMismatch(null);

    // Optimistic user message append
    const tempUserMsg = {
      id: 'temp-' + Date.now(),
      role: 'USER',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const assistantMsg = await sendMessage(datasetId, activeConversation.id, text);
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      if (err.code === 'ANALYST_DATASET_VERSION_MISMATCH') {
        setVersionMismatch('Dataset updated! Previous conversation turns were calculated on an older dataset version.');
      } else {
        setError(err.message || 'Failed to send message.');
      }
    } finally {
      setSending(false);
    }
  };

  const handleNewConversation = async () => {
    setLoading(true);
    setVersionMismatch(null);
    try {
      const newConv = await createConversation(datasetId);
      setActiveConversation(newConv);
      setMessages([]);
      const convs = await getConversations(datasetId);
      setConversations(convs || []);
    } catch (err) {
      setError(err.message || 'Failed to start new conversation.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteConversation = async (id) => {
    try {
      await deleteConversation(datasetId, id);
      await loadConversationsAndSuggestions();
    } catch (err) {
      setError(err.message || 'Failed to delete conversation.');
    }
  };

  return (
    <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', height: '80vh' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Bot size={24} color="#06b6d4" />
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>Natural-Language Data Analyst</h3>
            <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>Conversational, Evidence-Grounded Data Exploration</span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className="btn-secondary"
            onClick={handleNewConversation}
            style={{ fontSize: '0.8125rem', padding: '0.4rem 0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
          >
            <MessageSquare size={14} /> New Chat
          </button>
        </div>
      </div>

      {/* Version Mismatch / Error Banner */}
      {versionMismatch && (
        <div style={{ background: 'rgba(245, 158, 11, 0.15)', border: '1px solid #f59e0b', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', marginBottom: '1rem', color: '#fef3c7', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
            <AlertCircle size={18} color="#f59e0b" /> {versionMismatch}
          </div>
          <button className="btn-primary" onClick={handleNewConversation} style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}>
            Start Fresh Chat
          </button>
        </div>
      )}

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', marginBottom: '1rem', color: '#fca5a5' }}>
          {error}
        </div>
      )}

      {/* Chat Messages Body */}
      <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.5rem', marginBottom: '1rem' }}>
        {loading ? (
          <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Initializing analyst environment...
          </div>
        ) : messages.length === 0 ? (
          <div style={{ padding: '3rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            <Bot size={48} style={{ marginBottom: '1rem', opacity: 0.3 }} />
            <h4 style={{ color: '#f8fafc', fontWeight: 600, marginBottom: '0.5rem' }}>Ask Anything About Your Dataset</h4>
            <p style={{ fontSize: '0.875rem', maxWidth: 500, margin: '0 auto 1.5rem', lineHeight: 1.5 }}>
              VizMind's deterministic execution engine will compute exact answers and explain them using evidence-grounded AI.
            </p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <AnalystMessage
              key={msg.id || idx}
              message={msg}
              onOptionSelect={(opt) => handleSendMessage(opt)}
            />
          ))
        )}

        {sending && (
          <div style={{ display: 'flex', gap: '0.85rem', marginBottom: '1rem' }}>
            <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
              <Bot size={20} />
            </div>
            <div style={{ background: 'rgba(30, 41, 59, 0.7)', padding: '0.75rem 1.25rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              Computing deterministic query plan & evidence...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions Pills */}
      <AnalystSuggestions
        suggestions={suggestions}
        onSelectSuggestion={(s) => handleSendMessage(s)}
        disabled={sending || loading}
      />

      {/* Input Form */}
      <AnalystInput
        onSend={(t) => handleSendMessage(t)}
        loading={sending}
        disabled={loading}
      />
    </div>
  );
}
