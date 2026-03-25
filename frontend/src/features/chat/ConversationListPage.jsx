import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { conversationsApi } from '../../api/conversations';
import { useAuthStore } from '../../store/authStore';

function formatTime(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const now = new Date();
  const diffDays = Math.floor((now - d) / 86400000);
  if (diffDays === 0) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  if (diffDays === 1) return 'Yesterday';
  return d.toLocaleDateString();
}

export default function ConversationListPage() {
  const { user } = useAuthStore();
  const { data: conversations = [], isLoading } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => conversationsApi.list().then((r) => r.data),
  });

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-gray-100 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Messages</h1>

      {conversations.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <svg className="mx-auto h-12 w-12 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <p className="text-lg font-medium">No conversations yet</p>
          <p className="text-sm mt-1">Enquire on a property to start chatting</p>
        </div>
      ) : (
        <div className="space-y-2">
          {conversations.map((conv) => (
            <Link
              key={conv.id}
              to={`/chat/${conv.id}`}
              className="flex items-center gap-4 p-4 bg-white border border-gray-200 rounded-xl hover:border-primary-500 hover:shadow-sm transition-all"
            >
              {/* Avatar */}
              <div className="w-12 h-12 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-semibold text-lg flex-shrink-0">
                {conv.other_party_name?.[0]?.toUpperCase() || '?'}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-baseline">
                  <p className="font-semibold text-gray-900 truncate">{conv.other_party_name}</p>
                  <span className="text-xs text-gray-400 ml-2 flex-shrink-0">
                    {formatTime(conv.last_message_at)}
                  </span>
                </div>
                <p className="text-sm text-gray-500 truncate mt-0.5">{conv.property_title}</p>
                {conv.last_message && (
                  <p className="text-sm text-gray-400 truncate mt-0.5">{conv.last_message}</p>
                )}
              </div>

              {conv.unread_count > 0 && (
                <span className="ml-2 bg-primary-500 text-white text-xs font-bold rounded-full h-5 min-w-[20px] flex items-center justify-center px-1.5 flex-shrink-0">
                  {conv.unread_count}
                </span>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
