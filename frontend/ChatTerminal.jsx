// Filename: ChatTerminal.jsx
// Location: frontend/ChatTerminal.jsx

import { useState, useEffect, useRef } from "react";

export default function ChatTerminal() {
  // State to store the chat messages
  const [messages, setMessages] = useState([]);
  // State to manage the current input from the user
  const [input, setInput] = useState("");
  // State for streaming response (future feature)
  const [isStreaming, setIsStreaming] = useState(false);
  // Ref for auto-scrolling to bottom
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Function to handle sending a message
  const handleSend = async () => {
    if (!input.trim() || isStreaming) return; // Ignore empty messages or if streaming

    // Add the user's message to the local state
    const userMessage = { text: input, sender: "user" };
    setMessages([...messages, userMessage]);
    setInput(""); // Clear the input field
    setIsStreaming(true); // Start streaming state

    try {
      // Send the message to the FastAPI backend
      const response = await fetch("http://localhost:8001/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, sessionId: "default" }) // Include session ID
      });

      const data = await response.json(); // Parse the JSON reply from the server

      // Add the bot's reply to the chat with agent info
      const botMessage = {
        text: data.reply,
        sender: "bot",
        agent: data.agent_used,
        confidence: data.confidence
      };
      setMessages(prev => [...prev, botMessage]);
      setIsStreaming(false); // End streaming state
    } catch (err) {
      // Display an error message if the request fails
      setMessages(prev => [...prev, {
        text: "[Error getting response]",
        sender: "bot",
        agent: "system",
        confidence: 0
      }]);
      setIsStreaming(false); // End streaming state on error
    }
  };

  return (
    <div className="h-screen bg-black text-green-500 font-mono flex flex-col">
      {/* Message display area */}
      <div className="flex-1 overflow-y-auto p-4 pb-0">
        <div className="whitespace-pre-wrap">
          {messages.map((msg, idx) => (
            <div key={idx} className="mb-3">
              {msg.sender === "user" ? (
                <div>
                  <span className="text-blue-400">[USER]</span>
                  <span className="ml-2">&gt; {msg.text}</span>
                </div>
              ) : (
                <div>
                  <div className="text-yellow-400 text-sm mb-1">
                    [{msg.agent?.toUpperCase() || 'SYSTEM'}]
                    {msg.confidence && (
                      <span className="ml-2 text-gray-400">
                        (confidence: {(msg.confidence * 100).toFixed(0)}%)
                      </span>
                    )}
                  </div>
                  <div className="ml-2">&lt; {msg.text}</div>
                </div>
              )}
            </div>
          ))}
          {/* Invisible element to scroll to */}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Fixed input area at bottom */}
      <div className="flex-shrink-0 p-4 pt-2 border-t border-green-500">
        <div className="flex">
          <input
            className="flex-grow bg-black border border-green-500 text-green-500 px-2 py-1 outline-none"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSend()}
            placeholder={isStreaming ? "Agent is responding..." : "Type your message..."}
            disabled={isStreaming}
          />
          <button
            className={`ml-2 px-4 py-1 border border-green-500 transition-colors ${
              isStreaming
                ? "text-gray-500 border-gray-500 cursor-not-allowed"
                : "text-green-500 hover:bg-green-500 hover:text-black"
            }`}
            onClick={handleSend}
            disabled={isStreaming}
          >
            {isStreaming ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
