import "./Message.css";

function Message({ role, text }) {
  return (
    <div className={`message ${role}`}>
      <strong>{role}</strong>
      <div className="message-content">
        {text}
      </div>
    </div>
  );
}

export default Message;