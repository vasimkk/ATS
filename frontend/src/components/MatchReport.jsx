import React, { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Layers,
  Cpu,
  BookOpen,
  FileCheck,
  TrendingUp,
  Sparkles,
  ArrowRight,
  Filter,
  Network,
  ChevronDown,
  ChevronUp,
  Copy,
  Check
} from 'lucide-react';
import ScoreGauge from './ScoreGauge';
import VectorDebugger from './VectorDebugger';

export default function MatchReport({ atsData, parsedResumeData, onNavigateToTailor }) {
  const [filterMode, setFilterMode] = useState('all'); // 'all', 'missing', 'matched'
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [showVectorDebugger, setShowVectorDebugger] = useState(false);
  const [activeVectorTabReport, setActiveVectorTabReport] = useState('resume');
  const [copiedJD, setCopiedJD] = useState(false);

  if (!atsData) return null;

  const {
    overall_score,
    grade,
    grade_label,
    metrics,
    keywords,
    readability,
    recommendations,
    experience_notes,
    vector_analysis
  } = atsData;

  // Categories list
  const allCats = new Set([
    ...Object.keys(keywords?.matched_by_category || {}),
    ...Object.keys(keywords?.missing_by_category || {})
  ]);
  const categoryList = ['All', ...Array.from(allCats)];

  // Helper for progress bar color
  const getBarColor = (val) => {
    if (val >= 75) return '#10b981';
    if (val >= 50) return '#f59e0b';
    return '#f43f5e';
  };

  return (
    <div className="results-hub">
      {/* 1. Score Overview Card */}
      <div className="glass-card">
        <div className="score-hero-grid">
          {/* Radial Score Gauge */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <ScoreGauge
              score={overall_score}
              grade={grade}
              label={grade_label}
              size={210}
            />
            <div style={{ marginTop: 8, textAlign: 'center' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Target ATS Match Score
              </span>
            </div>
          </div>

          {/* Breakdown Cards */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
              <div>
                <h3 style={{ fontSize: '1.4rem', marginBottom: 4 }}>ATS Compatibility Analysis</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', maxWidth: '800px', lineHeight: '1.5' }}>
                  Now, your Target ATS Match Score (the big circle gauge on the left) is calculated 100% based on the embedding vector match. It completely ignores formatting, exact keyword matches, and strict years of experience. Instead, it relies purely on the AI understanding the deeper semantic meaning of your resume's achievements and matching them point-by-point against the job description's responsibilities.
                </p>
              </div>

              {onNavigateToTailor && (
                <button
                  onClick={onNavigateToTailor}
                  className="btn-primary"
                  style={{ padding: '10px 20px', fontSize: '0.9rem' }}
                >
                  <Sparkles size={16} />
                  Update Resume for JD
                </button>
              )}
            </div>

            <div className="breakdown-grid">

              {/* Vector Embeddings Match */}
              <div className="metric-card" style={{ borderColor: 'rgba(168, 85, 247, 0.35)' }}>
                <div className="metric-card-header">
                  <span style={{ color: '#c084fc', fontWeight: 600 }}>Vector Embeddings</span>
                  <Network size={15} color="#a855f7" />
                </div>
                <div className="metric-card-score" style={{ color: '#e9d5ff' }}>
                  {metrics.vector_similarity || 65}%
                </div>
                <div className="metric-progress-bar">
                  <div
                    className="metric-progress-fill"
                    style={{
                      width: `${metrics.vector_similarity || 65}%`,
                      backgroundColor: getBarColor(metrics.vector_similarity || 65)
                    }}
                  />
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>

      {/* 2. Dense Vector Embeddings Point-by-Point Resonance */}
      {vector_analysis && vector_analysis.point_by_point_matches && vector_analysis.point_by_point_matches.length > 0 && (
        <div className="glass-card" style={{ borderLeft: '4px solid #a855f7' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
            <div>
              <h3 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: 8 }}>
                <Network size={20} color="#a855f7" />
                <span>Vector Embeddings (Point-by-Point Semantic Resonance)</span>
              </h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.86rem', marginTop: 2 }}>
                Vectorizes the resume into dense high-dimensional embeddings and calculates cosine similarity against each JD requirement point.
              </p>
            </div>

            <div className="vector-header-badges">
              <span className="vector-badge vector-badge-purple">
                {vector_analysis.embedding_type}
              </span>
              <span className="vector-badge vector-badge-cyan">
                {vector_analysis.coverage_percentage}% Requirements Vector-Covered
              </span>
              <span className="vector-badge vector-badge-emerald">
                {vector_analysis.overall_vector_similarity}% Vector Cosine Score
              </span>
              <button
                type="button"
                onClick={() => setShowVectorDebugger(!showVectorDebugger)}
                className="btn-secondary"
                style={{ padding: '4px 10px', fontSize: '0.75rem', gap: 5, borderColor: 'rgba(168, 85, 247, 0.4)' }}
                id="btn-toggle-report-vector-debug"
              >
                <Cpu size={13} color="#a855f7" />
                <span>{showVectorDebugger ? 'Hide Vector Debugger' : 'Debug 384-D Vectors'}</span>
                {showVectorDebugger ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
              </button>
            </div>
          </div>

          {/* Collapsible Vector Debugger Drawer */}
          {showVectorDebugger && (
            <div style={{ marginTop: 14, marginBottom: 16 }}>
              <div className="presets-strip" style={{ marginBottom: 10, padding: '4px', display: 'inline-flex' }}>
                <button
                   onClick={() => setActiveVectorTabReport('resume')}
                   className={`preset-btn ${activeVectorTabReport === 'resume' ? 'active' : ''}`}
                >
                  Candidate Resume Vector
                </button>
                <button
                   onClick={() => setActiveVectorTabReport('jd')}
                   className={`preset-btn ${activeVectorTabReport === 'jd' ? 'active' : ''}`}
                >
                  Job Description Vector
                </button>
              </div>
              <VectorDebugger
                vectorData={activeVectorTabReport === 'resume' ? 
                  (parsedResumeData?.embedding_vector || {
                    dimension: 384,
                    vector: vector_analysis.resume_vector || [],
                    stats: { norm: vector_analysis.vector_stats?.resume_norm || 1.0, active_dimensions: 384, sparsity_pct: 0 }
                  }) : {
                    dimension: 384,
                    vector: vector_analysis.jd_vector || [],
                    stats: { norm: vector_analysis.vector_stats?.jd_norm || 1.0, active_dimensions: 384, sparsity_pct: 0 }
                  }
                }
                parsedDoc={activeVectorTabReport === 'resume' ? parsedResumeData : null}
              />
            </div>
          )}

          <div className="vector-points-grid">
            {vector_analysis.point_by_point_matches.map((pt, idx) => (
              <div key={idx} className="vector-point-card">
                <div className="vector-point-top">
                  <div className="vector-jd-text">
                    <strong style={{ color: '#93c5fd', marginRight: 6 }}>JD Requirement #{idx + 1}:</strong>
                    {pt.jd_requirement}
                  </div>
                  <span
                    className="vector-sim-pill"
                    style={{
                      background: pt.status === 'high' ? 'var(--emerald-bg)' : pt.status === 'medium' ? 'var(--amber-bg)' : 'var(--rose-bg)',
                      border: `1px solid ${pt.status === 'high' ? 'var(--emerald-border)' : pt.status === 'medium' ? 'var(--amber-border)' : 'var(--rose-border)'}`,
                      color: pt.status === 'high' ? '#34d399' : pt.status === 'medium' ? '#fbbf24' : '#fb7185'
                    }}
                  >
                    {pt.vector_similarity}% Vector Match
                  </span>
                </div>

                <div className="vector-resume-match">
                  <strong style={{ color: '#cbd5e1' }}>Best Matching Resume Vector Point: </strong>
                  {pt.matched_resume_bullet}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}


      {/* 4. ATS Structural & Readability Checklist */}
      {readability && readability.checks && (
        <div className="glass-card">
          <h3 style={{ fontSize: '1.25rem', marginBottom: 6 }}>ATS Scanner Formatting Checklist</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.86rem', marginBottom: 16 }}>
            Verifies whether your document headers, bullet structures, and contact information pass automated ATS parsers (Taleo, Greenhouse, Workday).
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12 }}>
            {readability.checks.map((chk, i) => (
              <div key={i} className="checklist-item">
                <div className="checklist-icon">
                  {chk.status === 'pass' && <CheckCircle2 size={18} color="#10b981" />}
                  {chk.status === 'warning' && <AlertTriangle size={18} color="#f59e0b" />}
                  {chk.status === 'fail' && <XCircle size={18} color="#f43f5e" />}
                </div>
                <div className="checklist-body">
                  <h4 style={{ color: chk.status === 'fail' ? '#fb7185' : chk.status === 'warning' ? '#fbbf24' : '#f8fafc' }}>
                    {chk.name}
                  </h4>
                  <p>{chk.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 5. Actionable Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="glass-card" style={{ borderLeft: '4px solid var(--primary)' }}>
          <h3 style={{ fontSize: '1.25rem', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Sparkles size={18} color="var(--primary)" />
            <span>High-Priority ATS Optimization Tips</span>
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {recommendations.map((rec, i) => (
              <div
                key={i}
                style={{
                  padding: '12px 16px',
                  background: rec.type === 'critical' ? 'var(--rose-bg)' : 'rgba(99, 102, 241, 0.08)',
                  border: `1px solid ${rec.type === 'critical' ? 'var(--rose-border)' : 'var(--border-glow)'}`,
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12
                }}
              >
                <div>
                  <h4 style={{ fontSize: '0.92rem', marginBottom: 2, color: rec.type === 'critical' ? '#fb7185' : '#c7d2fe' }}>
                    {rec.title}
                  </h4>
                  <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)' }}>{rec.message}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
