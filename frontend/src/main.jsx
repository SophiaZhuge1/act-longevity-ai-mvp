import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  Activity,
  Brain,
  BookOpen,
  CheckCircle2,
  ClipboardList,
  FileText,
  HeartPulse,
  Home,
  MapPin,
  MessageCircle,
  Moon,
  Pause,
  Play,
  Salad,
  ShieldCheck,
  ShoppingBasket,
  Sparkles,
  Users,
  Utensils,
  Volume2,
} from 'lucide-react';
import './styles.css';

const API = import.meta.env.VITE_API_URL || '';

const demoAnswers = {
  dob: '1947-04-12',
  gender: 'Female',
  marital_status: 'Widowed',
  living_arrangement: 'Alone',
  care_support: 'Yes - children',
  education_level: 'Secondary',
  employment_status: 'Retired',
  employment_sector: 'Education',
  postcode: 'SW1A',
  vision_problem: 'No',
  hearing_problem: 'Yes',
  teeth_problem: 'No',
  falls_3_months: 'Yes',
  diet_concern: 'Yes',
  lost_3kg: 'No',
  regular_exercise: 'No',
  vaccinations: 'Not sure',
  bp_checked: 'No',
  sleep_hours: '6-7',
  sleep_quality: 'Mixed',
  protein_veg: 'A few days a week',
  shopping: 'Yes, with some difficulty',
  dressing: 'Yes, without help',
  bathing: 'Yes, with some difficulty',
  toileting: 'Yes, without help',
  transfers: 'Yes, with some difficulty',
  indoors: 'Yes, without help',
  home_problems: 'No',
  finance_problems: 'No',
  activities: 'No',
  lonely: 'Yes',
  sleep_trouble: 'Yes',
  moderate_pain: 'Yes',
  down_depressed: 'No',
  life_satisfied: 'Yes',
  often_bored: 'Yes',
  memory_more: 'No',
  forgetting: 'Yes',
  confused_day_place: 'No',
  memory_concern_other: 'No',
};

const scoreMeta = [
  ['staying_healthy', 'Staying Healthy', HeartPulse],
  ['independence', 'Independence', Activity],
  ['wellbeing', 'Wellbeing', Sparkles],
  ['accommodation', 'Quality of Accommodation', Home],
  ['financial_wellbeing', 'Financial Wellbeing', ShieldCheck],
];

function App() {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState(demoAnswers);
  const [profile, setProfile] = useState({ name: 'Margaret', age_band: '70-90', postcode: 'SW1A' });
  const [consent, setConsent] = useState({ report: true, analytics: true });
  const [waitlist, setWaitlist] = useState({ join: true, email: 'margaret@example.com', organisation: '', interest_type: 'Individual' });
  const [dashboard, setDashboard] = useState(null);
  const [chatText, setChatText] = useState('Can you suggest gentle exercises for me?');
  const [chatAnswer, setChatAnswer] = useState('');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const dashboardRef = useRef(null);

  useEffect(() => {
    fetch(`${API}/api/questions`)
      .then((res) => res.json())
      .then((data) => setQuestions(data.questions || []))
      .catch(() => setQuestions([]));
  }, []);

  const grouped = useMemo(() => {
    return questions.reduce((acc, question) => {
      acc[question.section] ||= [];
      acc[question.section].push(question);
      return acc;
    }, {});
  }, [questions]);

  async function submitAssessment() {
    if (!consent.report) {
      setNotice('Please confirm consent to create your summary report.');
      return;
    }
    try {
      setBusy(true);
      setNotice('Preparing your ACT taster report...');
      const payload = { profile: { ...profile, postcode: answers.postcode || profile.postcode }, answers, consent, waitlist };
      const response = await fetch(`${API}/api/assessments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        throw new Error(`Dashboard request failed with status ${response.status}`);
      }
      const data = await response.json();
      setDashboard(data);
      setNotice('Your summary report is ready.');
      window.setTimeout(() => dashboardRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
    } catch (error) {
      setNotice('The report could not be built. Please check that the Python backend is running on port 8000.');
    } finally {
      setBusy(false);
    }
  }

  async function askChat() {
    if (!dashboard?.user_id || !chatText.trim()) return;
    setBusy(true);
    const response = await fetch(`${API}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: dashboard.user_id, message: chatText }),
    });
    const data = await response.json();
    setChatAnswer(data.answer || '');
    setBusy(false);
  }

  return (
    <main className="app">
      <section className="topbar">
        <div>
          <p className="eyebrow">ACT Assess Free Taster</p>
          <h1>Take a 10-minute wellness check.</h1>
          <p className="lede">
            Get a plain-English summary of your priorities for support, prevention opportunities,
            clinical risks to discuss with your doctor and a Healthy Longevity spider-gram.
          </p>
          <div className="trust-strip">
            <span><CheckCircle2 size={18} /> Wellness, not diagnosis</span>
            <span><CheckCircle2 size={18} /> Built on ACT Assess</span>
            <span><CheckCircle2 size={18} /> AI support coming next</span>
          </div>
        </div>
        <div className="profile-card">
          <label>
            First name
            <input value={profile.name} onChange={(e) => setProfile({ ...profile, name: e.target.value })} />
          </label>
          <label>
            Postcode area
            <input value={answers.postcode || ''} onChange={(e) => setAnswers({ ...answers, postcode: e.target.value })} />
          </label>
          <WaitlistForm waitlist={waitlist} setWaitlist={setWaitlist} />
          <ConsentBox consent={consent} setConsent={setConsent} />
          <button onClick={submitAssessment} disabled={busy}>{busy ? 'Preparing...' : 'Get My Summary Report'}</button>
          {notice && <p className={notice.includes('could not') ? 'notice error' : 'notice'}>{notice}</p>}
        </div>
      </section>

      <section className="workspace">
        <Questionnaire grouped={grouped} answers={answers} setAnswers={setAnswers} />
        <Dashboard dashboard={dashboard} dashboardRef={dashboardRef} />
      </section>

      {dashboard && (
        <section className="chat-panel">
          <div>
            <p className="eyebrow">Premium Preview</p>
            <h2>Ask about your plan</h2>
          </div>
          <div className="chat-row">
            <input value={chatText} onChange={(e) => setChatText(e.target.value)} />
            <button onClick={askChat} disabled={busy}><MessageCircle size={20} /> Ask</button>
          </div>
          {chatAnswer && <p className="chat-answer">{chatAnswer}</p>}
        </section>
      )}
    </main>
  );
}

function WaitlistForm({ waitlist, setWaitlist }) {
  return (
    <div className="waitlist-box">
      <label className="check-row">
        <input
          type="checkbox"
          checked={waitlist.join}
          onChange={(e) => setWaitlist({ ...waitlist, join: e.target.checked })}
        />
        <span>Join the early interest list for ACT Healthy Longevity support</span>
      </label>
      {waitlist.join && (
        <div className="waitlist-fields">
          <label>
            Email for your PDF report
            <input value={waitlist.email} onChange={(e) => setWaitlist({ ...waitlist, email: e.target.value })} />
          </label>
          <label>
            Organisation, if relevant
            <input value={waitlist.organisation} onChange={(e) => setWaitlist({ ...waitlist, organisation: e.target.value })} placeholder="Optional" />
          </label>
          <div className="chips compact">
            {['Individual', 'Organisation'].map((option) => (
              <button
                className={waitlist.interest_type === option ? 'chip active' : 'chip'}
                key={option}
                onClick={() => setWaitlist({ ...waitlist, interest_type: option })}
                type="button"
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ConsentBox({ consent, setConsent }) {
  return (
    <div className="consent-box">
      <label className="check-row">
        <input
          type="checkbox"
          checked={consent.report}
          onChange={(e) => setConsent({ ...consent, report: e.target.checked })}
        />
        <span>I agree that ACT can use my answers to create this taster report.</span>
      </label>
      <label className="check-row">
        <input
          type="checkbox"
          checked={consent.analytics}
          onChange={(e) => setConsent({ ...consent, analytics: e.target.checked })}
        />
        <span>ACT may use anonymised answers to understand population wellbeing trends.</span>
      </label>
    </div>
  );
}

function Questionnaire({ grouped, answers, setAnswers }) {
  const sections = Object.entries(grouped);
  if (!sections.length) {
    return <section className="panel"><h2>Questionnaire</h2><p>Start the backend to load questions.</p></section>;
  }
  return (
    <section className="panel questionnaire">
      <div className="panel-head">
        <div>
          <p className="eyebrow">Wellness Check</p>
          <h2>Friendly check-in</h2>
        </div>
        <span className="badge">{Object.keys(answers).length} answers</span>
      </div>
      {sections.map(([section, items]) => (
        <div className="quest" key={section}>
          <h3>{section}</h3>
          {items.map((q) => (
            <Question key={q.id} question={q} value={answers[q.id] || ''} onChange={(value) => setAnswers({ ...answers, [q.id]: value })} />
          ))}
        </div>
      ))}
    </section>
  );
}

function Question({ question, value, onChange }) {
  if (question.type === 'date' || question.type === 'text') {
    return (
      <label className="question">
        <span>{question.text}</span>
        <input type={question.type === 'date' ? 'date' : 'text'} value={value} placeholder={question.placeholder} onChange={(e) => onChange(e.target.value)} />
      </label>
    );
  }
  return (
    <div className="question">
      <span>{question.text}</span>
      <div className="chips">
        {(question.options || []).map((option) => (
          <button className={value === option ? 'chip active' : 'chip'} key={option} onClick={() => onChange(option)} type="button">
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}

function Dashboard({ dashboard, dashboardRef }) {
  const [speaking, setSpeaking] = useState(false);

  function recommendationText() {
    const intro = `Hi ${dashboard.profile.name}. Here is your ACT taster summary. ${dashboard.persona}`;
    const priorities = dashboard.support_priorities.map((item) => `${item.title}. ${item.body}`).join(' ');
    const prevention = dashboard.prevention_opportunities.map((item) => `${item.title}. ${item.body}`).join(' ');
    const risks = dashboard.clinical_risks.map((item) => `${item.title}. ${item.body}`).join(' ');
    return `${intro} Priorities for support: ${priorities}. Prevention opportunities: ${prevention}. Clinical points to discuss: ${risks}`;
  }

  function speakRecommendations() {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(recommendationText());
    utterance.rate = 0.86;
    utterance.pitch = 1.02;
    utterance.volume = 1;
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    setSpeaking(true);
    window.speechSynthesis.speak(utterance);
  }

  function stopSpeaking() {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    setSpeaking(false);
  }

  if (!dashboard) {
    return (
      <section className="panel empty" ref={dashboardRef}>
        <FileText size={36} />
        <h2>Your taster report will appear here</h2>
        <p>Use the demo answers or change them, then create the ACT summary report.</p>
      </section>
    );
  }
  return (
    <section className="panel dashboard" ref={dashboardRef} tabIndex="-1">
      <div className="panel-head">
        <div>
          <p className="eyebrow">ACT Taster Report</p>
          <h2>{dashboard.profile.name}'s Healthy Longevity Profile</h2>
        </div>
        <span className="badge"><MapPin size={14} /> {dashboard.profile.postcode}</span>
      </div>
      <Radar scores={dashboard.scores} />
      <p className="persona">{dashboard.persona}</p>
      <div className="voice-card">
        <div>
          <Volume2 size={24} />
          <div>
            <strong>Read this out loud</strong>
            <span>A calm, friendly voice can read the summary and recommendations.</span>
          </div>
        </div>
        <button onClick={speaking ? stopSpeaking : speakRecommendations}>
          {speaking ? <Pause size={20} /> : <Play size={20} />}
          {speaking ? 'Stop' : 'Listen'}
        </button>
      </div>
      <DeliveryStatus delivery={dashboard.delivery} />
      <div className="recommendations">
        {dashboard.recommendations.map((item) => (
          <article key={item.title} className="recommendation-card">
            <ResourceIcon type={item.type} />
            <strong>{item.title}</strong>
            <p>{item.body}</p>
          </article>
        ))}
      </div>
      <ReportSection
        icon={ClipboardList}
        eyebrow="Your Priorities"
        title="Priorities for support"
        items={dashboard.support_priorities}
        emptyText="No major support priorities were identified from these answers."
      />
      <ReportSection
        icon={ShieldCheck}
        eyebrow="WHO Guidance"
        title="Prevention opportunities"
        items={dashboard.prevention_opportunities}
        emptyText="Your answers suggest your core prevention routines are broadly on track."
      />
      <ReportSection
        icon={HeartPulse}
        eyebrow="For Your Doctor"
        title="Clinical risks to discuss"
        items={dashboard.clinical_risks}
        emptyText="No major clinical discussion points were identified from this taster."
      />
      <h3>Local resources near you</h3>
      <div className="resources">
        {dashboard.resources.map((item) => (
          <a href={item.url} target="_blank" key={item.name} className="resource-card">
            <ResourceIcon type={item.kind} icon={item.icon} />
            <span>
              <strong>{item.name}</strong>
              <em>{item.why}</em>
            </span>
          </a>
        ))}
      </div>
      <h3>Do it at home videos</h3>
      <div className="video-grid">
        {dashboard.videos.map((item) => (
          <a href={item.url} target="_blank" key={item.title} className="video-card">
            <VideoThumb title={item.title} thumbnail={item.thumbnail} category={item.category} />
            <span>
              <small className={item.category === 'Food' ? 'video-category food' : 'video-category'}>
                {item.category || 'Home idea'}
              </small>
              <strong>{item.title}</strong>
              <em>{item.why || 'Follow-along videos to review with comfort and care.'}</em>
            </span>
          </a>
        ))}
      </div>
    </section>
  );
}

function DeliveryStatus({ delivery }) {
  if (!delivery) return null;
  const sent = delivery.email?.sent;
  const message = sent
    ? `A PDF copy of this report has been emailed to ${delivery.email.to}.`
    : delivery.email?.reason || 'The PDF report was prepared, but email has not been sent yet.';
  return (
    <div className={sent ? 'delivery-card sent' : 'delivery-card pending'}>
      <FileText size={22} />
      <div>
        <strong>{sent ? 'Report emailed' : 'PDF prepared'}</strong>
        <span>{message}</span>
      </div>
    </div>
  );
}

function ReportSection({ icon: Icon, eyebrow, title, items = [], emptyText }) {
  return (
    <section className="report-section">
      <div className="report-heading">
        <span className="card-icon"><Icon size={22} /></span>
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h3>{title}</h3>
        </div>
      </div>
      <div className="report-list">
        {(items.length ? items : [{ title: 'All steady', body: emptyText }]).map((item) => (
          <article key={item.title}>
            <strong>{item.title}</strong>
            <p>{item.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function VideoThumb({ title, thumbnail, category }) {
  if (thumbnail) {
    return <img src={thumbnail} alt="" />;
  }
  if (category === 'Food') {
    return (
      <span className="video-thumb-fallback food-thumb" aria-hidden="true">
        <Salad size={36} />
        <small>Easy healthy recipe</small>
      </span>
    );
  }
  return (
    <span className="video-thumb-fallback" aria-hidden="true">
      <Play size={34} />
      <small>{title}</small>
    </span>
  );
}

function ResourceIcon({ type, icon }) {
  const key = icon || type;
  const Icon = {
    movement: Activity,
    walking: Activity,
    sleep: Moon,
    nutrition: Salad,
    local: MapPin,
    social: Users,
    users: Users,
    learning: BookOpen,
    book: BookOpen,
    prevention: ShieldCheck,
    maintenance: HeartPulse,
    service: ShoppingBasket,
    shopping: ShoppingBasket,
    meal: Utensils,
    meal_delivery: Utensils,
    home: Home,
    finance: ShieldCheck,
  }[key] || Sparkles;
  return (
    <span className="card-icon">
      <Icon size={22} />
    </span>
  );
}

function Radar({ scores }) {
  const size = 430;
  const center = size / 2;
  const radius = 122;
  const labelRadius = 172;
  const points = scoreMeta.map(([key], index) => {
    const angle = -Math.PI / 2 + (2 * Math.PI * index) / scoreMeta.length;
    const value = (scores[key] || 0) / 100;
    return [center + Math.cos(angle) * radius * value, center + Math.sin(angle) * radius * value].join(',');
  });
  return (
    <div className="radar-wrap">
      <svg viewBox={`0 0 ${size} ${size}`} className="radar" role="img" aria-label="Five dimension Healthy Longevity spider-gram">
        {[0.25, 0.5, 0.75, 1].map((scale) => (
          <polygon key={scale} points={scoreMeta.map((_, index) => {
            const angle = -Math.PI / 2 + (2 * Math.PI * index) / scoreMeta.length;
            return [center + Math.cos(angle) * radius * scale, center + Math.sin(angle) * radius * scale].join(',');
          }).join(' ')} className="grid" />
        ))}
        {scoreMeta.map((_, index) => {
          const angle = -Math.PI / 2 + (2 * Math.PI * index) / scoreMeta.length;
          return <line key={index} x1={center} y1={center} x2={center + Math.cos(angle) * radius} y2={center + Math.sin(angle) * radius} className="axis" />;
        })}
        <polygon points={points.join(' ')} className="shape" />
        {scoreMeta.map(([key, label], index) => {
          const angle = -Math.PI / 2 + (2 * Math.PI * index) / scoreMeta.length;
          const x = center + Math.cos(angle) * labelRadius;
          const y = center + Math.sin(angle) * labelRadius;
          const lines = label.split(' ');
          return (
            <g key={key}>
              {lines.map((line, lineIndex) => (
                <text
                  key={line}
                  x={x}
                  y={y + (lineIndex - (lines.length - 1) / 2) * 17}
                  className="radar-label"
                  textAnchor="middle"
                >
                  {line}
                </text>
              ))}
            </g>
          );
        })}
      </svg>
      <div className="score-list">
        {scoreMeta.map(([key, label, Icon]) => (
          <div key={key}>
            <Icon size={18} />
            <span>{label}</span>
            <strong>{scores[key]}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
