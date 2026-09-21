import React, { useRef, useState } from 'react';
import {
  UploadCloud,
  FileText,
  CheckCircle,
  X,
  AlertCircle,
  FileCode,
  FileCheck,
  RefreshCw,
  Cpu,
  Layers,
  Sparkles,
  FileSpreadsheet
} from 'lucide-react';
import VectorDebugger from './VectorDebugger';

export default function DualInputPanel({
  resumeText,
  setResumeText,
  jdText,
  setJdText,
  uploadedFileName,
  setUploadedFileName,
  isUploading,
  setIsUploading,
  parsedResumeData,
  setParsedResumeData
}) {
  const fileInputRef = useRef(null);
  const [uploadError, setUploadError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [resumeViewMode, setResumeViewMode] = useState('text'); // 'text' | 'vector'

  const handleFileUpload = async (file) => {
    if (!file) return;

    setIsUploading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/parse-resume', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Upload failed with status ${res.status}`);
      }

      const data = await res.json();
      setResumeText(data.text);
      setUploadedFileName(data.filename);
      if (setParsedResumeData) {
        setParsedResumeData(data);
      }
    } catch (err) {
      setUploadError(err.message || 'Failed to parse file. Please upload a valid PDF or DOCX file.');
    } finally {
      setIsUploading(false);
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const wordCount = (str) => {
    if (!str) return 0;
    const matches = str.match(/\b\w+\b/g);
    return matches ? matches.length : 0;
  };

  const clearResume = () => {
    setResumeText('');
    setUploadedFileName(null);
    if (setParsedResumeData) {
      setParsedResumeData(null);
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
    setResumeViewMode('text');
  };

  return (
    <div style={{ maxWidth: '700px', margin: '0 auto' }}>
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: 'none' }}
        accept=".pdf,.docx,.doc,.txt"
        onChange={(e) => {
          if (e.target.files && e.target.files[0]) {
            handleFileUpload(e.target.files[0]);
          }
        }}
      />

      {/* Candidate Resume Panel */}
      <div className="glass-card input-panel">
        <div className="panel-header">
          <div className="panel-title">
            <FileText size={18} />
            <span>Candidate Resume (Upload Only)</span>
          </div>

          {uploadedFileName && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              {/* View Switcher: Text vs Vector Debugger */}
              <div className="presets-strip" style={{ padding: '2px 3px' }}>
                <button
                  type="button"
                  onClick={() => setResumeViewMode('text')}
                  className={`preset-btn ${resumeViewMode === 'text' ? 'active' : ''}`}
                  style={{ padding: '4px 10px', fontSize: '0.75rem', gap: 5 }}
                >
                  <FileText size={13} />
                  Text
                </button>
                <button
                  type="button"
                  onClick={() => setResumeViewMode('vector')}
                  className={`preset-btn ${resumeViewMode === 'vector' ? 'active' : ''}`}
                  style={{
                    padding: '4px 10px',
                    fontSize: '0.75rem',
                    gap: 5,
                    color: resumeViewMode === 'vector' ? '#fff' : '#c084fc'
                  }}
                  id="btn-inspect-vector"
                >
                  <Cpu size={13} color="#a855f7" />
                  Vector (384-D)
                </button>
              </div>

              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="btn-secondary"
                style={{ padding: '5px 10px', fontSize: '0.75rem', gap: 5 }}
                title="Replace current resume file"
              >
                <RefreshCw size={12} />
                Change
              </button>
            </div>
          )}
        </div>

        {uploadError && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '8px 12px',
            background: 'var(--rose-bg)',
            border: '1px solid var(--rose-border)',
            borderRadius: 'var(--radius-sm)',
            color: '#fb7185',
            fontSize: '0.82rem'
          }}>
            <AlertCircle size={15} />
            <span>{uploadError}</span>
          </div>
        )}

        {/* If no file uploaded, show Dropzone */}
        {!resumeText ? (
          <div
            className={`dropzone ${isDragging ? 'active' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="dropzone-icon">
              {isUploading ? (
                <div className="spinner" style={{ width: 26, height: 26, border: '3px solid var(--primary)', borderTopColor: 'transparent', borderRadius: '50%' }} />
              ) : (
                <UploadCloud size={32} />
              )}
            </div>
            <div className="dropzone-title">
              {isUploading ? 'Extracting Layout, Tables & Vectors...' : 'Upload Candidate Resume'}
            </div>
            <div className="dropzone-sub">
              Supports 1-page, 2-page, 3-page, multi-column sidebars & tabular resumes
            </div>
            <div className="dropzone-formats">
              <span className="format-badge">.PDF</span>
              <span className="format-badge">.DOCX</span>
              <span className="format-badge">.TXT</span>
            </div>
            <button
              type="button"
              className="btn-primary"
              style={{ marginTop: 8, padding: '8px 20px', fontSize: '0.86rem' }}
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
            >
              Select Resume File
            </button>
          </div>
        ) : (
          /* File uploaded view */
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, flex: 1 }}>
            {/* Uploaded File Pill with Quick Meta */}
            <div className="file-pill">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <FileCheck size={18} color="#10b981" />
                <span>Uploaded: <strong>{uploadedFileName || 'Candidate Resume'}</strong></span>
                {parsedResumeData?.page_count && (
                  <span className="badge-purple" style={{ fontSize: '0.72rem' }}>
                    {parsedResumeData.page_count} Page{parsedResumeData.page_count > 1 ? 's' : ''}
                  </span>
                )}
                {parsedResumeData?.layout_detected && (
                  <span className="badge-cyan" style={{ fontSize: '0.72rem' }}>
                    {parsedResumeData.layout_detected.split('(')[0].trim()}
                  </span>
                )}
                {parsedResumeData?.embedding_vector && (
                  <span
                    className="badge-emerald"
                    style={{ fontSize: '0.72rem', cursor: 'pointer' }}
                    onClick={() => setResumeViewMode('vector')}
                    title="Click to view 384-D vector debugger"
                  >
                    <Cpu size={11} style={{ marginRight: 4 }} />
                    384-D Vector Ready
                  </span>
                )}
              </div>
              <button
                type="button"
                onClick={clearResume}
                style={{ background: 'transparent', border: 'none', color: '#cbd5e1', cursor: 'pointer' }}
                title="Remove file"
              >
                <X size={15} />
              </button>
            </div>

            {/* View 1: Extracted Text */}
            {resumeViewMode === 'text' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, flex: 1 }}>
                <textarea
                  className="custom-textarea"
                  value={resumeText}
                  readOnly
                  rows={13}
                  style={{
                    cursor: 'default',
                    background: 'rgba(11, 17, 33, 0.65)',
                    color: '#cbd5e1',
                    userSelect: 'text'
                  }}
                  title="Parsed text from your resume file (Read Only)"
                />

                {/* Quick bar linking to Vector Debugger */}
                {parsedResumeData?.embedding_vector && (
                  <div
                    onClick={() => setResumeViewMode('vector')}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '8px 12px',
                      background: 'rgba(168, 85, 247, 0.1)',
                      border: '1px solid rgba(168, 85, 247, 0.3)',
                      borderRadius: 'var(--radius-sm)',
                      cursor: 'pointer',
                      fontSize: '0.78rem'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Cpu size={15} color="#c084fc" />
                      <span style={{ color: '#e9d5ff' }}>
                        Dense 384-D Vector created • {parsedResumeData.embedding_vector.stats?.active_dimensions || 384} active dimensions
                      </span>
                    </div>
                    <span style={{ color: '#a855f7', fontWeight: 600 }}>Open Vector Debugger →</span>
                  </div>
                )}
              </div>
            )}

            {/* View 2: Interactive Vector & Parser Debugger */}
            {resumeViewMode === 'vector' && (
              <VectorDebugger
                vectorData={parsedResumeData?.embedding_vector}
                parsedDoc={parsedResumeData}
              />
            )}
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span className="panel-meta">
            {resumeText ? `${wordCount(resumeText)} words parsed • Clean layout reconstructed` : 'Upload required for ATS scoring'}
          </span>
          {resumeText && (
            <button
              type="button"
              onClick={clearResume}
              style={{ background: 'none', border: 'none', color: 'var(--text-subtle)', cursor: 'pointer', fontSize: '0.8rem' }}
            >
              Clear File
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
