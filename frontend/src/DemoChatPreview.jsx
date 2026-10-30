import React, { useState } from 'react';
import { ArrowLeft, ShieldCheck } from 'lucide-react';
import HealthChat from './HealthChat.jsx';
import sample from './demo-assessment.json';
import { scoreLabels } from './demo-chat.js';
export default function DemoChatPreview({ onBack }) {
  const [open, setOpen] = useState(true);
  return <main className="demo-preview"><button className="text-button" onClick={onBack}><ArrowLeft size={18}/> Back to wellness</button><p className="eyebrow">Sample profile · Nothing is saved</p><h1>A conversation<br/><em>about living well.</em></h1><p className="lede">Meet Alex, a fictional person who lives alone and reported a recent fall, limited exercise, nutrition concerns and trouble sleeping.</p><div className="demo-score-grid">{Object.entries(scoreLabels).map(([key,label]) => <article key={key}><span>{label}</span><strong>{sample.dashboard.scores[key]}<small>/100</small></strong></article>)}</div><h2>Alex’s chosen priorities</h2><div className="demo-priorities">{sample.dashboard.selected_priorities.map(item=><span key={item.id}>{item.title}</span>)}</div><p className="demo-local-note"><ShieldCheck size={20}/> Prepared replies use this sample’s answers and scores. Try a suggested question, then ask “What should I do first?” to see a follow-up.</p><HealthChat dashboard={sample.dashboard} answers={sample.answers} open={open} setOpen={setOpen}/></main>;
}
