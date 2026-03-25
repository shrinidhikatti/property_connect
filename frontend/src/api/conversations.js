import api from './client';

export const conversationsApi = {
  list: () => api.get('/conversations/'),
  get: (id) => api.get(`/conversations/${id}/`),
  start: (propertyId) => api.post('/conversations/start/', { property_id: propertyId }),
  messages: (id) => api.get(`/conversations/${id}/messages/`),
  shareContact: (id) => api.post(`/conversations/${id}/share_contact/`),
};

export const notificationsApi = {
  list: () => api.get('/notifications/'),
  unreadCount: () => api.get('/notifications/unread-count/'),
  markAllRead: () => api.post('/notifications/mark-all-read/'),
  markOneRead: (id) => api.patch(`/notifications/${id}/read/`),
};
