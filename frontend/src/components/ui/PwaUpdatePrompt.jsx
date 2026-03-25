import { useRegisterSW } from 'virtual:pwa-register/react';

export default function PwaUpdatePrompt() {
  const {
    needRefresh: [needRefresh],
    updateServiceWorker,
  } = useRegisterSW({ immediate: true });

  if (!needRefresh) return null;

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 bg-gray-900 text-white px-5 py-3 rounded-xl shadow-lg flex items-center gap-4 text-sm">
      <span>A new version is available.</span>
      <button
        onClick={() => updateServiceWorker(true)}
        className="bg-primary-500 text-white px-3 py-1 rounded-lg font-medium hover:bg-primary-600 transition-colors"
      >
        Update
      </button>
    </div>
  );
}
