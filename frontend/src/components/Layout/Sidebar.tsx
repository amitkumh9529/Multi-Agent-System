import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useThreads, useDeleteThread } from '../../services/threads';

const navigation = [
  { name: 'Knowledge Bases', href: '/kb', icon: '📚' },
  { name: 'Prompts', href: '/prompts', icon: '📝' },
  { name: 'Agents', href: '/agents', icon: '🤖' },
  { name: 'Teams', href: '/teams', icon: '👥' },
];

export default function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { data: threads, isLoading } = useThreads();
  const deleteThread = useDeleteThread();

  const handleDeleteThread = async (e: React.MouseEvent, threadId: string) => {
    e.preventDefault(); // Prevent navigation
    if (window.confirm('Are you sure you want to delete this chat?')) {
      await deleteThread.mutateAsync(threadId);
      if (location.pathname === `/chat/${threadId}`) {
        navigate('/chat');
      }
    }
  };

  // Sort threads by updated_at descending (newest first)
  const sortedThreads = [...(threads || [])].sort((a, b) => {
    const dateA = new Date(a.updated_at || a.created_at).getTime();
    const dateB = new Date(b.updated_at || b.created_at).getTime();
    return dateB - dateA;
  });

  return (
    <div className={`flex h-full flex-col bg-gray-900 text-white transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-64'}`}>
      <div className={`flex h-16 items-center border-b border-gray-800 ${isCollapsed ? 'justify-center' : 'justify-between px-5'}`}>
        {!isCollapsed && (
          <Link to="/" className="text-xl font-bold hover:text-gray-300 transition-colors truncate">
            MAS Platform
          </Link>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1 rounded hover:bg-gray-800 text-gray-400 hover:text-white transition-colors flex-shrink-0"
          title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {isCollapsed ? (
            <svg className="w-5 h-5 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" /></svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" /></svg>
          )}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-4">
        {/* Main Navigation */}
        <nav className="space-y-1 mb-6">
          {navigation.map((item) => {
            const isActive = location.pathname.startsWith(item.href);
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center rounded-lg py-2 text-sm font-medium transition-colors ${isCollapsed ? 'justify-center px-0' : 'gap-3 px-3'} ${isActive
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  }`}
                title={isCollapsed ? item.name : undefined}
              >
                <span className="text-lg flex-shrink-0">{item.icon}</span>
                {!isCollapsed && <span className="truncate">{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Recent Chats Section */}
        <div className="pt-4 border-t border-gray-800">
          <Link
            to="/chat"
            className={`flex items-center rounded-lg py-2 mb-4 text-sm font-medium transition-colors ${isCollapsed ? 'justify-center px-0' : 'gap-3 px-3'} ${location.pathname === '/chat'
              ? 'bg-primary-600 text-white'
              : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            title={isCollapsed ? "New Chat" : undefined}
          >
            <span className="text-lg flex-shrink-0">💬</span>
            {!isCollapsed && <span>New Chat</span>}
          </Link>

          {!isCollapsed && (
            <>
              <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Recent Chats
              </h3>
              <div className="space-y-1">
                {isLoading ? (
                  <div className="px-3 text-gray-500 text-sm">Loading...</div>
                ) : sortedThreads.length === 0 ? (
                  <div className="px-3 text-gray-500 text-sm">No recent chats</div>
                ) : (
                  sortedThreads.map((thread) => {
                    const isActive = location.pathname === `/chat/${thread.thread_id}`;
                    return (
                      <Link
                        key={thread.thread_id}
                        to={`/chat/${thread.thread_id}`}
                        className={`group flex items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors ${isActive
                          ? 'bg-gray-800 text-white'
                          : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                          }`}
                      >
                        <div className="truncate flex-1" title={thread.title || 'Untitled Chat'}>
                          {thread.title || 'Untitled Chat'}
                        </div>
                        <button
                          onClick={(e) => handleDeleteThread(e, thread.thread_id)}
                          className={`ml-2 opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 transition-opacity ${deleteThread.isPending ? 'cursor-wait' : ''
                            }`}
                          title="Delete Chat"
                        >
                          ×
                        </button>
                      </Link>
                    );
                  })
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

