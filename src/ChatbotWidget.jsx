
import { useState } from "react";

export default function ChatbotWidget() {
  const [open, setOpen] = useState(false);
  const [stage, setStage] = useState("inquiry");
  const [slateId, setSlateId] = useState("");
  const [email, setEmail] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      const botMessage = { role: "bot", content: data.response };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: "Server error. Please try again later." },
      ]);
    }
  };

  const lookupApplicant = async () => {
    try {
      const res = await fetch("http://localhost:8000/lookup_applicant", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ slate_id: slateId, email }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: `Applicant Status: ${data.status}` },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: "Error contacting applicant service." },
      ]);
    }
  };

  return (
    <div style={{ position: 'fixed', bottom: '20px', right: '20px', zIndex: 9999 }}>
      {open && (
        <div style={{ width: '350px', height: '500px', background: '#fff', border: '1px solid #ccc', borderRadius: '8px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '10px', borderBottom: '1px solid #ccc' }}>
            <label>Stage:&nbsp;</label>
            <select value={stage} onChange={(e) => setStage(e.target.value)}>
              <option value="inquiry">Inquiry</option>
              <option value="applicant">Applicant</option>
            </select>
          </div>
          <div style={{ flex: 1, padding: '10px', overflowY: 'auto' }}>
            {messages.map((msg, idx) => (
              <div key={idx} style={{
                textAlign: msg.role === 'user' ? 'right' : 'left',
                marginBottom: '8px',
              }}>
                <div style={{
                  display: 'inline-block',
                  background: msg.role === 'user' ? '#cce5ff' : '#eee',
                  padding: '8px',
                  borderRadius: '12px',
                  maxWidth: '80%',
                }}>
                  {msg.content}
                </div>
              </div>
            ))}
          </div>
          <div style={{ padding: '10px', borderTop: '1px solid #ccc' }}>
            {stage === 'applicant' && (
              <div style={{ marginBottom: '10px' }}>
                <input
                  style={{ width: '100%', marginBottom: '6px', padding: '6px' }}
                  value={slateId}
                  onChange={(e) => setSlateId(e.target.value)}
                  placeholder="Slate ID (optional)"
                />
                <input
                  style={{ width: '100%', marginBottom: '6px', padding: '6px' }}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email (optional)"
                />
                <button onClick={lookupApplicant} style={{ width: '100%' }}>Lookup Status</button>
              </div>
            )}
            <div style={{ display: 'flex', gap: '6px' }}>
              <input
                style={{ flex: 1, padding: '6px' }}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Ask a question..."
              />
              <button onClick={sendMessage}>Send</button>
            </div>
          </div>
        </div>
      )}
      <button onClick={() => setOpen(prev => !prev)} style={{ marginTop: '6px' }}>
        {open ? "Close Chat" : "Chat with Us"}
      </button>
    </div>
  );
}
