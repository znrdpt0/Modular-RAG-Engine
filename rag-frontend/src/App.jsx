import { useState, useRef, useEffect } from 'react'

function App() {
  const API_BASE_URL = 'http://35.157.208.84:8000'; //***AWS public 8000 port***
  // --- 1. SOHBET STATE'LERİ ---
  const [messages, setMessages] = useState([
    { role: 'model', text: 'Merhaba! Ben senin RAG asistanınım. Yüklediğin PDF hakkında bana her şeyi sorabilirsin.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // --- 2. DOSYA YÜKLEME STATE'LERİ ---
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(''); // Kullanıcıya bilgi vermek için

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // --- 3. DOSYA YÜKLEME FONKSİYONLARI ---
  const handleFileChange = (e) => {
    setUploadStatus(''); // Yeni dosya seçilince eski mesajı temizle
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadStatus('Belge yükleniyor ve vektörlere dönüştürülüyor...');

    // Dosya gönderimi için özel FormData nesnesi
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Yükleme başarısız oldu.');
      }

      const data = await response.json();
      setUploadStatus(`✅ Başarılı: ${data.filename} (${data.chunks_created} parçaya bölündü)`);
      setSelectedFile(null); // İşlem bitince seçimi sıfırla
      
    } catch (error) {
      console.error("Yükleme Hatası:", error);
      setUploadStatus('❌ Hata: Belge yüklenemedi. Sunucu bağlantısını kontrol edin.');
    } finally {
      setIsUploading(false);
    }
  };

  // --- 4. SOHBET FONKSİYONU ---
  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userText = input;
    setInput('');
    setIsLoading(true);

    setMessages(prev => [
      ...prev, 
      { role: 'user', text: userText },
      { role: 'model', text: '' }
    ]);

    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: userText,
          history: messages.slice(1) 
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let done = false;
      let aiText = '';

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          aiText += decoder.decode(value, { stream: true });
          
          setMessages(prev => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1].text = aiText;
            return newMessages;
          });
        }
      }
    } catch (error) {
      console.error("API Hatası:", error);
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1].text = "Sunucuya bağlanılamadı. Backend açık mı?";
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center p-4 font-sans text-gray-100">
      
      {/* Üst Başlık */}
      <div className="w-full max-w-3xl bg-gray-800 p-4 rounded-t-xl shadow-md border-b border-gray-700 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-blue-400">Modular RAG Engine</h1>
          <p className="text-sm text-gray-400">Belgelerinle akıllı sohbet et</p>
          <p className="text-sm text-bleu-400">Created by znrdpt0</p>
        </div>
      </div>

      {/*PDF Yükleme Paneli */}
      <div className="w-full max-w-3xl bg-gray-800 p-4 border-b border-gray-700 flex flex-col gap-3">
        <div className="flex gap-2 items-center">
          <input 
            type="file" 
            accept=".pdf" 
            onChange={handleFileChange}
            disabled={isUploading}
            className="block w-full text-sm text-gray-400
              file:mr-4 file:py-2 file:px-4
              file:rounded-lg file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-600 file:text-white
              hover:file:bg-blue-700
              cursor-pointer"
          />
          <button 
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
            className="bg-green-600 hover:bg-green-700 transition-colors px-6 py-2 rounded-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
          >
            {isUploading ? 'Yükleniyor...' : 'Yükle'}
          </button>
        </div>
        {/* Durum Mesajı */}
        {uploadStatus && (
          <div className={`text-sm ${uploadStatus.includes('❌') ? 'text-red-400' : 'text-green-400'}`}>
            {uploadStatus}
          </div>
        )}
      </div>

      {/* Sohbet Ekranı */}
      <div className="w-full max-w-3xl flex-1 bg-gray-800 p-4 overflow-y-auto flex flex-col gap-4 shadow-lg border-x border-gray-700 h-[50vh]">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white rounded-br-none' 
                : 'bg-gray-700 text-gray-200 rounded-bl-none'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Yazı Yazma Alanı */}
      <div className="w-full max-w-3xl bg-gray-800 p-4 rounded-b-xl shadow-md border-t border-gray-700">
        <form onSubmit={sendMessage} className="flex gap-2">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            placeholder="Mesajınızı yazın..." 
            className="flex-1 bg-gray-700 text-white p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button 
            type="submit" 
            disabled={isLoading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 transition-colors px-6 py-3 rounded-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? '...' : 'Gönder'}
          </button>
        </form>
      </div>
      
    </div>
  )
}

export default App