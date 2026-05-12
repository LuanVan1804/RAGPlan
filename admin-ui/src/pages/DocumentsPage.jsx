import { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import DocumentTable from '../components/DocumentTable';
import UploadCard from '../components/UploadCard';
import { RefreshCw, Search, Plus, X} from 'lucide-react';

const DocumentsPage = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showUpload, setShowUpload] = useState(false);

   const fetchDocuments = useCallback(async () => {
     setLoading(true);
     try {
       const response = await axios.get('http://localhost:8000/admin/knowledge/list');
       setDocuments(Array.isArray(response.data?.documents) ? response.data.documents : []);
     } catch (error) {
       console.error("Failed to fetch documents:", error);
       setDocuments([]); // Đảm bảo documents là mảng rỗng khi có lỗi
     } finally {
       setLoading(false);
     }
   }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

   const filteredDocs = useMemo(() => {
     const lowerSearchTerm = searchTerm.toLowerCase();
     return documents.filter(doc => 
       (doc.name && doc.name.toLowerCase().includes(lowerSearchTerm)) ||
       (doc.destination && doc.destination.toLowerCase().includes(lowerSearchTerm)) ||
       (doc.preview && doc.preview.toLowerCase().includes(lowerSearchTerm))
     );
   }, [documents, searchTerm]);

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            Quản lý <span className="text-primary-500">Tài liệu</span>
          </h2>
          <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">
            Quản lý kho tri thức cốt lõi của hệ thống RAG.
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <button 
            onClick={() => setShowUpload(!showUpload)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-bold transition-all ${
              showUpload 
                ? 'bg-rose-50 text-rose-600 border border-rose-100 hover:bg-rose-100' 
                : 'bg-primary-600 text-white shadow-lg shadow-primary-900/20 hover:shadow-primary-500/40 hover:-translate-y-0.5'
            }`}
          >
            {showUpload ? <X size={18} /> : <Plus size={18} />}
            <span>{showUpload ? 'Hủy' : 'Thêm nhanh'}</span>
          </button>
          
          <button 
            onClick={fetchDocuments}
            className="p-3 bg-white dark:bg-surface-800 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-surface-700 text-slate-600 dark:text-slate-300 transition-all shadow-sm"
            title="Tải lại danh sách"
          >
            <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Upload Section (Expandable) */}
      {showUpload && (
        <div className="animate-in fade-in zoom-in-95 duration-500">
          <UploadCard />
        </div>
      )}

      <div className="flex flex-col md:flex-row gap-4 items-center justify-between p-1">
        <div className="relative w-full md:w-80">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input 
            type="text"
            placeholder="Tìm kiếm tài liệu..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-xl text-sm focus:outline-none focus:ring-4 focus:ring-primary-500/10 focus:border-primary-500/50 transition-all shadow-sm dark:text-white"
          />
        </div>
        
        <div className="flex items-center space-x-6 text-sm font-bold text-slate-400">
          <div className="flex items-center space-x-2">
            <span className="text-slate-900 dark:text-slate-200">{documents.length}</span>
            <span>Documents</span>
          </div>
        </div>
      </div>

      {/* Main Table */}
      <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
        <DocumentTable documents={filteredDocs} loading={loading} />
      </div>
    </div>
  );
};

export default DocumentsPage;
