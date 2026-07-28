import "./Message.css";

function Message({ role, text }) {
  const highlightSOP = (text, key) => {
    if (!/SOP_\d+_\S+/.test(text)) return text;
    return text.split(/(\bSOP_\d+_[^\s*,.:]+)/).map((part, i) =>
      /SOP_\d+_\S+/.test(part) ? (
        <span key={`${key}-${i}`} className="sop-citation">{part}</span>
      ) : part
    );
  };

  const renderText = (content) => {
    const lines = content.split("\n");

    return lines.map((line, index) => {
      if (line.trim() === "") return <br key={index} />;

      // Bold (**teks**) — tapi bukan yang dimulai dengan nomor
      if (/\*\*.+\*\*/.test(line) && !/^\d+\./.test(line)) {
        const parts = line.split(/(\*\*[^*]+\*\*)/);
        return (
          <p key={index} className="message-line">
            {parts.map((part, i) =>
              /^\*\*[^*]+\*\*$/.test(part) ? (
                <strong key={i}>{part.replace(/\*\*/g, "")}</strong>
              ) : highlightSOP(part, `${index}-${i}`)
            )}
          </p>
        );
      }

      // Langkah bernomor (1. 2. 3.)
      if (/^\d+\.\s/.test(line)) {
        return (
          <p key={index} className="message-step">
            {highlightSOP(line, index)}
          </p>
        );
      }

      // Bullet point (• atau -)
      if (/^[•\-]\s/.test(line)) {
        return (
          <p key={index} className="message-bullet">
            {highlightSOP(line, index)}
          </p>
        );
      }

      // Teks biasa
      return (
        <p key={index} className="message-line">
          {highlightSOP(line, index)}
        </p>
      );
    });
  };

  const label = role === "user" ? "👤 Anda" : "🤖 Asisten";

  return (
    <div className={`message ${role}`}>
      <span className="message-role">{label}</span>
      <div className="message-content">{renderText(text)}</div>
    </div>
  );
}

export default Message;
