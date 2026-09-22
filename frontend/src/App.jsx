import React, { useState } from 'react';
import Navbar from './components/Navbar';
import DualInputPanel from './components/DualInputPanel';
import MatchReport from './components/MatchReport';
import ResumeTailor from './components/ResumeTailor';
import BatchRecommendations from './components/BatchRecommendations';
import { JOB_DATABASE } from './utils/sampleData';
import {
  Sparkles,
  BarChart3,
  Edit3,
  FileCheck,
  AlertCircle,
  ArrowRight
} from 'lucide-react';
import confetti from 'canvas-confetti';

export default function App() {
  // Clean initial state with zero static data
  const [resumeText, setResumeText] = useState('');
  const [jdText, setJdText] = useState('');
  const [uploadedFileName, setUploadedFileName] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [parsedResumeData, setParsedResumeData] = useState(null);

  // Results & Analysis states
  const [atsData, setAtsData] = useState(null);
  const [tailoredData, setTailoredData] = useState(null);
  const [batchResults, setBatchResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isBatchAnalyzing, setIsBatchAnalyzing] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Tab navigation: 'input' | 'report' | 'tailor'
  const [activeTab, setActiveTab] = useState('input');

  // Run ATS Match Analysis
  const handleAnalyzeATS = async () => {
    if (!resumeText.trim() || !jdText.trim()) {
      setErrorMsg('Please provide both candidate resume and job description.');
      return;
    }

    setIsAnalyzing(true);
    setErrorMsg(null);

    try {
      const res = await fetch('/api/analyze-ats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: resumeText,
          job_description: jdText
        })
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Analysis failed with status ${res.status}`);
      }

      const data = await res.json();
      setAtsData(data);
      setActiveTab('report');

      if (data.overall_score >= 80) {
        confetti({ particleCount: 70, spread: 60, origin: { y: 0.6 } });
      }
    } catch (err) {
      setErrorMsg(err.message || 'Error running ATS analysis.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Run Resume Update / Tailoring
  const handleOptimizeResume = async () => {
    if (!resumeText.trim() || !jdText.trim()) {
      setErrorMsg('Please provide both resume and job description.');
      return;
    }

    setIsOptimizing(true);
    setErrorMsg(null);

    try {
      const res = await fetch('/api/optimize-resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: resumeText,
          job_description: jdText
        })
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Optimization failed with status ${res.status}`);
      }

      const data = await res.json();
      setTailoredData(data);
      setActiveTab('tailor');
      confetti({ particleCount: 90, spread: 75, origin: { y: 0.5 } });
    } catch (err) {
      setErrorMsg(err.message || 'Error updating resume.');
    } finally {
      setIsOptimizing(false);
    }
  };

  // Run Batch Analysis for Recommendations
  const handleBatchAnalyze = async () => {
    if (!resumeText.trim()) {
      setErrorMsg('Please upload or paste your resume first.');
      return;
    }

    setIsBatchAnalyzing(true);
    setErrorMsg(null);

    try {
      const res = await fetch('/api/analyze-ats-batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: resumeText,
          job_descriptions: JOB_DATABASE
        })
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Batch analysis failed with status ${res.status}`);
      }

      const data = await res.json();
      setBatchResults(data.ranked_matches);
      setActiveTab('batch_results');
      confetti({ particleCount: 50, spread: 40, origin: { y: 0.6 } });
    } catch (err) {
      setErrorMsg(err.message || 'Error finding recommended jobs.');
    } finally {
      setIsBatchAnalyzing(false);
    }
  };

  const handleTargetRole = async (jobInfo) => {
    setJdText(jobInfo.text);

    setIsAnalyzing(true);
    setErrorMsg(null);

    try {
      const res = await fetch('/api/analyze-ats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: resumeText,
          job_description: jobInfo.text
        })
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Analysis failed with status ${res.status}`);
      }

      const data = await res.json();
      setAtsData(data);
      setActiveTab('report');

      if (data.overall_score >= 80) {
        confetti({ particleCount: 70, spread: 60, origin: { y: 0.6 } });
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setErrorMsg(err.message || 'Error running ATS analysis.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="app-container">
      {/* Top Navbar with Centered Logo & Title */}
      <Navbar />

      {/* Hero Header */}
      <section className="hero-banner">

        <h2 className="hero-title">
          Align Your Resume with Any <br />
          <span className="gradient-highlight">Target Job Description</span>
        </h2>
        <p className="hero-subtitle">
          Extract ATS match percentages, detect missing hard/soft skills, generate STAR-method achievements, and export interview-ready resumes in seconds.
        </p>
      </section>

      {/* Primary Action Button Bar */}
      <div className="action-bar">
        <button
          onClick={handleBatchAnalyze}
          disabled={isAnalyzing || isOptimizing || isBatchAnalyzing}
          className="btn-primary"
          style={{ background: 'linear-gradient(135deg, #a855f7, #6366f1)' }}
        >
          {isBatchAnalyzing ? (
            <>
              <div className="spinner" style={{ width: 18, height: 18, border: '2px solid #fff', borderTopColor: 'transparent', borderRadius: '50%' }} />
              Scanning Job Database...
            </>
          ) : (
            <>
              <Sparkles size={18} />
              Find Recommended Jobs
            </>
          )}
        </button>
      </div>

      {/* Error Alert */}
      {errorMsg && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            padding: '12px 18px',
            background: 'var(--rose-bg)',
            border: '1px solid var(--rose-border)',
            borderRadius: 'var(--radius-md)',
            color: '#fb7185',
            marginBottom: '24px',
            fontSize: '0.9rem'
          }}
        >
          <AlertCircle size={18} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Tabs (when data is ready) */}
      {(atsData || tailoredData || batchResults) && (
        <div className="tabs-header" style={{ marginBottom: '24px' }}>
          <button
            onClick={() => setActiveTab('input')}
            className={`tab-btn ${activeTab === 'input' ? 'active' : ''}`}
          >
            <Edit3 size={16} />
            Source Inputs
          </button>

          {batchResults && (
            <button
              onClick={() => setActiveTab('batch_results')}
              className={`tab-btn ${activeTab === 'batch_results' ? 'active' : ''}`}
            >
              <Sparkles size={16} />
              Job Matches
            </button>
          )}

          {atsData && (
            <button
              onClick={() => setActiveTab('report')}
              className={`tab-btn ${activeTab === 'report' ? 'active' : ''}`}
            >
              <BarChart3 size={16} />
              Vector Match Score ({atsData.overall_score}%)
            </button>
          )}

          {tailoredData && (
            <button
              onClick={() => setActiveTab('tailor')}
              className={`tab-btn ${activeTab === 'tailor' ? 'active' : ''}`}
            >
              <Sparkles size={16} />
              Updated Resume (+{tailoredData.score_delta}%)
            </button>
          )}
        </div>
      )}

      {/* Tab 1: Input Panel */}
      {activeTab === 'input' && (
        <DualInputPanel
          resumeText={resumeText}
          setResumeText={setResumeText}
          jdText={jdText}
          setJdText={setJdText}
          uploadedFileName={uploadedFileName}
          setUploadedFileName={setUploadedFileName}
          isUploading={isUploading}
          setIsUploading={setIsUploading}
          parsedResumeData={parsedResumeData}
          setParsedResumeData={setParsedResumeData}
        />
      )}

      {/* Tab 2: Match Report */}
      {activeTab === 'report' && atsData && (
        <MatchReport
          atsData={atsData}
          parsedResumeData={parsedResumeData}
          onNavigateToTailor={handleOptimizeResume}
        />
      )}

      {/* Tab: Batch Results */}
      {activeTab === 'batch_results' && batchResults && (
        <BatchRecommendations
          batchResults={batchResults}
          onTargetRole={handleTargetRole}
        />
      )}

      {/* Tab 3: Updated Resume & STAR Bullets */}
      {activeTab === 'tailor' && tailoredData && (
        <ResumeTailor
          originalText={resumeText}
          tailoredData={tailoredData}
        />
      )}

    
    </div>
  );
}
