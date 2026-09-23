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
                  Your Target ATS Match Score is calculated using a hybrid matching engine. It combines keyword density, skill overlap, and cosine similarity (60% of total score) with a point-by-point Deep LLM semantic vector pass (40% of total score) to fully understand the alignment between your resume and the target job description.
                </p>
              </div>

            </div>

            <div className="breakdown-grid" style={{ gridTemplateColumns: '1fr' }}>

              {/* Formula Debugger Card */}
              <div className="metric-card" style={{ borderColor: 'rgba(56, 189, 248, 0.35)' }}>
                <div className="metric-card-header">
                  <span style={{ color: '#38bdf8', fontWeight: 600 }}>Algorithm Debugger (F1-F4)</span>
                  <Cpu size={15} color="#0ea5e9" />
                </div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: 8, display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>F1 (Cosine Similarity):</span>
                    <strong>{metrics.f1_weight_20} / 20 pts</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>F2 (Keyword Density):</span>
                    <strong>{metrics.f2_weight_20} / 20 pts</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>F3 (Skill Overlap):</span>
                    <strong>{metrics.f3_weight_20} / 20 pts</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>F4 (Deep LLM Pass):</span>
                    <strong>{metrics.f4_weight_40} / 40 pts</strong>
                  </div>
                  <div style={{ width: '100%', height: 1, background: 'rgba(255,255,255,0.1)', margin: '4px 0' }} />
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: '#10b981', fontWeight: 'bold' }}>
                    <span>Total ATS Score (F1 + F2 + F3 + F4):</span>
                    <strong>{metrics.f1_weight_20} + {metrics.f2_weight_20} + {metrics.f3_weight_20} + {metrics.f4_weight_40} = {overall_score}%</strong>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>


      {/* 4. ATS Scoring Engine Methodology Explanation */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1.25rem', marginBottom: 6 }}>How the ATS Engine Scores You</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.86rem', marginBottom: 12 }}>
          Your total score is a combination of 4 distinct analytical passes.
        </p>

        <div style={{
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.2)',
          padding: '10px 14px',
          borderRadius: '6px',
          marginBottom: '20px',
          fontFamily: 'monospace',
          color: '#10b981',
          fontSize: '0.9rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>Score Calculation:</span>
          <strong>{metrics.f1_weight_20} + {metrics.f2_weight_20} + {metrics.f3_weight_20} + {metrics.f4_weight_40} = {overall_score}%</strong>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12 }}>
          <div className="checklist-item">
            <div className="checklist-icon"><CheckCircle2 size={18} color="#38bdf8" /></div>
            <div className="checklist-body">
              <h4 style={{ color: '#38bdf8' }}>F1: Dense Vector Similarity (20%)</h4>
              <p>Extracts your core skills and pushes them through a 384-dimensional semantic space to measure their conceptual distance to the job description.</p>
              <div style={{ marginTop: '8px', fontSize: '0.8rem', color: '#94a3b8', background: 'rgba(255,255,255,0.05)', padding: '8px', borderRadius: '4px', fontFamily: 'monospace' }}>
                <div style={{ marginBottom: '6px', color: '#7dd3fc', borderBottom: '1px dashed rgba(255,255,255,0.2)', paddingBottom: '4px' }}>
                  <strong>Cosine Math (Debug):</strong><br/>
                  Raw Cosine Similarity (Resume Vector × JD Vector) = {vector_analysis?.vector_stats?.cosine_similarity || 0}<br/>
                  <span style={{ fontSize: '0.75rem', color: '#38bdf8', fontStyle: 'italic', display: 'block', marginBottom: '4px' }}>
                    * What this means: 1.0 is a perfect conceptual match, 0.0 means completely unrelated, and negative means opposite concepts.
                  </span>
                  <em>Curve Formula: √(max(0, {vector_analysis?.vector_stats?.cosine_similarity || 0})) * 100</em>
                </div>
                <strong style={{ color: '#bae6fd' }}>Step 1:</strong> Curved Base Score = {metrics.f1_cosine}/100<br />
                <strong style={{ color: '#bae6fd' }}>Step 2:</strong> Apply 20% Weight: {metrics.f1_cosine} * 0.20 = <strong style={{ color: '#fff' }}>{metrics.f1_weight_20} pts</strong>
              </div>
            </div>
          </div>
          <div className="checklist-item">
            <div className="checklist-icon"><CheckCircle2 size={18} color="#38bdf8" /></div>
            <div className="checklist-body">
              <h4 style={{ color: '#38bdf8' }}>F2: Keyword Density (20%)</h4>
              <p>Calculates the raw word-for-word overlap density between your resume and the exact vocabulary used by the hiring manager.</p>
              <div style={{ marginTop: '8px', fontSize: '0.8rem', color: '#94a3b8', background: 'rgba(255,255,255,0.05)', padding: '8px', borderRadius: '4px', fontFamily: 'monospace' }}>
                <div style={{ marginBottom: '6px', color: '#7dd3fc', borderBottom: '1px dashed rgba(255,255,255,0.2)', paddingBottom: '4px' }}>
                  <strong>Keyword Density Math (Debug):</strong><br/>
                  Total Unique JD Words = {metrics.f2_jd_words || 0}<br/>
                  Matched Resume Words = {metrics.f2_matched_words || 0}<br/>
                  <em>Formula: (Matched / JD Words) * 100 * 1.5 Multiplier</em>

                  {metrics.f2_matched_words_list && (
                    <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px dashed rgba(255,255,255,0.1)' }}>
                      <strong style={{ color: '#10b981', display: 'block', marginBottom: '4px', fontSize: '0.75rem' }}>Matched Words (F2 Component):</strong>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '8px' }}>
                        {metrics.f2_matched_words_list.map((w, i) => <span key={i} style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981', padding: '2px 6px', borderRadius: '4px', fontSize: '0.7rem' }}>{w}</span>)}
                      </div>
                      
                      <strong style={{ color: '#fb7185', display: 'block', marginBottom: '4px', fontSize: '0.75rem' }}>Missing Words (F2 Component):</strong>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                        {metrics.f2_missing_words_list?.map((w, i) => <span key={i} style={{ background: 'rgba(244, 63, 94, 0.15)', color: '#fb7185', padding: '2px 6px', borderRadius: '4px', fontSize: '0.7rem' }}>{w}</span>)}
                      </div>
                    </div>
                  )}
                </div>
                <strong style={{ color: '#bae6fd' }}>Step 1:</strong> Base Keyword Density = {metrics.f2_keyword}/100<br />
                <strong style={{ color: '#bae6fd' }}>Step 2:</strong> Apply 20% Weight: {metrics.f2_keyword} * 0.20 = <strong style={{ color: '#fff' }}>{metrics.f2_weight_20} pts</strong>
              </div>
            </div>
          </div>

          <div className="checklist-item">
            <div className="checklist-icon"><CheckCircle2 size={18} color="#38bdf8" /></div>
            <div className="checklist-body">
              <h4 style={{ color: '#38bdf8' }}>F3: Skill Overlap (20%)</h4>
              <p>A direct, taxonomy-based evaluation mapping how many explicit hard and soft skills requested in the JD are present in your resume.</p>
              <div style={{ marginTop: '8px', fontSize: '0.8rem', color: '#94a3b8', background: 'rgba(255,255,255,0.05)', padding: '8px', borderRadius: '4px', fontFamily: 'monospace' }}>
                <div style={{ marginBottom: '6px', color: '#7dd3fc', borderBottom: '1px dashed rgba(255,255,255,0.2)', paddingBottom: '4px' }}>
                  <strong>Skill Overlap Math (Debug):</strong><br/>
                  Tech Match = ({metrics.f3_matched_tech || 0} Matched / {metrics.f3_jd_tech || 0} Total JD Tech Skills) * 100 = {metrics.technical_skills_match}%<br/>
                  Soft Match = ({metrics.f3_matched_soft || 0} Matched / {metrics.f3_jd_soft || 0} Total JD Soft Skills) * 100 = {metrics.soft_skills_match}%<br/>
                  <em>Formula: Average(Tech Match, Soft Match)</em>
                </div>
                <strong style={{ color: '#bae6fd' }}>Step 1:</strong> Base Skill Overlap = {metrics.f3_skill}/100<br />
                <strong style={{ color: '#bae6fd' }}>Step 2:</strong> Apply 20% Weight: {metrics.f3_skill} * 0.20 = <strong style={{ color: '#fff' }}>{metrics.f3_weight_20} pts</strong>
              </div>
            </div>
          </div>

          <div className="checklist-item">
            <div className="checklist-icon"><Cpu size={18} color="#a855f7" /></div>
            <div className="checklist-body">
              <h4 style={{ color: '#a855f7' }}>F4: Deep LLM Analysis (40%)</h4>
              <p>A true Generative AI recruiter analyzes your actual bullet points for contextual alignment, impact, and relevancy to the role.</p>
              <div style={{ marginTop: '8px', fontSize: '0.8rem', color: '#94a3b8', background: 'rgba(255,255,255,0.05)', padding: '6px 8px', borderRadius: '4px', fontFamily: 'monospace' }}>
                Calculation: F4_Base_Score * 0.40 = {metrics.f4_weight_40}<br />
                <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid rgba(255,255,255,0.1)', fontFamily: 'inherit', color: '#e9d5ff', lineHeight: '1.4' }}>
                  <strong style={{ color: '#c084fc' }}>AI Recruiter Feedback (Debug): </strong>
                  {atsData.llm_analysis?.reasoning || 'No detailed reasoning provided by the LLM.'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Deep Debugging Details */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1.25rem', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
          <BookOpen size={18} color="#0ea5e9" />
          <span>Deep Debugging: Keyword Matches</span>
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.86rem', marginBottom: 12 }}>
          Detailed breakdown of exact skills found vs. missing. These directly drive the F2 (Keyword Density) and F3 (Skill Overlap) scores.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <div style={{ background: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: '6px', padding: '12px' }}>
            <h4 style={{ color: '#10b981', marginBottom: '8px', fontSize: '0.95rem' }}>Matched Skills ({keywords?.total_matched || 0})</h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {keywords?.matched_skills?.length > 0 ? keywords.matched_skills.map((skill, i) => (
                <span key={i} style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', padding: '2px 6px', borderRadius: '4px', fontSize: '0.8rem', fontFamily: 'monospace' }}>{skill}</span>
              )) : <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>None found</span>}
            </div>
          </div>
          <div style={{ background: 'rgba(244, 63, 94, 0.05)', border: '1px solid rgba(244, 63, 94, 0.2)', borderRadius: '6px', padding: '12px' }}>
            <h4 style={{ color: '#fb7185', marginBottom: '8px', fontSize: '0.95rem' }}>Missing Skills ({keywords?.total_missing || 0})</h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {keywords?.missing_skills?.length > 0 ? keywords.missing_skills.map((skill, i) => (
                <span key={i} style={{ background: 'rgba(244, 63, 94, 0.1)', color: '#fb7185', padding: '2px 6px', borderRadius: '4px', fontSize: '0.8rem', fontFamily: 'monospace' }}>{skill}</span>
              )) : <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>None missing</span>}
            </div>
          </div>
        </div>
      </div>

      {/* Deep Debugging: Semantic Matches */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1.25rem', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Network size={18} color="#0ea5e9" />
          <span>Deep Debugging: Semantic Vector Matches (F1)</span>
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.86rem', marginBottom: 12 }}>
          Point-by-point semantic resonance map showing exactly which resume bullets matched which JD requirements.
        </p>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {vector_analysis?.point_by_point_matches?.map((match, i) => (
            <div key={i} style={{ padding: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.85rem', color: '#38bdf8', fontWeight: 'bold' }}>JD Requirement:</span>
                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 'bold', color: match.status === 'high' ? '#10b981' : match.status === 'medium' ? '#f59e0b' : '#f43f5e', display: 'block' }}>
                    {match.vector_similarity}% Match
                  </span>
                  {match.raw_cosine !== undefined && (
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Raw Cosine: {match.raw_cosine}</span>
                  )}
                </div>
              </div>
              <p style={{ fontSize: '0.9rem', marginBottom: '10px' }}>"{match.jd_requirement}"</p>
              
              <div style={{ fontSize: '0.85rem', color: '#10b981', fontWeight: 'bold', marginBottom: '4px' }}>Matched Resume Section:</div>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>"{match.matched_resume_bullet}"</p>
            </div>
          ))}
          {(!vector_analysis?.point_by_point_matches || vector_analysis.point_by_point_matches.length === 0) && (
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No point-by-point data available.</span>
          )}
        </div>
      </div>


    </div>
  );
}
