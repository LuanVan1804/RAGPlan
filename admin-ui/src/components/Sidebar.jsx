import { FileText, User, LayoutDashboard, Plus } from 'lucide-react';

const Sidebar = ({ activePage, setActivePage }) => {
  const menuItems = [
    { id: 'add-documents', name: 'Thêm tài liệu', icon: Plus},
    { id: 'documents', name: 'Quản lý tài liệu', icon: FileText },
  ];

  return (
    <div className="w-72 h-screen bg-surface-950 text-white flex flex-col fixed left-0 top-0 border-r border-surface-900 shadow-2xl z-50">
      {/* Header */}
      <div className="p-8">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-8 h-8 bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg flex items-center justify-center shadow-glow-primary">
            <LayoutDashboard size={20} className="text-white" />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white">RAG<span className="text-primary-400">Plan</span></h1>
        </div>
        <p className="text-[10px] text-surface-500 font-semibold uppercase tracking-[0.2em]">Management Console</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-6 space-y-1.5">
        {menuItems.map((item) => {
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActivePage(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3.5 rounded-xl transition-all duration-300 group ${
                isActive 
                  ? 'bg-primary-600/10 text-primary-400 border border-primary-500/20 shadow-glow-primary/10' 
                  : 'text-surface-400 hover:bg-surface-900 hover:text-white border border-transparent'
              }`}
            >
              <item.icon size={20} className={isActive ? 'text-primary-400' : 'text-surface-500 group-hover:text-white transition-colors'} />
              <span className="font-semibold text-sm tracking-wide">{item.name}</span>
              {isActive && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary-400 shadow-glow-primary" />}
            </button>
          );
        })}
      </nav> 
    </div>
  );
};

export default Sidebar;
