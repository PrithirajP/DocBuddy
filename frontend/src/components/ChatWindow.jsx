import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

export default function ChatWindow({ messages, loading }) {
  const windowEndRef = useRef(null);

  useEffect(() => {
    windowEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="flex-1 overflow-y-auto flex flex-col gap-6 p-4 sm:p-6 bg-slate-50 rounded-2xl border border-slate-200 shadow-inner min-h-[500px] max-h-[600px]">
      {messages.map((msg, index) => {
        const isUser = msg.sender === 'user';
        return (
          <div key={index} className={`flex w-full gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
            
            {!isUser && (
              <div className="w-8 h-8 rounded-full bg-white border border-slate-200 shadow-sm flex items-center justify-center text-sm flex-shrink-0">
                🤖
              </div>
            )}

            <div className={`px-5 py-3.5 max-w-[85%] rounded-2xl shadow-sm text-[15px] leading-relaxed ${
              isUser 
                ? 'bg-indigo-600 text-white rounded-br-sm' 
                : 'bg-white text-slate-800 rounded-bl-sm border border-slate-100'
            }`}>
              {/* Wraps ReactMarkdown in a div to prevent the v9 crash */}
              <div className={`prose max-w-none ${isUser ? 'prose-invert' : 'prose-slate'} prose-p:my-1 prose-ul:my-1 prose-li:my-0.5 prose-a:text-indigo-500`}>
                <ReactMarkdown>
                  {msg.text}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        );
      })}
      
      {loading && (
        <div className="flex w-full gap-3 justify-start">
          <div className="w-8 h-8 rounded-full bg-white border border-slate-200 shadow-sm flex items-center justify-center text-sm flex-shrink-0 animate-pulse">
            ⚡
          </div>
          <div className="px-5 py-3.5 max-w-[80%] rounded-2xl bg-white text-slate-500 rounded-bl-sm border border-slate-100 shadow-sm text-[15px] italic flex items-center gap-2">
            <span className="flex gap-1">
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></span>
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce delay-100"></span>
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce delay-200"></span>
            </span>
            Routing through LangGraph...
          </div>
        </div>
      )}
      <div ref={windowEndRef} />
    </div>
  );
}