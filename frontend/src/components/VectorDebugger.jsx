import React, { useState } from 'react';
import {
  Cpu,
  Copy,
  Check
} from 'lucide-react';

export default function VectorDebugger({
  vectorData,
  parsedDoc,
  compact = false
}) {
  const [copied, setCopied] = useState(false);

  if (!vectorData && !parsedDoc) {
    return null;
  }

  const vectorList = vectorData?.vector || [];

  const handleCopy = () => {
    if (!vectorList || vectorList.length === 0) return;
    navigator.clipboard.writeText(JSON.stringify(vectorList, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="vector-debugger-container">
      {/* Header Bar */}
      <div className="vector-debugger-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div className="vector-header-icon">
            <Cpu size={18} color="#a855f7" />
          </div>
          <div>
            <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: '#f8fafc' }}>
              Raw Vector Data
            </h4>
            <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Float32 Vector Array
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button
            type="button"
            onClick={handleCopy}
            className="btn-secondary"
            style={{ padding: '4px 10px', fontSize: '0.75rem', gap: 5 }}
            title="Copy vector as JSON"
          >
            {copied ? <Check size={13} color="#10b981" /> : <Copy size={13} />}
            <span>{copied ? 'Copied!' : 'Copy Data'}</span>
          </button>
        </div>
      </div>

      <div className="raw-vector-box" style={{ marginTop: '16px' }}>
        <pre className="raw-vector-code">
          {JSON.stringify(vectorList, null, 2)}
        </pre>
      </div>
    </div>
  );
}
