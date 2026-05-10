import ChatBot from 'react-chatbotify';
import Sidebar from './components/Sidebar.jsx';

function App() {
  // Cấu hình kịch bản chat và kết nối với Backend RAG
  const flow = {
    start: {
      message: "Hello! I'm your AI assistant. How can I help you today?",
      path: "loop",
    },
    loop: {
      message: async (params) => {
        try {
          // Gọi đến API Backend RAG của bạn
          const response = await fetch("http://localhost:8000/user/chat/invoke", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              message: params.userInput,
              thread_id: "user_session_1" // Bạn có thể tạo ID động sau này
            }),
          });

          if (!response.ok) throw new Error("Backend connection failed");

          const data = await response.json();
          return data.final_plan;
        } catch (error) {
          return "Sorry, I'm having trouble connecting to the travel brain. Please try again later!";
        }
      },
      path: "loop",
    },
  };

  // Tùy chỉnh giao diện để giống bản thiết kế nhất có thể
  const settings = {
    general: {
      embedded: true,
      showFooter: false,
      primaryColor: "#2563eb",
      secondaryColor: "#4f46e5",
      fontFamily: "'Outfit', sans-serif",
      width: "100%",
      height: "100%",
    },
    header: {
      title: (
        <div className="flex items-center gap-2">
          <span className="font-bold tracking-tight">AI Assistant</span>
          <div className="px-1.5 py-0.5 rounded-md bg-white/20 text-[10px] font-bold uppercase tracking-wider">Pro</div>
        </div>
      ),
      showAvatar: true,
      avatar: "https://cdn-icons-png.flaticon.com/512/4712/4712035.png",
      style: {
        background: "linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)",
        padding: "20px",
        height: "70px",
        boxShadow: "0 4px 20px -5px rgba(0,0,0,0.1)"
      }
    },
    chatWindow: {
      showUserAvatar: true,
      welcomeMessage: "Hello! I'm your AI assistant. How can I help you today?",
      backgroundColor: "#ffffff",
      style: {
        width: "100%",
        height: "100%",
        maxWidth: "none",
        maxHeight: "none",
        borderRadius: "0px",
      }
    },
    botBubble: {
      showAvatar: true,
      avatar: "https://cdn-icons-png.flaticon.com/512/4712/4712035.png",
      style: {
        backgroundColor: "#f8fafc",
        color: "#334155",
        borderRadius: "20px 20px 20px 5px",
        boxShadow: "0 2px 5px rgba(0,0,0,0.02)",
        border: "1px solid #f1f5f9",
        fontSize: "14px",
        lineHeight: "1.6"
      }
    },
    userBubble: {
      style: {
        backgroundColor: "#2563eb",
        color: "#ffffff",
        borderRadius: "20px 20px 5px 20px",
        boxShadow: "0 4px 15px -3px rgba(37, 99, 235, 0.2)",
        fontSize: "14px",
        lineHeight: "1.6"
      }
    },
    chatInput: {
      placeholder: "Type your message...",
      style: {
        padding: "15px",
        fontSize: "14px"
      },
      sendButtonStyle: {
        backgroundColor: "#2563eb",
        borderRadius: "10px"
      }
    }
  };

  const styles = {
    chatWindowStyle: {
      width: "100%",
      height: "100%",
      display: "flex",
      flexDirection: "column",
      flexGrow: 1,
    },
    bodyStyle: {
      flexGrow: 1,
      display: "flex",
      flexDirection: "column",
      height: "100%",
    },
    chatInputContainerStyle: {
      flexShrink: 0,
      marginTop: "auto",
    }
  };

  return (
    <div className="flex h-screen w-full bg-[#f8fafc] antialiased overflow-hidden font-['Outfit'] text-slate-900">
      {/* Sidebar của chúng ta đã viết bằng Tailwind */}
      <Sidebar />

      {/* Khu vực Chat sử dụng thư viện chatbotify */}
      <main className="flex-1 flex flex-col h-full bg-white relative">
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'radial-gradient(#2563eb 0.5px, transparent 0.5px)', backgroundSize: '24px 24px' }}></div>
        <div className="flex-1 w-full h-full relative z-10 flex flex-col">
          <ChatBot
            flow={flow}
            settings={settings}
            styles={styles}
            id="ragplan_chatbot"
          />
        </div>
      </main>
    </div>
  );
}


export default App;
