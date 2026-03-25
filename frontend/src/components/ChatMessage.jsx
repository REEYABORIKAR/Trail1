/**
 * ChatMessage — renders a single message bubble.
 * Handles: User bubble, AI bubble, source badges with tooltips,
 * fallback HR escalation banner, and typing shimmer.
 */

export function TypingMessage() {
  return (
    <div className="message-row">
      <div className="msg-avatar ai">🤖</div>
      <div className="msg-content">
        <div className="typing-bubble">
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
        </div>
      </div>
    </div>
  );
}

function SourceBadge({ source }) {
  const label = source.page
    ? `${source.filename} · p.${source.page}`
    : source.filename;

  return (
    <span className="source-badge">
      📄 {label}
      {source.excerpt && (
        <span className="source-tooltip">
          <strong style={{ color: 'var(--text)', display: 'block', marginBottom: 4 }}>
            {source.filename} {source.page ? `— Page ${source.page}` : ''}
          </strong>
          {source.excerpt}
        </span>
      )}
    </span>
  );
}

function FallbackBanner({ contactEmail, question }) {
  const subject = encodeURIComponent(`Policy Question: ${question}`);
  const body = encodeURIComponent(
    `Hi HR Team,\n\nI searched DocTalk AI and couldn't find an answer to my question:\n\n"${question}"\n\nCould you please help?\n\nThank you.`
  );
  const href = `mailto:${contactEmail}?subject=${subject}&body=${body}`;

  return (
    <div className="fallback-banner">
      <span>⚠️ No matching policy found in the documents.</span>
      <a href={href} className="btn btn-hr" style={{ textDecoration: 'none' }}>
        ✉️ Contact HR
      </a>
    </div>
  );
}

export default function ChatMessage({ message, userInitials }) {
  const isUser = message.role === 'user';

  return (
    <div className={`message-row ${isUser ? 'user' : ''}`}>
      {/* Avatar */}
      <div className={`msg-avatar ${isUser ? 'user' : 'ai'}`}>
        {isUser ? userInitials : '🤖'}
      </div>

      {/* Content */}
      <div className="msg-content">
        {/* Main bubble */}
        <div className={`msg-bubble ${isUser ? 'user' : 'ai'} ${message.is_fallback ? 'fallback' : ''}`}>
          {message.content}
        </div>

        {/* Source badges (AI only) */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="sources-row">
            {message.sources.map((src, i) => (
              <SourceBadge key={i} source={src} />
            ))}
          </div>
        )}

        {/* Fallback HR banner (AI only) */}
        {!isUser && message.is_fallback && (
          <FallbackBanner
            contactEmail={message.contact_email}
            question={message.question}
          />
        )}
      </div>
    </div>
  );
}