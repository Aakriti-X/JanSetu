import React, { useState, useRef, useEffect } from 'react';
import './index.css';

// --- HACKATHON DEMO AUTH & API ---
const DEMO_USER = { id: "jan_setu_demo", pin: "1234", name: "Citizen" };
const API_URL = "http://localhost:8000";

// --- UI TRANSLATION DICTIONARY ---
const uiText = {
  en: {
    appTitle: "JanSetu AI",
    ragStatus: "Local RAG Active",
    greeting: "Namaste.",
    helpText: "How can I help?",
    subText: "Speak securely in your local language. No internet required.",
    connectWa: "Connect via WhatsApp",
    privacyTitle: "100% Private & Offline",
    privacyDesc: "Your documents and voice data never leave this device.",
    cards: [
      { id: 'schemes', title: 'Discover Schemes', desc: 'Find benefits mapped to your profile' },
      { id: 'eligibility', title: 'Check Eligibility', desc: 'Verify criteria via local RAG' },
      { id: 'grievance', title: 'Lodge Grievance', desc: 'Report issues directly to authorities' },
      { id: 'scan', title: 'Scan Document', desc: 'Extract text from notices & forms' }
    ],
    modal: {
      listening: "Listening...",
      micReady: "Microphone Ready",
      voicePrompt: "Tell me what government assistance you need.",
      sendAi: "Send to AI",
      scanTitle: "Scan a Document",
      cameraView: "Camera viewfinder will open here",
      openCamera: "Open Camera",
      retake: "Retake Photo",
      evalLang: "Select Evaluation Language",
      extractBtn: "Extract & Evaluate",
      analyzing: "Analyzing Offline...",
      chatSub: "Local RAG Connected",
      typeMsg: "Type a message...",
      listen: "Listen",
      typing: "AI is thinking..."
    },
    botReplies: {
      welcome: "Namaste! I am JanSetu AI. You can upload a document or ask me a question.",
    }
  },
  hi: {
    appTitle: "जनसेतु AI",
    ragStatus: "लोकल RAG सक्रिय",
    greeting: "नमस्ते।",
    helpText: "मैं आपकी कैसे मदद कर सकता हूँ?",
    subText: "अपनी स्थानीय भाषा में सुरक्षित रूप से बोलें। इंटरनेट की आवश्यकता नहीं है।",
    connectWa: "WhatsApp से जुड़ें",
    privacyTitle: "100% निजी और ऑफ़लाइन",
    privacyDesc: "आपके दस्तावेज़ और वॉइस डेटा कभी भी इस डिवाइस से बाहर नहीं जाते हैं।",
    cards: [
      { id: 'schemes', title: 'सरकारी योजनाएँ', desc: 'अपनी प्रोफ़ाइल के अनुसार लाभ खोजें' },
      { id: 'eligibility', title: 'पात्रता जाँचें', desc: 'स्थानीय RAG द्वारा मानदंड सत्यापित करें' },
      { id: 'grievance', title: 'शिकायत दर्ज करें', desc: 'सीधे अधिकारियों को समस्याओं की रिपोर्ट करें' },
      { id: 'scan', title: 'दस्तावेज़ स्कैन करें', desc: 'नोटिस और फॉर्म से टेक्स्ट निकालें' }
    ],
    modal: {
      listening: "सुन रहा हूँ...",
      micReady: "माइक्रोफ़ोन तैयार है",
      voicePrompt: "मुझे बताएं कि आपको किस सरकारी सहायता की आवश्यकता है।",
      sendAi: "AI को भेजें",
      scanTitle: "दस्तावेज़ स्कैन करें",
      cameraView: "कैमरा व्यूफाइंडर यहां खुलेगा",
      openCamera: "कैमरा खोलें",
      retake: "फिर से फोटो लें",
      evalLang: "मूल्यांकन भाषा चुनें",
      extractBtn: "निकालें और मूल्यांकन करें",
      analyzing: "ऑफ़लाइन विश्लेषण कर रहा है...",
      chatSub: "लोकल RAG कनेक्टेड",
      typeMsg: "संदेश लिखें...",
      listen: "सुनें",
      typing: "AI सोच रहा है..."
    },
    botReplies: {
      welcome: "नमस्ते! मैं जनसेतु AI हूँ। आप अपना दस्तावेज़ अपलोड कर सकते हैं या मुझसे बोलकर सवाल पूछ सकते हैं।",
    }
  },
  mr: {
    appTitle: "जनसेतू AI",
    ragStatus: "लोकल RAG सक्रिय",
    greeting: "नमस्कार.",
    helpText: "मी तुमची कशी मदत करू शकतो?",
    subText: "तुमच्या स्थानिक भाषेत सुरक्षितपणे बोला. इंटरनेटची आवश्यकता नाही.",
    connectWa: "WhatsApp वर कनेक्ट करा",
    privacyTitle: "100% खाजगी आणि ऑफलाइन",
    privacyDesc: "तुमचे दस्तऐवज आणि व्हॉइस डेटा कधीही हे डिव्हाइस सोडत नाहीत.",
    cards: [
      { id: 'schemes', title: 'सरकारी योजना', desc: 'तुमच्या प्रोफाइलनुसार लाभ शोधा' },
      { id: 'eligibility', title: 'पात्रता तपासा', desc: 'स्थानिक RAG द्वारे निकष सत्यापित करा' },
      { id: 'grievance', title: 'तक्रार नोंदवा', desc: 'थेट अधिकाऱ्यांना समस्यांची तक्रार करा' },
      { id: 'scan', title: 'दस्तऐवज स्कॅन करा', desc: 'नोटिसा आणि फॉर्ममधून मजकूर काढा' }
    ],
    modal: {
      listening: "ऐकत आहे...",
      micReady: "मायक्रोफोन तयार आहे",
      voicePrompt: "तुम्हाला कोणत्या सरकारी मदतीची आवश्यकता आहे ते मला सांगा.",
      sendAi: "AI ला पाठवा",
      scanTitle: "दस्तऐवज स्कॅन करा",
      cameraView: "कॅमेरा व्ह्यूफाइंडर येथे उघडेल",
      openCamera: "कॅमेरा उघडा",
      retake: "पुन्हा फोटो घ्या",
      evalLang: "मूल्यांकन भाषा निवडा",
      extractBtn: "काढा आणि मूल्यांकन करा",
      analyzing: "ऑफलाइन विश्लेषण करत आहे...",
      chatSub: "लोकल RAG कनेक्टेड",
      typeMsg: "संदेश लिहा...",
      listen: "ऐका",
      typing: "AI विचार करत आहे..."
    },
    botReplies: {
      welcome: "नमस्कार! मी जनसेतू AI आहे. तुम्ही दस्तऐवज अपलोड करू शकता किंवा मला प्रश्न विचारू शकता.",
    }
  },
  gu: {
    appTitle: "જનસેતુ AI",
    ragStatus: "લોકલ RAG સક્રિય",
    greeting: "નમસ્તે.",
    helpText: "હું તમારી કેવી રીતે મદદ કરી શકું?",
    subText: "તમારી સ્થાનિક ભાષામાં સુરક્ષિત રીતે બોલો. ઇન્ટરનેટની જરૂર નથી.",
    connectWa: "WhatsApp પર કનેક્ટ કરો",
    privacyTitle: "100% ખાનગી અને ઑફલાઇન",
    privacyDesc: "તમારા દસ્તાવેજો અને વૉઇસ ડેટા ક્યારેય આ ઉપકરણ છોડતા નથી.",
    cards: [
      { id: 'schemes', title: 'સરકારી યોજનાઓ', desc: 'લાભો શોધો' },
      { id: 'eligibility', title: 'પાત્રતા ચકાસો', desc: 'RAG દ્વારા ચકાસો' },
      { id: 'grievance', title: 'ફરિયાદ નોંધાવો', desc: 'અધિકારીઓને જાણ કરો' },
      { id: 'scan', title: 'દસ્તાવેજ સ્કેન કરો', desc: 'ટેક્સ્ટ કાઢો' }
    ],
    modal: {
      listening: "સાંભળી રહ્યો છું...",
      micReady: "માઇક્રોફોન તૈયાર છે",
      voicePrompt: "તમારે કઈ સહાયની જરૂર છે તે કહો.",
      sendAi: "AI ને મોકલો",
      scanTitle: "દસ્તાવેજ સ્કેન કરો",
      cameraView: "કેમેરા અહીં ખુલશે",
      openCamera: "કેમેરા ખોલો",
      retake: "ફરીથી ફોટો લો",
      evalLang: "ભાષા પસંદ કરો",
      extractBtn: "સ્કેન કરો અને મૂલ્યાંકન કરો",
      analyzing: "વિશ્લેષણ કરી રહ્યું છે...",
      chatSub: "લોકલ RAG જોડાયેલ છે",
      typeMsg: "સંદેશ લખો...",
      listen: "સાંભળો",
      typing: "AI વિચારી રહ્યું છે..."
    },
    botReplies: {
      welcome: "નમસ્તે! હું જનસેતુ AI છું. તમે દસ્તાવેજ અપલોડ કરી શકો છો અથવા પ્રશ્ન પૂછી શકો છો.",
    }
  },
  bn: {
    appTitle: "জনসেতু AI",
    ragStatus: "লোকাল RAG সক্রিয়",
    greeting: "নমস্কার।",
    helpText: "আমি কীভাবে সাহায্য করতে পারি?",
    subText: "আপনার মাতৃভাষায় নিরাপদে কথা বলুন। ইন্টারনেটের প্রয়োজন নেই।",
    connectWa: "WhatsApp এ যুক্ত হন",
    privacyTitle: "100% ব্যক্তিগত এবং অফলাইন",
    privacyDesc: "আপনার নথি এবং ভয়েস ডেটা এই ডিভাইস ছেড়ে যায় না।",
    cards: [
      { id: 'schemes', title: 'সরকারি প্রকল্প', desc: 'সুবিধা খুঁজুন' },
      { id: 'eligibility', title: 'যোগ্যতা যাচাই করুন', desc: 'RAG এর মাধ্যমে যাচাই করুন' },
      { id: 'grievance', title: 'অভিযোগ দায়ের করুন', desc: 'কর্তৃপক্ষকে জানান' },
      { id: 'scan', title: 'নথি স্ক্যান করুন', desc: 'পাঠ্য বের করুন' }
    ],
    modal: {
      listening: "শুনছি...",
      micReady: "মাইক্রোফোন প্রস্তুত",
      voicePrompt: "আপনার কী সরকারি সহায়তা প্রয়োজন তা বলুন।",
      sendAi: "AI কে পাঠান",
      scanTitle: "একটি নথি স্ক্যান করুন",
      cameraView: "ক্যামেরা এখানে খুলবে",
      openCamera: "ক্যামেরা খুলুন",
      retake: "আবার ছবি তুলুন",
      evalLang: "ভাষা নির্বাচন করুন",
      extractBtn: "স্ক্যান এবং মূল্যায়ন করুন",
      analyzing: "বিশ্লেষণ করা হচ্ছে...",
      chatSub: "লোকাল RAG সংযুক্ত",
      typeMsg: "একটি বার্তা টাইপ করুন...",
      listen: "শুনুন",
      typing: "AI ভাবছে..."
    },
    botReplies: {
      welcome: "নমস্কার! আমি জনসেতু AI। আপনি নথি আপলোড করতে পারেন বা প্রশ্ন করতে পারেন।",
    }
  }
};

const icons = {
  schemes: <svg className="w-8 h-8" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>,
  eligibility: <svg className="w-8 h-8" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
  grievance: <svg className="w-8 h-8" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" /></svg>,
  scan: <svg className="w-8 h-8" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
};

export default function App() {
  const [appLang, setAppLang] = useState('en');
  const [activeModal, setActiveModal] = useState(null);
  const [inputValue, setInputValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isProcessingDoc, setIsProcessingDoc] = useState(false);
  const [isBotTyping, setIsBotTyping] = useState(false);

  const t = uiText[appLang];
  const [messages, setMessages] = useState([]);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  // Auto-Register Demo User on Mount
  useEffect(() => {
    fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: DEMO_USER.id,
        display_name: DEMO_USER.name,
        pin: DEMO_USER.pin
      })
    }).catch(err => console.log("Silent error (User likely exists):", err));
  }, []);

  // Update welcome message on language change
  useEffect(() => {
    setMessages([{ id: 1, role: 'bot', text: t.botReplies.welcome }]);
  }, [appLang, t.botReplies.welcome]);

  // Auto-scroll chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isBotTyping]);

  const handleWhatsAppConnect = () => {
    const phoneNumber = "910000000000";
    const message = encodeURIComponent("Namaste! I need help.");
    window.open(`https://wa.me/${phoneNumber}?text=${message}`, '_blank');
  };

  const getLangCode = (lang) => {
    const codes = { en: 'en-US', hi: 'hi-IN', mr: 'mr-IN', gu: 'gu-IN', bn: 'bn-IN' };
    return codes[lang] || 'en-US';
  }

  // --- NATIVE VOICE CAPTURE ---
  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return alert("Browser does not support Voice Recognition.");

    const recognition = new SpeechRecognition();
    recognition.lang = getLangCode(appLang);
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event) => {
      setInputValue(event.results[0][0].transcript);
      setIsListening(false);
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);
    recognition.start();
  };

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = getLangCode(appLang);
      window.speechSynthesis.speak(utterance);
    }
  };

  // --- API CONNECTION: SEND TEXT TO RAG ---
  const handleSendChat = async (textOverrides = null) => {
    const textToSend = textOverrides || inputValue;
    if (!textToSend.trim()) return;

    setMessages(prev => [...prev, { id: Date.now(), role: 'user', text: textToSend }]);
    setInputValue('');
    setIsBotTyping(true);

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': DEMO_USER.id,
          'X-User-PIN': DEMO_USER.pin
        },
        body: JSON.stringify({ question: textToSend })
      });

      if (!response.ok) throw new Error("API Error");
      const data = await response.json();
      setMessages(prev => [...prev, { id: Date.now() + 1, role: 'bot', text: data.answer }]);
    } catch (error) {
      console.error("Query failed:", error);
      setMessages(prev => [...prev, { id: Date.now() + 1, role: 'bot', text: "सॉरी, सर्वर से संपर्क नहीं हो पा रहा है। (Connection failed. Please make sure the Python server is running on port 8000)" }]);
    } finally {
      setIsBotTyping(false);
    }
  };

  // --- API CONNECTION: SEND DOCUMENT TO INGESTION ---
  const processDocument = async (fileToProcess = null) => {
    setIsProcessingDoc(true);
    const file = fileToProcess || cameraInputRef.current?.files[0] || fileInputRef.current?.files[0];

    if (!file) {
      setIsProcessingDoc(false);
      return;
    }

    setActiveModal('schemes');
    setMessages(prev => [...prev, { id: Date.now(), role: 'user', text: `📎 [Document Uploaded: ${file.name}]` }]);
    setIsBotTyping(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/ingest`, {
        method: 'POST',
        headers: {
          'X-User-ID': DEMO_USER.id,
          'X-User-PIN': DEMO_USER.pin
        },
        body: formData
      });

      if (!response.ok) throw new Error("Upload Error");
      const data = await response.json();

      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'bot',
        text: `Document processed successfully (${data.chunks} chunks created). You can now ask questions about this document!`
      }]);
    } catch (error) {
      console.error("Upload failed:", error);
      setMessages(prev => [...prev, { id: Date.now() + 1, role: 'bot', text: "Error scanning document. Ensure Python server is running." }]);
    } finally {
      setIsProcessingDoc(false);
      setIsBotTyping(false);
      setCapturedImage(null);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) processDocument(file);
  };

  const handleCameraCapture = (event) => {
    const file = event.target.files[0];
    if (file) setCapturedImage(URL.createObjectURL(file));
  };

  return (
    <div className="min-h-screen bg-[#F0F7F2] text-[#2C4037] font-sans relative overflow-x-hidden flex flex-col">

      {/* Ambient Celadon Orbs */}
      <div className="absolute top-[-15%] left-[-10%] w-[50%] h-[50%] bg-[#ACE1AF]/30 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-[#B5E5BA]/40 rounded-full blur-[100px] pointer-events-none"></div>

      <header className="relative z-10 w-full max-w-6xl mx-auto p-4 sm:p-6 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-[#549074] to-[#415C52] rounded-xl flex items-center justify-center shadow-lg">
            <span className="text-white font-extrabold text-2xl leading-none">J</span>
          </div>
          <span className="font-extrabold text-2xl tracking-tighter text-[#2C4037]">{t.appTitle}</span>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={appLang}
            onChange={(e) => setAppLang(e.target.value)}
            className="bg-white border-2 border-[#D5F2CE] text-[#415C52] font-bold text-sm rounded-full px-4 py-2 outline-none focus:ring-2 focus:ring-[#549074] shadow-sm cursor-pointer"
          >
            <option value="en">English</option>
            <option value="hi">हिंदी</option>
            <option value="mr">मराठी</option>
            <option value="gu">ગુજરાતી</option>
            <option value="bn">বাংলা</option>
          </select>

          <div className="hidden sm:flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm border border-[#D5F2CE]">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#ACE1AF] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-[#549074]"></span>
            </span>
            <span className="text-xs font-bold text-[#415C52] tracking-wide uppercase">{t.ragStatus}</span>
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-5xl w-full mx-auto px-6 pt-6 pb-24 flex-grow flex flex-col items-center">
        <div className="flex flex-col items-center mb-12 text-center mt-4">
          <h1 className="text-5xl sm:text-7xl font-sans font-medium tracking-tighter text-[#2C4037] mb-4">
            {t.greeting} <br className="sm:hidden" /><span className="font-bold text-[#415C52]">{t.helpText}</span>
          </h1>
          <p className="text-[#549074] font-semibold text-lg mb-10 max-w-lg">
            {t.subText}
          </p>

          <button
            onClick={() => { setActiveModal('voice'); startListening(); }}
            className="group relative flex items-center justify-center w-32 h-32 bg-[#415C52] rounded-full shadow-[0_10px_40px_rgba(65,92,82,0.4)] hover:shadow-[0_10px_60px_rgba(65,92,82,0.6)] hover:scale-105 transition-all duration-300"
          >
            <div className="absolute inset-0 rounded-full border-4 border-[#ACE1AF]/30 animate-pulse"></div>
            <svg className="w-14 h-14 text-[#D5F2CE]" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </button>

          <button
            onClick={handleWhatsAppConnect}
            className="mt-10 flex items-center gap-3 bg-[#25D366] text-white px-8 py-4 rounded-full font-bold shadow-lg hover:scale-105 hover:bg-[#20bd5a] transition-all text-lg"
          >
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12.031 0C5.385 0 0 5.385 0 12.031c0 2.65.834 5.105 2.26 7.152L.645 24l5.006-1.583C7.575 23.708 9.722 24 12.031 24 18.677 24 24 18.615 24 11.97 24 5.385 18.677 0 12.031 0zm.013 20.032c-2.146 0-4.22-.559-6.071-1.616l-.435-.257-3.327 1.052.894-3.21-.282-.449a12.03 12.03 0 01-1.848-6.425C.975 4.542 5.51 0 11.044 0 16.578 0 21.113 4.542 21.113 10.076c0 5.534-4.535 10.076-10.068 10.076zM16.55 13.5c-.275-.137-1.62-.797-1.872-.888-.252-.09-.436-.137-.62.137-.184.274-.707.888-.867 1.071-.16.183-.321.206-.596.069-.275-.138-1.156-.426-2.203-1.356-.815-.724-1.365-1.62-1.525-1.895-.16-.275-.017-.424.12-.56.124-.124.275-.321.413-.48.137-.161.183-.275.275-.458.092-.183.046-.344-.023-.48-.069-.138-.62-1.493-.849-2.046-.223-.538-.45-.465-.62-.474-.16-.008-.344-.008-.528-.008-.184 0-.482.069-.734.344-.252.275-.964.939-.964 2.29s.987 2.656 1.124 2.839c.138.183 1.936 2.955 4.69 4.108 2.753 1.153 2.753.768 3.258.723.504-.046 1.62-.662 1.849-1.303.23-.64.23-1.189.16-1.303-.068-.114-.252-.183-.527-.321z" /></svg>
            {t.connectWa}
          </button>
        </div>

        <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-5 mt-4">
          {t.cards.map((card) => (
            <button
              key={card.id}
              onClick={() => setActiveModal(card.id)}
              className="group relative bg-white shadow-[0_8px_30px_rgb(65,92,82,0.06)] border border-[#D5F2CE] rounded-[2rem] p-6 flex items-center gap-5 text-left transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_12px_40px_rgb(65,92,82,0.15)] hover:border-[#ACE1AF]"
            >
              <div className="w-16 h-16 rounded-full flex items-center justify-center flex-shrink-0 transition-transform group-hover:scale-110 bg-[#E8F5E9] text-[#415C52] border border-[#D5F2CE]">
                {icons[card.id]}
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-extrabold text-[#2C4037] leading-snug tracking-tight">{card.title}</span>
                <span className="text-sm font-bold text-[#549074] mt-1">{card.desc}</span>
              </div>
            </button>
          ))}
        </div>
      </main>

      <footer className="relative z-10 w-full p-6 mt-auto">
        <div className="max-w-2xl mx-auto bg-[#415C52] rounded-3xl p-5 flex items-center gap-5 shadow-2xl">
          <div className="w-12 h-12 bg-[#D5F2CE] rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-2xl">🛡️</span>
          </div>
          <div className="text-sm">
            <p className="font-bold text-white text-base tracking-wide">{t.privacyTitle}</p>
            <p className="text-[#D5F2CE] mt-1 font-medium">{t.privacyDesc}</p>
          </div>
        </div>
      </footer>

      {/* BOTTOM SHEET MODAL */}
      {activeModal && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-[#2C4037]/60 backdrop-blur-md transition-all duration-300">
          <div className="absolute inset-0" onClick={() => { setActiveModal(null); setIsListening(false); }}></div>

          <div className="relative bg-[#FAFCFB] w-full max-w-3xl rounded-t-[3rem] p-8 min-h-[80vh] shadow-2xl flex flex-col animate-[slideUp_0.3s_ease-out] border-t border-[#ACE1AF]">

            <button
              onClick={() => { setActiveModal(null); setIsListening(false); setCapturedImage(null); }}
              className="absolute top-8 right-8 p-3 bg-[#E8F5E9] hover:bg-[#D5F2CE] rounded-full text-[#415C52] transition-colors z-10"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="3" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>

            {/* Voice Mode */}
            {activeModal === 'voice' && (
              <div className="text-center mt-24">
                <div className="w-40 h-40 bg-[#415C52] text-[#D5F2CE] rounded-full flex items-center justify-center mx-auto mb-8 relative shadow-2xl">
                  {isListening && <div className="absolute inset-0 bg-[#ACE1AF] rounded-full animate-ping opacity-40"></div>}
                  <svg className="w-20 h-20 relative z-10" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
                </div>
                <h2 className="text-3xl font-extrabold text-[#2C4037] mb-3 tracking-tight">{isListening ? t.modal.listening : t.modal.micReady}</h2>
                <p className="text-[#549074] text-lg font-bold">{inputValue ? `"${inputValue}"` : t.modal.voicePrompt}</p>
                {!isListening && (
                  <button onClick={() => handleSendChat(inputValue)} className="mt-10 bg-[#415C52] text-white px-8 py-3 rounded-full font-bold text-lg hover:bg-[#2C4037] transition-colors">
                    {t.modal.sendAi}
                  </button>
                )}
              </div>
            )}

            {/* Scan Mode */}
            {activeModal === 'scan' && (
              <div className="text-center w-full mt-4">
                <h2 className="text-3xl font-extrabold text-[#2C4037] mb-6 tracking-tight">{t.modal.scanTitle}</h2>

                <div className="w-full h-64 bg-[#E8F5E9] border-4 border-dashed border-[#ACE1AF] rounded-[2rem] flex flex-col items-center justify-center mb-8 overflow-hidden relative">
                  {capturedImage ? (
                    <img src={capturedImage} alt="Captured" className="w-full h-full object-cover" />
                  ) : (
                    <>
                      <svg className="w-14 h-14 text-[#549074] mb-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /></svg>
                      <p className="text-[#415C52] font-bold text-lg">{t.modal.cameraView}</p>
                    </>
                  )}
                </div>

                {/* Hidden Inputs */}
                <input type="file" accept="image/*" capture="environment" ref={cameraInputRef} onChange={handleCameraCapture} className="hidden" />

                {!capturedImage ? (
                  <button
                    onClick={() => cameraInputRef.current.click()}
                    className="bg-[#415C52] text-white px-10 py-4 rounded-full font-extrabold text-lg shadow-xl hover:bg-[#2C4037] transition-transform hover:scale-105"
                  >
                    {t.modal.openCamera}
                  </button>
                ) : (
                  <div className="flex flex-col gap-5 w-full max-w-sm mx-auto">
                    <button
                      onClick={() => processDocument()}
                      disabled={isProcessingDoc}
                      className="bg-[#415C52] text-white px-8 py-4 rounded-full font-extrabold text-lg shadow-xl hover:bg-[#2C4037] transition-all flex items-center justify-center gap-3"
                    >
                      {isProcessingDoc ? (
                        <>
                          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-[#ACE1AF]" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          {t.modal.analyzing}
                        </>
                      ) : (
                        t.modal.extractBtn
                      )}
                    </button>

                    <button
                      onClick={() => cameraInputRef.current.click()}
                      className="text-[#549074] font-bold hover:text-[#2C4037]"
                    >
                      {t.modal.retake}
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Chat UI */}
            {(activeModal === 'schemes' || activeModal === 'eligibility' || activeModal === 'grievance') && (
              <div className="flex flex-col h-full w-full flex-grow">
                <div className="border-b-2 border-[#D5F2CE] pb-5 mb-5 flex items-center justify-between">
                  <div>
                    <h2 className="text-3xl font-extrabold text-[#2C4037] tracking-tight">
                      {t.cards.find(c => c.id === activeModal)?.title}
                    </h2>
                    <p className="text-sm text-green-700 font-bold flex items-center gap-2 mt-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></span>
                      {t.modal.chatSub}
                    </p>
                  </div>
                </div>

                <div className="flex-grow overflow-y-auto space-y-5 pr-2 mb-6 min-h-[300px] max-h-[450px]">
                  {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[85%] p-5 rounded-[2rem] ${msg.role === 'user' ? 'bg-[#415C52] text-white rounded-tr-sm shadow-lg' : 'bg-white border border-[#D5F2CE] text-[#2C4037] rounded-tl-sm shadow-md'
                        }`}>
                        <p className="text-lg font-semibold leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                        {msg.role === 'bot' && (
                          <button onClick={() => speakText(msg.text)} className="mt-4 text-[#415C52] hover:bg-[#E8F5E9] flex items-center gap-2 text-sm font-extrabold bg-[#D5F2CE] px-5 py-2 rounded-full transition-transform hover:scale-105">
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M13.5 4.06c0-1.336-1.616-2.005-2.56-1.06l-4.5 4.5H4.508c-1.141 0-2.318.664-2.66 1.905A9.76 9.76 0 001.5 12c0 .898.121 1.768.35 2.595.341 1.24 1.518 1.905 2.659 1.905h1.93l4.5 4.5c.945.945 2.561.276 2.561-1.06V4.06zM18.584 5.106a.75.75 0 011.06 0c3.808 3.807 3.808 9.98 0 13.788a.75.75 0 11-1.06-1.06 8.25 8.25 0 000-11.668.75.75 0 010-1.06z" /><path d="M15.932 7.757a.75.75 0 011.061 0 6 6 0 010 8.486.75.75 0 01-1.06-1.061 4.5 4.5 0 000-6.364.75.75 0 010-1.06z" /></svg>
                            {t.modal.listen}
                          </button>
                        )}
                      </div>
                    </div>
                  ))}

                  {/* Typing Indicator */}
                  {isBotTyping && (
                    <div className="flex justify-start">
                      <div className="bg-white border border-[#D5F2CE] text-[#549074] rounded-[2rem] rounded-tl-sm p-4 shadow-sm flex items-center gap-2 font-bold">
                        <span className="w-2 h-2 bg-[#549074] rounded-full animate-bounce"></span>
                        <span className="w-2 h-2 bg-[#549074] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></span>
                        <span className="w-2 h-2 bg-[#549074] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                        <span className="ml-2 text-sm">{t.modal.typing}</span>
                      </div>
                    </div>
                  )}
                  {/* Auto-scroll anchor */}
                  <div ref={messagesEndRef} />
                </div>

                <div className="mt-auto bg-white border-2 border-[#D5F2CE] rounded-full p-2 flex items-center shadow-xl focus-within:border-[#415C52] transition-all">
                  <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept=".pdf,image/*" />
                  <button onClick={() => fileInputRef.current.click()} className="p-3 text-[#549074] hover:text-[#2C4037] transition-colors rounded-full hover:bg-[#E8F5E9]">
                    <svg className="w-7 h-7" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" /></svg>
                  </button>
                  <input
                    type="text"
                    placeholder={t.modal.typeMsg}
                    className="flex-grow px-4 py-3 outline-none text-[#2C4037] bg-transparent text-lg font-bold placeholder-[#549074]/60"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleSendChat();
                    }}
                  />
                  <button onClick={startListening} className={`p-3 transition-colors rounded-full mr-2 ${isListening ? 'text-[#415C52] bg-[#ACE1AF] animate-pulse' : 'text-[#549074] hover:text-[#2C4037] hover:bg-[#E8F5E9]'}`}>
                    <svg className="w-7 h-7" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
                  </button>
                  <button
                    className="bg-[#415C52] hover:bg-[#2C4037] text-white p-4 rounded-full shadow-lg transition-transform hover:scale-105"
                    onClick={() => handleSendChat()}
                  >
                    <svg className="w-7 h-7" fill="none" stroke="currentColor" strokeWidth="3" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}