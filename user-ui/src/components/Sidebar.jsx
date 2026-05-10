import { Plus, MessageSquare, Settings, User, LogOut, ChevronRight } from 'lucide-react';

const Sidebar = () => {
  // Dữ liệu mẫu để hiển thị danh sách chat
  const recentChats = [
    { id: 1, title: 'General Questions', snippet: 'How can I help you today?', time: '2 min ago' },
    { id: 2, title: 'Product Information', snippet: 'What would you like to know?', time: '1 hour ago' },
    { id: 3, title: 'Technical Support', snippet: 'I can help with that issue', time: 'Yesterday' },
  ];

  return (
    <aside className="w-72 h-screen bg-[#0B0F1A] text-slate-300 flex flex-col border-r border-slate-800/50 shrink-0">
      
      {/* 1. Header with Logo/Title */}
      <div className="p-6">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white shadow-lg shadow-blue-600/30">
            <MessageSquare size={18} fill="currentColor" />
          </div>
          <h1 className="text-lg font-bold text-white tracking-tight">RAGPlan</h1>
        </div>

        {/* 2. Nút New Chat */}
        <button className="w-full py-2.5 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl flex items-center justify-center gap-2 font-semibold transition-all duration-300 shadow-xl shadow-blue-900/40 active:scale-[0.98]">
          <Plus size={18} strokeWidth={2.5} />
          New Chat
        </button>
      </div>

      {/* 3. Danh sách Recent Conversations */}
      <div className="flex-1 overflow-y-auto px-3 py-2 custom-scrollbar">
        <div className="flex items-center justify-between px-3 mb-4">
            <h2 className="text-[11px] font-bold text-slate-500 uppercase tracking-[0.1em]">
            Recent Conversations
            </h2>
        </div>
        
        <div className="space-y-1">
          {recentChats.map((chat) => (
            <div 
              key={chat.id} 
              className="group p-3 rounded-xl hover:bg-slate-800/40 cursor-pointer transition-all duration-200 border border-transparent hover:border-slate-800"
            >
              <div className="flex items-start gap-3">
                <div className="mt-1 p-1.5 rounded-lg bg-slate-800/50 text-slate-500 group-hover:text-blue-400 group-hover:bg-blue-400/10 transition-colors">
                    <MessageSquare size={14} />
                </div>
                <div className="flex-1 overflow-hidden">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-slate-200 truncate group-hover:text-white">{chat.title}</h3>
                  </div>
                  <p className="text-xs text-slate-500 truncate mt-0.5">{chat.snippet}</p>
                </div>
                <ChevronRight size={14} className="mt-1 text-slate-700 group-hover:text-slate-500 transition-colors opacity-0 group-hover:opacity-100" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 4. Phần dưới cùng: Settings & User */}
      <div className="p-4 bg-[#0B0F1A]/80 backdrop-blur-md border-t border-slate-800/50 space-y-3">
        <button className="flex items-center gap-3 w-full p-2.5 hover:bg-slate-800/50 rounded-xl transition-all text-sm font-medium text-slate-400 hover:text-slate-200">
          <Settings size={18} />
          <span>Settings</span>
        </button>

        <div className="flex items-center gap-3 p-3 bg-slate-800/20 rounded-2xl border border-slate-800/30 hover:border-slate-700 transition-colors cursor-pointer group">
          <div className="relative">
            <div className="w-10 h-10 bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold text-sm shadow-inner">
                U
            </div>
            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 border-2 border-[#0B0F1A] rounded-full"></div>
          </div>
          <div className="flex-1 overflow-hidden text-left">
            <h4 className="font-bold text-slate-200 truncate text-sm">User Name</h4>
            <p className="text-[10px] text-slate-500 truncate font-medium">user@example.com</p>
          </div>
          <LogOut size={16} className="text-slate-600 hover:text-red-400 transition-colors" />
        </div>
      </div>

    </aside>
  );
};

export default Sidebar;

