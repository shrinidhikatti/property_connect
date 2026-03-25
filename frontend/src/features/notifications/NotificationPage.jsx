import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationsApi } from '../../api/conversations';
import { Link } from 'react-router-dom';

const TYPE_ICONS = {
  listing_approved: '✅',
  listing_rejected: '❌',
  changes_requested: '📝',
  new_inquiry: '💬',
  new_message: '✉️',
  contact_shared: '📞',
  verification_assigned: '🔍',
  system: 'ℹ️',
};

export default function NotificationPage() {
  const qc = useQueryClient();

  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsApi.list().then((r) => r.data),
  });

  const markAllMutation = useMutation({
    mutationFn: notificationsApi.markAllRead,
    onSuccess: () => {
      qc.invalidateQueries(['notifications']);
      qc.invalidateQueries(['notifications-unread']);
    },
  });

  const markOneMutation = useMutation({
    mutationFn: notificationsApi.markOneRead,
    onSuccess: () => {
      qc.invalidateQueries(['notifications']);
      qc.invalidateQueries(['notifications-unread']);
    },
  });

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="animate-pulse space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-16 bg-gray-100 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Notifications
          {unreadCount > 0 && (
            <span className="ml-2 text-sm font-normal bg-primary-500 text-white rounded-full px-2 py-0.5">
              {unreadCount} new
            </span>
          )}
        </h1>
        {unreadCount > 0 && (
          <button
            onClick={() => markAllMutation.mutate()}
            disabled={markAllMutation.isPending}
            className="text-sm text-primary-600 hover:underline disabled:opacity-50"
          >
            Mark all read
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <svg className="mx-auto h-12 w-12 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <p className="text-lg font-medium">No notifications yet</p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((notif) => {
            const convId = notif.data?.conversation_id;
            const content = (
              <div
                className={`flex gap-4 p-4 rounded-xl border transition-all cursor-pointer ${
                  notif.is_read
                    ? 'bg-white border-gray-100 text-gray-500'
                    : 'bg-primary-50 border-primary-100 text-gray-800'
                }`}
                onClick={() => !notif.is_read && markOneMutation.mutate(notif.id)}
              >
                <span className="text-2xl flex-shrink-0">{TYPE_ICONS[notif.notif_type] || 'ℹ️'}</span>
                <div className="flex-1 min-w-0">
                  <p className={`font-semibold text-sm ${notif.is_read ? 'text-gray-600' : 'text-gray-900'}`}>
                    {notif.title}
                    {!notif.is_read && <span className="ml-2 inline-block w-2 h-2 rounded-full bg-primary-500 align-middle" />}
                  </p>
                  <p className="text-sm mt-0.5 line-clamp-2">{notif.message}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(notif.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            );

            return convId ? (
              <Link key={notif.id} to={`/chat/${convId}`}>
                {content}
              </Link>
            ) : (
              <div key={notif.id}>{content}</div>
            );
          })}
        </div>
      )}
    </div>
  );
}
