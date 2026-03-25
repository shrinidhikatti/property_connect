import { useEffect, useRef, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { conversationsApi } from '../../api/conversations';
import { useAuthStore } from '../../store/authStore';
import { useChat } from '../../hooks/useChat';
import { useToastStore } from '../../components/ui/Toast';

export default function ChatPage() {
  const { id } = useParams();
  const { user } = useAuthStore();
  const { addToast } = useToastStore();
  const qc = useQueryClient();
  const bottomRef = useRef(null);
  const [input, setInput] = useState('');

  // Load conversation detail + history
  const { data: conv, isLoading: loadingConv } = useQuery({
    queryKey: ['conversation', id],
    queryFn: () => conversationsApi.get(id).then((r) => r.data),
  });

  const { data: history = [], isLoading: loadingMsgs } = useQuery({
    queryKey: ['messages', id],
    queryFn: () => conversationsApi.messages(id).then((r) => r.data),
  });

  const { messages: wsMessages, setMessages, connected, typingUser, sendMessage, sendTyping, sendReadReceipt } =
    useChat(id);

  // Merge history + live messages
  const allMessages = [
    ...history,
    ...wsMessages.filter((m) => !history.find((h) => h.id === m.id)),
  ];

  // Mark last message read on load
  useEffect(() => {
    const last = history[history.length - 1];
    if (last && last.sender_id !== user?.id) {
      sendReadReceipt(last.id);
    }
  }, [history]);

  // Scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [allMessages.length]);

  const shareContactMutation = useMutation({
    mutationFn: () => conversationsApi.shareContact(id),
    onSuccess: () => {
      qc.invalidateQueries(['conversation', id]);
      addToast('Contact details shared with buyer.', 'success');
    },
  });

  const handleSend = (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;
    sendMessage(text);
    setInput('');
  };

  const handleTyping = (e) => {
    setInput(e.target.value);
    sendTyping();
  };

  if (loadingConv || loadingMsgs) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-64px)]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500" />
      </div>
    );
  }

  const isSeller = user?.id === conv?.seller_id;

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b bg-white shadow-sm">
        <Link to="/chat" className="text-gray-400 hover:text-gray-600">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </Link>
        <div className="w-9 h-9 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-semibold">
          {conv?.other_party_name?.[0]?.toUpperCase() || '?'}
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-gray-900 truncate">{conv?.other_party_name}</p>
          <p className="text-xs text-gray-400 truncate">{conv?.property_title}</p>
        </div>
        <div className={`h-2 w-2 rounded-full ${connected ? 'bg-green-400' : 'bg-gray-300'}`} title={connected ? 'Connected' : 'Disconnected'} />
      </div>

      {/* Contact share banner */}
      {isSeller && !conv?.contact_shared && (
        <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 flex items-center justify-between text-sm">
          <span className="text-amber-700">Share your contact to let the buyer reach you directly.</span>
          <button
            onClick={() => shareContactMutation.mutate()}
            disabled={shareContactMutation.isPending}
            className="ml-3 text-amber-800 font-semibold hover:underline disabled:opacity-50"
          >
            Share Contact
          </button>
        </div>
      )}

      {conv?.contact_shared && (
        <div className="bg-green-50 border-b border-green-200 px-4 py-2 text-sm text-green-700">
          Contact details have been shared.
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-gray-50">
        {allMessages.length === 0 && (
          <p className="text-center text-gray-400 text-sm py-8">No messages yet. Say hello!</p>
        )}
        {allMessages.map((msg) => {
          const isOwn = msg.sender_id === user?.id || msg.sender === user?.id;
          return (
            <div key={msg.id} className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[75%] px-4 py-2 rounded-2xl text-sm leading-relaxed ${
                  isOwn
                    ? 'bg-primary-500 text-white rounded-br-sm'
                    : 'bg-white text-gray-800 border border-gray-200 rounded-bl-sm shadow-sm'
                }`}
              >
                <p>{msg.masked_content || msg.content}</p>
                <p className={`text-[10px] mt-1 ${isOwn ? 'text-primary-100' : 'text-gray-400'}`}>
                  {new Date(msg.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  {isOwn && msg.is_read && ' ✓✓'}
                </p>
              </div>
            </div>
          );
        })}

        {typingUser && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-2 text-sm text-gray-400 shadow-sm">
              {typingUser} is typing…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="flex items-center gap-2 px-4 py-3 bg-white border-t">
        <input
          type="text"
          value={input}
          onChange={handleTyping}
          placeholder="Type a message…"
          className="flex-1 border border-gray-200 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
        />
        <button
          type="submit"
          disabled={!input.trim() || !connected}
          className="w-10 h-10 bg-primary-500 text-white rounded-full flex items-center justify-center hover:bg-primary-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <svg className="w-4 h-4 rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </form>
    </div>
  );
}
