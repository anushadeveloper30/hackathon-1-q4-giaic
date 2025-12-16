import React, { useState, useRef, useEffect } from 'react';
import styles from './ChatAgent.module.css'; // Make sure this path is correct

interface Message {
  sender: 'user' | 'ai';
  text: string;
}

const ChatAgent: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const BOT_NAME = "Anusha's Book Agent";
  const USER_NAME = "You";
  const FASTAPI_BACKEND_URL = "http://localhost:8000/chat"; // FastAPI backend URL

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleSendMessage = async () => {
    if (input.trim() === '') return;

    const userMessage: Message = { sender: USER_NAME, text: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(FASTAPI_BACKEND_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage.text }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage = errorData.detail || `HTTP error! status: ${response.status}`;
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setMessages((prevMessages) => [...prevMessages, { sender: BOT_NAME, text: data.reply }]);
    } catch (error: any) {
      console.error('Error sending message to FastAPI backend:', error);
      // Log the actual error to the browser console as required
      console.error('Detailed Error:', error.message || error);
      setMessages((prevMessages) => [...prevMessages, { sender: BOT_NAME, text: `Oops! Something went wrong: ${error.message || 'Unknown error'}. Please check console for details.` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isLoading) {
      handleSendMessage();
    }
  };

  return (
    <div className={styles.aiAgentContainer}>
      <button className={styles.floatingButton} onClick={toggleChat}>
        {isOpen ? '✖' : '💬'}
      </button>

      {isOpen && (
        <div className={styles.chatWindow}>
          <div className={styles.chatHeader}>
            <h3>{BOT_NAME}</h3>
          </div>
          <div className={styles.messagesContainer}>
            {messages.length === 0 && (
                <div className={styles.welcomeMessage}>
                    Hi there! I'm Anusha's Book Agent. Ask me anything about the book content!
                </div>
            )}
            {messages.map((msg, index) => (
              <div
                key={index}
                className={msg.sender === USER_NAME ? styles.userMessage : styles.aiMessage}
              >
                <strong>{msg.sender}:</strong> {msg.text}
              </div>
            ))}
            {isLoading && (
              <div className={styles.aiMessage}>
                <strong>{BOT_NAME}:</strong> Thinking...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <div className={styles.inputContainer}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about the book..."
              disabled={isLoading}
            />
            <button onClick={handleSendMessage} disabled={isLoading}>
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatAgent;
