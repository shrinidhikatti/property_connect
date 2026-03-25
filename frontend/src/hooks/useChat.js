import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuthStore } from '../store/authStore';

const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8001';

export function useChat(conversationId) {
  const { accessToken } = useAuthStore();
  const ws = useRef(null);
  const [messages, setMessages] = useState([]);
  const [connected, setConnected] = useState(false);
  const [typingUser, setTypingUser] = useState(null);
  const typingTimer = useRef(null);

  useEffect(() => {
    if (!conversationId || !accessToken) return;

    const url = `${WS_BASE}/ws/chat/${conversationId}/?token=${accessToken}`;
    ws.current = new WebSocket(url);

    ws.current.onopen = () => setConnected(true);
    ws.current.onclose = () => setConnected(false);

    ws.current.onmessage = (e) => {
      const data = JSON.parse(e.data);

      if (data.type === 'chat_message') {
        setMessages((prev) => [...prev, data.message]);
      } else if (data.type === 'typing_indicator') {
        setTypingUser(data.username || null);
        clearTimeout(typingTimer.current);
        typingTimer.current = setTimeout(() => setTypingUser(null), 3000);
      } else if (data.type === 'read_receipt') {
        setMessages((prev) =>
          prev.map((m) => (m.id === data.message_id ? { ...m, is_read: true } : m))
        );
      } else if (data.type === 'error') {
        console.error('WS error:', data.message);
      }
    };

    return () => {
      ws.current?.close();
      clearTimeout(typingTimer.current);
    };
  }, [conversationId, accessToken]);

  const sendMessage = useCallback((content) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'chat_message', content }));
    }
  }, []);

  const sendTyping = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'typing_indicator' }));
    }
  }, []);

  const sendReadReceipt = useCallback((messageId) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'read_receipt', message_id: messageId }));
    }
  }, []);

  return { messages, setMessages, connected, typingUser, sendMessage, sendTyping, sendReadReceipt };
}
