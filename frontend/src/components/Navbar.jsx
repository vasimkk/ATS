import React from 'react';
import { FileText } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="navbar navbar-centered">
      <div className="brand-group brand-centered">
        <div className="brand-icon">
          <FileText size={24} strokeWidth={2.2} />
        </div>
        <div className="brand-text">
          <h1>ResuMatch ATS</h1>
          <span>AI Resume Optimizer & JD Matcher</span>
        </div>
      </div>
    </header>
  );
}
