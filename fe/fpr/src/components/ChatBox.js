import React from 'react';
import './ChatBox.css';

export function ChatBox(props) {
  const { chat } = props;
  let restoreChat = () => {
    let chatbox = document.getElementById("chat-box");
    chatbox.scrollTop = chatbox.outerHeight;
    return 0;
  }
  return (
    <div class="chat-box" id="chat-box">
      {restoreChat() || chat.join("\n")}
    </div>
  );
}

