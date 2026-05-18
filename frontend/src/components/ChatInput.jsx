import React, { useState, useRef } from 'react';

export default function ChatInput({ onSendMessage, loading }) {
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() && !file) return;
    onSendMessage(text, file);
    setText('');
    setFile(null);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full flex flex-col gap-3 mt-4">
      <div className="relative flex items-center w-full">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Ask about symptoms, drag reports, check drugs..."
          disabled={loading}
          className="w-full py-4 pl-5 pr-14 rounded-2xl border border-slate-200 shadow-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all text-slate-700 bg-white disabled:bg-slate-50"
        />
        
        {/* Hidden Native File Input */}
        <input
          type="file"
          ref={fileInputRef}
          accept="image/*,.pdf"
          onChange={(e) => setFile(e.target.files[0])}
          className="hidden"
        />

        {/* Custom Attachment Trigger Button */}
        <button
          type="button"
          onClick={() => fileInputRef.current.click()}
          className={`absolute right-4 text-xl transition-colors ${
            file ? 'text-emerald-500' : 'text-slate-400 hover:text-indigo-500'
          }`}
          title="Upload Medical Report"
        >
          📎
        </button>
      </div>

      <div className="flex justify-between items-center min-h-[36px]">
        <div>
          {file && (
            <span className="text-xs font-medium bg-emerald-100 text-emerald-700 py-1.5 px-3 rounded-full shadow-sm">
              📄 {file.name}
            </span>
          )}
        </div>
        <button 
          type="submit" 
          disabled={loading} 
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 px-6 rounded-xl shadow-md transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </>
          ) : (
            'Analyze Now →'
          )}
        </button>
      </div>
    </form>
  );
}