import React, { useState } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';

function App() {
  const [messages, setMessages] = useState([
    { 
      sender: 'ai', 
      text: "Hello! I am **DocBuddy**, your personal clinical diagnostic companion. Drop your symptoms, list your active medications, or upload medical files below to get started!" 
    }
  ]);
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async (text, file) => {
    let displayTemplate = text;
    if (file) displayTemplate += `\n\n📄 *Attached Document: ${file.name}*`;

    // Immediately update UI with user's message
    setMessages((prev) => [...prev, { sender: 'user', text: displayTemplate }]);
    setLoading(true);

    const formData = new FormData();
    formData.append('message', text);
    if (file) formData.append('file', file);

    try {
      // Connect to the FastAPI backend running on port 8000
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) throw new Error('Network error');
      
      const data = await response.json();
      
      // Update UI with the AI's response
      setMessages((prev) => [...prev, { sender: 'ai', text: data.reply }]);
    } catch (error) {
      setMessages((prev) => [...prev, { 
        sender: 'ai', 
        text: "❌ **Connection Error:** Unable to reach the clinic backend. Ensure FastAPI is running on port 8000." 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center py-8 px-4 sm:px-6">
      <div className="w-full max-w-4xl flex flex-col gap-6">
        
        {/* Header section updated for DocBuddy */}
        <header className="flex flex-col items-center text-center space-y-3 mt-4">
          <div className="w-16 h-16 bg-gradient-to-br from-teal-500 to-emerald-400 rounded-2xl shadow-lg flex items-center justify-center text-white text-3xl font-bold tracking-tighter">
            DB
          </div>
          <div>
            <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">DocBuddy</h1>
            <p className="text-sm font-medium text-teal-600 mt-1 uppercase tracking-widest">Your AI Clinical Assistant</p>
          </div>
        </header>

        {/* Main Chat Interface Container */}
        <div className="bg-white p-3 sm:p-4 rounded-[2rem] shadow-xl border border-slate-200/60 w-full mt-4">
          <ChatWindow messages={messages} loading={loading} />
          <div className="px-2 pb-2">
             <ChatInput onSendMessage={handleSendMessage} loading={loading} />
          </div>
        </div>
        
        {/* Footer Disclaimer */}
        <p className="text-center text-xs text-slate-400 max-w-xl mx-auto mt-4 px-4">
          ⚠️ DocBuddy operates as a clinical diagnostic assistant. Information delivered does not constitute official prescriptive treatment profiles. Always consult a real doctor.
        </p>

      </div>
    </div>
  );
}

export default App;