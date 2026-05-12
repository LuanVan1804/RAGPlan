import { useState, useRef } from 'react';
import { UploadCloud, File, X, CheckCircle, AlertCircle, Info } from 'lucide-react';
import axios from 'axios';

const UploadCard = () => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState(null); // 'success' | 'error' | null
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    if (selectedFile.type === "text/plain" || selectedFile.name.endsWith('.txt')) {
      setFile(selectedFile);
      setStatus(null);
    } else {
      alert("Hiện tại hệ thống chỉ hỗ trợ định dạng file .txt");
    }
  };

  const onButtonClick = () => {
    inputRef.current.click();
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setStatus(null);

    try {
      const content = await file.text();
      const response = await axios.post('http://localhost:8000/admin/knowledge/ingest', {
        content: content,
        destination: file.name.split('.')[0].toLowerCase(),
        category: 'travel_guide',
        tags: ['uploaded_via_ui']
      });

      if (response.data.status === 'success') {
        setStatus('success');
        setFile(null);
      }
    } catch (error) {
      console.error("Upload failed:", error);
      setStatus('error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card-premium p-6 w-full mx-auto mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-xl font-bold text-slate-900 dark:text-white">Thêm Tài liệu</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">Nạp tài liệu mới vào hệ thống RAG.</p>
        </div>
        <div className="p-1.5 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
          <Info size={16} className="text-primary-500" />
        </div>
      </div>

      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative group border-2 border-dashed rounded-2xl p-8 transition-all duration-500 flex flex-col items-center justify-center overflow-hidden ${
          dragActive 
            ? 'border-primary-500 bg-primary-50/50 dark:bg-primary-900/10' 
            : 'border-slate-200 dark:border-slate-800 hover:border-primary-400/50 hover:bg-slate-50/50 dark:hover:bg-surface-800/50'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".txt"
          onChange={handleChange}
        />

        <div className={`p-4 rounded-xl mb-4 transition-transform duration-500 group-hover:scale-110 ${
          dragActive ? 'bg-primary-500 text-white shadow-glow-primary' : 'bg-slate-100 dark:bg-surface-800 text-slate-400 dark:text-slate-500'
        }`}>
          <UploadCloud size={32} strokeWidth={1.5} />
        </div>

        <div className="text-center">
          <p className="text-base font-semibold text-slate-900 dark:text-white mb-1">
            {file ? (
              <span className="text-primary-600 dark:text-primary-400">Đã chọn: {file.name}</span>
            ) : (
              "Kéo thả file vào đây"
            )}
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mb-6">
            Hệ thống hiện tại chỉ hỗ trợ file .txt.
          </p>
        </div>

        {!file && (
          <button
            onClick={onButtonClick}
            className="px-6 py-2 bg-slate-900 dark:bg-primary-600 text-white rounded-lg text-sm font-bold shadow-xl hover:shadow-primary-500/20 hover:-translate-y-0.5 transition-all active:scale-95"
          >
            Chọn từ máy tính
          </button>
        )}

        {/* Decorative elements */}
        <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-primary-500/5 blur-3xl rounded-full" />
        <div className="absolute bottom-0 left-0 -mb-4 -ml-4 w-24 h-24 bg-indigo-500/5 blur-3xl rounded-full" />
      </div>

      {file && !uploading && !status && (
        <div className="mt-8 animate-in fade-in slide-in-from-bottom-4 duration-300">
          <div className="flex items-center justify-between p-5 bg-slate-50 dark:bg-surface-800/50 rounded-2xl border border-slate-100 dark:border-slate-800">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-white dark:bg-surface-700 rounded-xl shadow-sm">
                <File className="text-primary-500" size={24} />
              </div>
              <div>
                <span className="block text-sm font-bold text-slate-900 dark:text-white">{file.name}</span>
                <span className="text-xs text-slate-500">{(file.size / 1024).toFixed(2)} KB</span>
              </div>
            </div>
            <div className="flex space-x-3">
              <button 
                onClick={() => setFile(null)} 
                className="p-3 text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/10 rounded-xl transition-colors"
              >
                <X size={20} />
              </button>
              <button
                onClick={handleUpload}
                className="px-6 py-3 bg-primary-600 text-white rounded-xl text-sm font-bold hover:bg-primary-700 shadow-lg shadow-primary-900/20 transition-all"
              >
                Xác nhận & Tải lên
              </button>
            </div>
          </div>
        </div>
      )}

      {uploading && (
        <div className="mt-8 flex flex-col items-center justify-center p-12 bg-slate-50 dark:bg-surface-800/50 rounded-2xl border border-slate-100 dark:border-slate-800 animate-pulse">
          <div className="relative w-16 h-16 mb-4">
            <div className="absolute inset-0 border-4 border-primary-200 dark:border-primary-900 rounded-full" />
            <div className="absolute inset-0 border-4 border-primary-600 rounded-full border-t-transparent animate-spin" />
          </div>
          <span className="text-slate-900 dark:text-white font-bold">Đang xử lý tài liệu...</span>
          <p className="text-xs text-slate-500 mt-2">Đang vector hóa và lập chỉ mục cho RAG engine</p>
        </div>
      )}

      {status === 'success' && (
        <div className="mt-8 p-6 bg-emerald-50 dark:bg-emerald-900/10 text-emerald-700 dark:text-emerald-400 rounded-2xl border border-emerald-100 dark:border-emerald-800/50 flex items-center space-x-4 animate-in zoom-in-95 duration-300">
          <div className="p-2 bg-emerald-500 text-white rounded-full">
            <CheckCircle size={24} />
          </div>
          <div>
            <p className="font-bold">Thành công!</p>
            <p className="text-sm opacity-90">Tài liệu đã được nạp thành công vào hệ thống.</p>
          </div>
        </div>
      )}

      {status === 'error' && (
        <div className="mt-8 p-6 bg-rose-50 dark:bg-rose-900/10 text-rose-700 dark:text-rose-400 rounded-2xl border border-rose-100 dark:border-rose-800/50 flex items-center space-x-4 animate-in zoom-in-95 duration-300">
          <div className="p-2 bg-rose-500 text-white rounded-full">
            <AlertCircle size={24} />
          </div>
          <div>
            <p className="font-bold">Tải lên thất bại</p>
            <p className="text-sm opacity-90">Có lỗi xảy ra trong quá trình xử lý. Vui lòng kiểm tra lại backend.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadCard;
