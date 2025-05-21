
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";

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
    <div className="fixed bottom-4 right-4 z-50">
      {open && (
        <Card className="w-80 h-[500px] flex flex-col">
          <CardContent className="flex-1 overflow-y-auto space-y-2 p-2">
            <div className="mb-2">
              <label>Stage: </label>
              <select value={stage} onChange={(e) => setStage(e.target.value)}>
                <option value="inquiry">Inquiry</option>
                <option value="applicant">Applicant</option>
              </select>
            </div>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`p-2 rounded-xl max-w-xs ${
                  msg.role === "user" ? "bg-blue-100 self-end" : "bg-gray-100 self-start"
                }`}
              >
                {msg.content}
              </div>
            ))}
          </CardContent>
          <div className="p-2 flex flex-col gap-2 border-t">
            {stage === "applicant" && (
              <>
                <Input
                  value={slateId}
                  onChange={(e) => setSlateId(e.target.value)}
                  placeholder="Slate ID (optional)"
                />
                <Input
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email (optional)"
                />
                <Button onClick={lookupApplicant}>Lookup Status</Button>
              </>
            )}
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Ask a question..."
              />
              <Button onClick={sendMessage}>Send</Button>
            </div>
          </div>
        </Card>
      )}
      <Button onClick={() => setOpen((prev) => !prev)}>
        {open ? "Close Chat" : "Chat with Us"}
      </Button>
    </div>
  );
}
