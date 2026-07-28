import { useState } from "react";
import "./Chat.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function Chat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    const trimmedMessage = message.trim();

    if (!trimmedMessage || isLoading) {
      return;
    }

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmedMessage,
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      userMessage,
    ]);

    setMessage("");
    setError("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: trimmedMessage,
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.reply,
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        assistantMessage,
      ]);
    } catch (requestError) {
      console.error(requestError);

      setError(
        "The AI assistant could not respond. Check that the FastAPI backend is running."
      );
    } finally {
      setIsLoading(false);
    }
  }

  function clearConversation() {
    setMessages([]);
    setError("");
  }

  return (
    <main className="chat-page">
      <section className="chat-container">
        <header className="chat-header">
          <div>
            <p className="chat-label">AI Workspace</p>
            <h1>Software Engineering Assistant</h1>
            <p className="chat-description">
              Ask questions about React, FastAPI, Docker, databases,
              cloud computing and artificial intelligence.
            </p>
          </div>

          <button
            className="clear-button"
            type="button"
            onClick={clearConversation}
            disabled={messages.length === 0 || isLoading}
          >
            Clear chat
          </button>
        </header>

        <div className="messages">
          {messages.length === 0 && (
            <div className="empty-state">
              <h2>How can I help?</h2>
              <p>
                Try asking: “Explain how React communicates with FastAPI.”
              </p>
            </div>
          )}

          {messages.map((chatMessage) => (
            <article
              className={`message ${chatMessage.role}`}
              key={chatMessage.id}
            >
              <p className="message-role">
                {chatMessage.role === "user" ? "You" : "AI Assistant"}
              </p>

              <p className="message-content">
                {chatMessage.content}
              </p>
            </article>
          ))}

          {isLoading && (
            <article className="message assistant">
              <p className="message-role">AI Assistant</p>
              <p className="message-content">Thinking...</p>
            </article>
          )}
        </div>

        {error && <p className="error-message">{error}</p>}

        <form className="chat-form" onSubmit={handleSubmit}>
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Ask a software engineering question..."
            rows="3"
            disabled={isLoading}
          />

          <button
            type="submit"
            disabled={!message.trim() || isLoading}
          >
            {isLoading ? "Sending..." : "Send message"}
          </button>
        </form>
      </section>
    </main>
  );
}

export default Chat;