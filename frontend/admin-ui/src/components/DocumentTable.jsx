import { Calendar, MapPin, MoreVertical, ExternalLink, FileText} from 'lucide-react';

const DocumentTable = ({ documents, loading }) => {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-32 space-y-6">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 border-4 border-primary-100 dark:border-primary-900/20 rounded-full" />
          <div className="absolute inset-0 border-4 border-primary-500 rounded-full border-t-transparent animate-spin" />
        </div>
        <p className="text-slate-500 dark:text-slate-400 font-medium animate-pulse">Loading documents...</p>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-32 bg-slate-50/50 dark:bg-surface-900/50 rounded-3xl border-2 border-dashed border-slate-200 dark:border-slate-800">
        <div className="w-16 h-16 bg-slate-100 dark:bg-surface-800 rounded-2xl flex items-center justify-center mx-auto mb-4 text-slate-400">
          <FileText size={32} strokeWidth={1.5} />
        </div>
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">No documents found</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 max-w-xs mx-auto mt-2">
          The RAG system is currently empty. Start by uploading some knowledge.
        </p>
      </div>
    );
  }

  return (
    <div className="card-premium overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50/50 dark:bg-surface-800/50 border-b border-slate-100 dark:border-slate-800">
              <th className="py-3 px-4 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-[0.15em]">Destination</th>
              <th className="py-3 px-4 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-[0.15em]">Category</th>
              <th className="py-3 px-4 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-[0.15em]">Preview Content</th>
              <th className="py-3 px-4 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-[0.15em]">Timestamp</th>
              <th className="py-3 px-4 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-[0.15em] text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50 dark:divide-slate-800/50">
            {documents.map((doc) => (
              <tr key={doc.doc_id} className="group hover:bg-slate-50/30 dark:hover:bg-primary-900/5 transition-all duration-300">
                <td className="py-3 px-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-7 h-7 bg-primary-50 dark:bg-primary-900/20 rounded-lg flex items-center justify-center text-primary-500 group-hover:scale-110 transition-transform">
                      <MapPin size={14} />
                    </div>
                    <span className="font-bold text-sm text-slate-900 dark:text-white capitalize tracking-tight">{doc.destination}</span>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 border border-indigo-100/50 dark:border-indigo-500/20">
                    {doc.category}
                  </span>
                </td>
                <td className="py-3 px-4 max-w-md">
                  <p className="text-xs text-slate-500 dark:text-slate-400 truncate leading-relaxed">
                    {doc.preview}
                  </p>
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center text-[10px] font-medium text-slate-400 dark:text-slate-500">
                    <Calendar size={12} className="mr-1.5 opacity-60" />
                    {new Date(doc.created_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </div>
                </td>
                <td className="py-3 px-4 text-right">
                  <div className="flex items-center justify-end space-x-1">
                    <button className="p-1.5 text-slate-400 hover:text-primary-500 dark:hover:text-primary-400 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all active:scale-90">
                      <ExternalLink size={14} />
                    </button>
                    <button className="p-1.5 text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-surface-700 transition-all active:scale-90">
                      <MoreVertical size={14} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Table Footer / Pagination Placeholder */}
      <div className="p-4 bg-slate-50/30 dark:bg-surface-900/30 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
        <p className="text-xs text-slate-400 font-medium">Showing {documents.length} entries</p>
        <div className="flex space-x-2">
          <div className="w-2 h-2 rounded-full bg-primary-500 shadow-glow-primary" />
          <div className="w-2 h-2 rounded-full bg-slate-200 dark:bg-surface-700" />
          <div className="w-2 h-2 rounded-full bg-slate-200 dark:bg-surface-700" />
        </div>
      </div>
    </div>
  );
};

export default DocumentTable;
