
import React, { useState } from 'react';
import {
  Sparkles,
  ArrowRight,
  Copy,
  Check,
  Zap,
  Target,
  FileCheck2,
  FileCode,
  Download,
  Printer
} from 'lucide-react';
import confetti from 'canvas-confetti';

export default function ResumeTailor({
  originalText,
  tailoredData
}) {
  const [activeTab, setActiveTab] = useState('diff'); // 'diff', 'bullets', 'summary', 'skills'
  const [copiedKey, setCopiedKey] = useState(null);
  const [isExporting, setIsExporting] = useState(false);

  if (!tailoredData) return null;

  const {
    target_role,
    original_score,
    projected_score,
    score_delta,
    tailored_summary,
    tailored_bullets,
    optimized_skills,
    injected_keywords,
    full_optimized_resume
  } = tailoredData;

  const handleCopy = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleExportDocx = async () => {
    if (!full_optimized_resume.trim()) return;

    setIsExporting(true);
    try {
      const res = await fetch('/api/export-docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: full_optimized_resume,
          filename: 'ATS_Updated_Resume.docx'
        })
      });

      if (!res.ok) throw new Error('Export failed');

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'ATS_Updated_Resume.docx';
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

  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>ATS Updated Resume</title>
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
          <pre>${full_optimized_resume.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
          <script>
            window.onload = function() { window.print(); window.close(); }
          </script>
        </body>
      </html>
    `);
    printWindow.document.close();
  };

  const triggerCelebration = () => {
    confetti({
      particleCount: 80,
      spread: 70,
      origin: { y: 0.6 }
    });
  };

  return (
    <div className="tailor-studio">
      {/* 1. Score Delta Banner */}
      <div className="tailor-banner">
        <div className="tailor-banner-info">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <Sparkles size={20} color="#a855f7" />
            <span style={{ fontSize: '0.85rem', color: '#c084fc', fontWeight: 600, textTransform: 'uppercase' }}>
              Targeted Role: {target_role}
            </span>
          </div>
          <h3>Updated Resume Generated</h3>
          <p>
            Successfully incorporated {injected_keywords.length} critical keywords into STAR achievements, summary, and skills.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <div className="tailor-score-badge" onClick={triggerCelebration} style={{ cursor: 'pointer' }} title="Click for celebratory confetti!">
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>ATS Projection</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800 }}>
                {original_score}% → <span style={{ color: '#10b981' }}>{projected_score}%</span>
              </div>
            </div>
            {score_delta > 0 && (
              <span className="score-delta-tag">+{score_delta}%</span>
            )}
          </div>

          <button
            onClick={handleExportDocx}
            disabled={isExporting}
            className="btn-primary"
            style={{ padding: '10px 20px', fontSize: '0.88rem' }}
          >
            <Download size={15} />
            {isExporting ? 'Exporting...' : 'Download Word (.docx)'}
          </button>

          <button
            onClick={() => handleCopy(full_optimized_resume, 'top_full_resume')}
            className="btn-secondary"
            style={{ padding: '10px 16px', fontSize: '0.88rem' }}
          >
            {copiedKey === 'top_full_resume' ? <Check size={15} color="#10b981" /> : <Copy size={15} />}
            {copiedKey === 'top_full_resume' ? 'Copied' : 'Copy Resume'}
          </button>

          <button
            onClick={handlePrint}
            className="btn-secondary"
            style={{ padding: '10px 14px', fontSize: '0.88rem' }}
            title="Print or Save PDF"
          >
            <Printer size={15} />
            Print PDF
          </button>
        </div>
      </div>

      {/* 2. Sub-tabs Navigation */}
      <div className="tabs-header">
        <button
          onClick={() => setActiveTab('diff')}
          className={`tab-btn ${activeTab === 'diff' ? 'active' : ''}`}
        >
          <FileCode size={16} />
          Side-by-Side Diff
        </button>

        <button
          onClick={() => setActiveTab('bullets')}
          className={`tab-btn ${activeTab === 'bullets' ? 'active' : ''}`}
        >
          <Zap size={16} />
          STAR Bullet Points ({tailored_bullets?.length || 0})
        </button>

        <button
          onClick={() => setActiveTab('summary')}
          className={`tab-btn ${activeTab === 'summary' ? 'active' : ''}`}
        >
          <Target size={16} />
          Tailored Summary
        </button>

        <button
          onClick={() => setActiveTab('skills')}
          className={`tab-btn ${activeTab === 'skills' ? 'active' : ''}`}
        >
          <FileCheck2 size={16} />
          Optimized Skills Matrix
        </button>
      </div>

      {/* 3. Sub-tab Contents */}

      {/* Tab: Side-by-Side Diff */}
      {activeTab === 'diff' && (
        <div className="diff-grid">
          {/* Original Column */}
          <div className="diff-col">
            <div className="diff-header">
              <span>Original Resume</span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-subtle)' }}>Score: {original_score}%</span>
            </div>
            <div className="diff-content-box" style={{ opacity: 0.85 }}>
              {originalText}
            </div>
          </div>

          {/* Optimized Column */}
          <div className="diff-col">
            <div className="diff-header" style={{ borderColor: 'var(--emerald-border)', background: 'rgba(16, 185, 129, 0.08)' }}>
              <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: 6 }}>
                <Sparkles size={15} />
                Updated & ATS-Optimized Resume
              </span>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <span style={{ fontSize: '0.78rem', color: '#10b981', fontWeight: 700 }}>
                  Score: {projected_score}%
                </span>
                <button
                  onClick={() => handleCopy(full_optimized_resume, 'full_resume')}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: copiedKey === 'full_resume' ? '#10b981' : 'var(--text-muted)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4,
                    fontSize: '0.78rem'
                  }}
                >
                  {copiedKey === 'full_resume' ? <Check size={14} /> : <Copy size={14} />}
                  {copiedKey === 'full_resume' ? 'Copied' : 'Copy'}
                </button>
              </div>
            </div>
            <div className="diff-content-box" style={{ borderColor: 'rgba(16, 185, 129, 0.3)' }}>
              {full_optimized_resume}
            </div>
          </div>
        </div>
      )}

      {/* Tab: STAR Bullets */}
      {activeTab === 'bullets' && (
        <div className="glass-card">
          <div style={{ marginBottom: 16 }}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: 4 }}>STAR-Method Bullet Points</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.86rem' }}>
              Rewritten following the <strong>Situation, Task, Action, Result</strong> framework with injected target skills and quantified impact metrics.
            </p>
          </div>

          <div>
            {tailored_bullets?.map((b, idx) => (
              <div key={idx} className="bullet-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  {b.injected_skill && (
                    <span className="bullet-injected-badge">
                      <Sparkles size={11} />
                      Skill Injected: {b.injected_skill}
                    </span>
                  )}
                  <button
                    onClick={() => handleCopy(b.optimized, `bullet_${idx}`)}
                    className="btn-secondary"
                    style={{ padding: '4px 10px', fontSize: '0.75rem', marginLeft: 'auto' }}
                  >
                    {copiedKey === `bullet_${idx}` ? <Check size={12} color="#10b981" /> : <Copy size={12} />}
                    {copiedKey === `bullet_${idx}` ? 'Copied' : 'Copy Bullet'}
                  </button>
                </div>

                {b.original && b.original !== '(New bullet recommended to address missing keyword)' && (
                  <div className="bullet-original">
                    <strong>Original: </strong>{b.original}
                  </div>
                )}

                <div className="bullet-optimized">
                  <strong>Optimized: </strong>{b.optimized}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab: Tailored Executive Summary */}
      {activeTab === 'summary' && (
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div>
              <h3 style={{ fontSize: '1.2rem', marginBottom: 4 }}>Targeted Professional Summary</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.86rem' }}>
                Positioned directly for <strong>{target_role}</strong> and highlighting critical technologies.
              </p>
            </div>
            <button
              onClick={() => handleCopy(tailored_summary, 'summary')}
              className="btn-secondary"
              style={{ padding: '6px 14px', fontSize: '0.82rem' }}
            >
              {copiedKey === 'summary' ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
              {copiedKey === 'summary' ? 'Copied' : 'Copy Summary'}
            </button>
          </div>

          <div
            style={{
              padding: '20px',
              background: 'rgba(99, 102, 241, 0.08)',
              border: '1px solid rgba(99, 102, 241, 0.25)',
              borderRadius: 'var(--radius-md)',
              lineHeight: 1.7,
              fontSize: '0.96rem'
            }}
          >
            {tailored_summary}
          </div>
        </div>
      )}

      {/* Tab: Optimized Skills Matrix */}
      {activeTab === 'skills' && (
        <div className="glass-card">
          <div style={{ marginBottom: 16 }}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: 4 }}>Categorized Skills & Core Competencies</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.86rem' }}>
              Structured to maximize scan rates for ATS search filters.
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {Object.entries(optimized_skills || {}).map(([category, skills]) => (
              <div key={category} style={{ borderBottom: '1px solid var(--border-subtle)', paddingBottom: 12 }}>
                <h4 style={{ fontSize: '0.92rem', color: 'var(--text-muted)', marginBottom: 8 }}>
                  {category}
                </h4>
                <div className="chips-cloud">
                  {skills.map((s) => {
                    const isInjected = injected_keywords.some(
                      (k) => k.toLowerCase() === s.toLowerCase()
                    );
                    return (
                      <span
                        key={s}
                        className={`chip ${isInjected ? 'chip-matched' : ''}`}
                        style={{
                          background: isInjected ? 'var(--emerald-bg)' : 'rgba(255, 255, 255, 0.05)',
                          border: `1px solid ${isInjected ? 'var(--emerald-border)' : 'var(--border-subtle)'}`,
                          color: isInjected ? '#34d399' : 'var(--text-main)'
                        }}
                      >
                        {isInjected ? `+ ${s} (Added)` : s}
                      </span>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
