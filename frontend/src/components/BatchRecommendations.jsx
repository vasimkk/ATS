import React from 'react';
import { Target, CheckCircle2, AlertTriangle, ArrowRight, TrendingUp, Send } from 'lucide-react';
import { JOB_DATABASE } from '../utils/sampleData';

export default function BatchRecommendations({ batchResults, onTargetRole }) {
  if (!batchResults || batchResults.length === 0) {
    return null;
  }

  const getBarColor = (val) => {
    if (val >= 75) return '#10b981';
    if (val >= 50) return '#f59e0b';
    return '#f43f5e';
  };

  const readyToApply = batchResults.filter(r => r.overall_score >= 75);
  const needsOptimization = batchResults.filter(r => r.overall_score < 75);

  const renderJobCard = (result, index, isTopSection) => {
    const jobInfo = JOB_DATABASE.find(j => j.id === result.jd_id);
    if (!jobInfo) return null;
    
    const isReady = result.overall_score >= 75;

    return (
      <div 
        key={result.jd_id} 
        className="glass-card" 
        style={{ 
          padding: '16px', 
          border: isTopSection && index === 0 ? '1px solid #10b981' : '1px solid var(--border-subtle)',
          background: isTopSection && index === 0 ? 'rgba(16, 185, 129, 0.05)' : 'rgba(255,255,255,0.02)'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
          <div>
            {isTopSection && index === 0 && (
              <span className="badge-emerald" style={{ fontSize: '0.65rem', marginBottom: 6, display: 'inline-block' }}>
                ★ Top Match
              </span>
            )}
            <h4 style={{ fontSize: '1.1rem', color: '#f8fafc', margin: 0 }}>
              {jobInfo.title}
            </h4>
          </div>
          <div style={{ 
            background: getBarColor(result.overall_score), 
            color: '#fff', 
            padding: '4px 8px', 
            borderRadius: '4px',
            fontWeight: 'bold',
            fontSize: '1rem'
          }}>
            {result.grade}
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Vector Match Score</span>
          <span style={{ fontSize: '0.9rem', fontWeight: 600, color: getBarColor(result.overall_score) }}>
            {result.overall_score}%
          </span>
        </div>
        
        <div className="metric-progress-bar" style={{ height: '6px', marginBottom: 16 }}>
          <div
            className="metric-progress-fill"
            style={{
              width: `${result.overall_score}%`,
              backgroundColor: getBarColor(result.overall_score)
            }}
          />
        </div>

        <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: 20, height: '40px', overflow: 'hidden' }}>
          {jobInfo.text.substring(0, 100)}...
        </div>

        {isReady ? (
          <button 
            onClick={() => alert(`Auto-applying for ${jobInfo.title} using your current resume!`)}
            className="btn-primary" 
            style={{ width: '100%', justifyContent: 'center', padding: '8px', fontSize: '0.85rem' }}
          >
            <Send size={14} style={{ marginRight: 6 }} />
            Auto Apply Now
          </button>
        ) : (
          <button 
            onClick={() => onTargetRole(jobInfo)}
            className="btn-secondary" 
            style={{ width: '100%', justifyContent: 'center', padding: '8px', fontSize: '0.85rem', borderColor: 'var(--amber-border)' }}
          >
            <Target size={14} style={{ marginRight: 6, color: '#fbbf24' }} />
            Update Resume First
            <ArrowRight size={14} style={{ marginLeft: 4 }} />
          </button>
        )}
      </div>
    );
  };

  return (
    <div className="batch-recommendations" style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      
      {/* Section 1: Ready to Apply */}
      {readyToApply.length > 0 && (
        <div className="glass-card" style={{ borderLeft: '4px solid #10b981' }}>
          <h3 style={{ fontSize: '1.4rem', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 10 }}>
            <CheckCircle2 size={22} color="#10b981" />
            Ready for Auto-Apply (≥75% Match)
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 20 }}>
            Your resume naturally resonates strongly with these positions based on semantic embedding alignment. You can apply directly.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 16 }}>
            {readyToApply.map((result, index) => renderJobCard(result, index, true))}
          </div>
        </div>
      )}

      {/* Section 2: Needs Optimization */}
      {needsOptimization.length > 0 && (
        <div className="glass-card" style={{ borderLeft: '4px solid #f59e0b' }}>
          <h3 style={{ fontSize: '1.4rem', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 10 }}>
            <AlertTriangle size={22} color="#f59e0b" />
            Needs Resume Optimization (&lt;75% Match)
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 20 }}>
            These roles are a partial match, but you are missing key semantic signals. You should optimize your resume before applying.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 16 }}>
            {needsOptimization.map((result, index) => renderJobCard(result, index, false))}
          </div>
        </div>
      )}

    </div>
  );
}
