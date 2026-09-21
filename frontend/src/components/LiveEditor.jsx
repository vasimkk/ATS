import React, { useState } from 'react';
import {
  Download,
  Copy,
  Check,
  Printer,
  RotateCw,
  Sparkles,
  FileDown,
  CheckCircle2
} from 'lucide-react';

export default function LiveEditor({
  editorText,
  setEditorText,
  onReAnalyze,
  isAnalyzing
}) {
  const [copied, setCopied] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const wordCount = (str) => {
    if (!str) return 0;
    const matches = str.match(/\b\w+\b/g);
    return matches ? matches.length : 0;
  };

  const lineCount = (str) => {
    if (!str) return 0;
    return str.split('\n').length;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(editorText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>ATS Optimized Resume</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              padding: 40px;
              color: #111;
              line-height: 1.5;
              font-size: 11pt;
            }
            pre {
              white-space: pre-wrap;
              font-family: inherit;
            }
          </style>
        </head>
        <body>
          <pre>${editorText.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
          <script>
            window.onload = function() { window.print(); window.close(); }
          </script>
        </body>
      </html>
    `);
    printWindow.document.close();
  };

  const handleExportDocx = async () => {
    if (!editorText.trim()) return;

    setIsExporting(true);
    try {
      const res = await fetch('/api/export-docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: editorText,
          filename: 'ATS_Optimized_Resume.docx'
        })
      });

      if (!res.ok) throw new Error('Export failed');

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'ATS_Optimized_Resume.docx';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Failed to download DOCX: ' + err.message);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="glass-card">
      {/* Editor Toolbar */}
      <div className="editor-toolbar">
        <div>
          <h3 style={{ fontSize: '1.25rem', marginBottom: 2 }}>Interactive Resume Editor</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.84rem' }}>
            Edit directly, adjust wording, and re-scan instantly to track ATS score evolution.
          </p>
        </div>

        <div className="editor-actions">
          <button
            onClick={onReAnalyze}
            disabled={isAnalyzing}
            className="btn-primary"
            style={{ padding: '8px 18px', fontSize: '0.86rem' }}
            title="Re-run ATS check on edited resume text"
          >
            <RotateCw size={14} className={isAnalyzing ? 'spinner' : ''} />
            {isAnalyzing ? 'Analyzing...' : 'Re-Score ATS'}
          </button>

          <button
            onClick={handleExportDocx}
            disabled={isExporting}
            className="btn-secondary"
            style={{ padding: '8px 16px', fontSize: '0.86rem', borderColor: 'var(--emerald-border)' }}
            title="Export as ATS-clean Microsoft Word (.docx)"
          >
            <Download size={14} color="#10b981" />
            {isExporting ? 'Generating...' : 'Export DOCX'}
          </button>

          <button
            onClick={handleCopy}
            className="btn-secondary"
            style={{ padding: '8px 14px', fontSize: '0.86rem' }}
            title="Copy full resume text"
          >
            {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
            {copied ? 'Copied' : 'Copy'}
          </button>

          <button
            onClick={handlePrint}
            className="btn-secondary"
            style={{ padding: '8px 14px', fontSize: '0.86rem' }}
            title="Print or save as PDF"
          >
            <Printer size={14} />
            Print PDF
          </button>
        </div>
      </div>

      {/* Editor Body */}
      <textarea
        className="custom-textarea"
        value={editorText}
        onChange={(e) => setEditorText(e.target.value)}
        style={{
          minHeight: '480px',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.88rem',
          lineHeight: '1.6'
        }}
        placeholder="Type or tweak your tailored resume here..."
      />

      {/* Footer Stats */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
        <span className="panel-meta">
          {wordCount(editorText)} words • {editorText.length} characters • {lineCount(editorText)} lines
        </span>
        <span style={{ fontSize: '0.78rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: 4 }}>
          <CheckCircle2 size={13} />
          ATS Standard Layout Compliant
        </span>
      </div>
    </div>
  );
}
