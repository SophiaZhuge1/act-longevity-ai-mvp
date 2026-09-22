import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  Activity, ArrowLeft, ArrowRight, BookOpen, CalendarDays, Check, CheckCircle2,
  ClipboardList, Copy, FileText, HeartPulse, History, Home, LockKeyhole, MapPin,
  Minus, Moon, Pause, Play, Salad, Send, ShieldCheck, ShoppingBasket, Sparkles,
  TrendingDown, TrendingUp, Users, Utensils, Volume2, X,
} from 'lucide-react';
import './styles.css';

const API = import.meta.env.VITE_API_URL || '';
const sectionOrder = ['Staying Healthy', 'Independence', 'Wellbeing'];
const sectionCopy = {
  'Staying Healthy': ['Your everyday foundations', 'Health checks, movement, nutrition and prevention'],
  Independence: ['Living life your way', 'How confidently you manage everyday activities'],
  Wellbeing: ['How you feel and think', 'Sleep, pain, mood, connection and memory'],
};
const scoreMeta = [
  ['staying_healthy', 'Staying Healthy', HeartPulse, 'coral'],
  ['independence', 'Independence', Activity, 'blue'],
  ['wellbeing', 'Wellbeing', Sparkles, 'amber'],
  ['social_resources', 'Social Resources', Users, 'green'],
  ['clinical_risk', 'Clinical Risk', ClipboardList, 'violet'],
];
function questionIsVisible(question, answers) {
  if (!question.show_if?.length) return true;
  const matches = question.show_if.map((condition) => answers[condition.id] === condition.value);
  return question.show_if_mode === 'any' ? matches.some(Boolean) : matches.every(Boolean);
}
function App() {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [profile, setProfile] = useState({
    name: '', postcode: '', dob: '', gender: '', marital_status: '', phone: '', address: '', country: 'United Kingdom',
    living_arrangement: '', care_support: '', employment_status: '', employment_sector: '',
  });
  const [waitlist, setWaitlist] = useState({ join: true, email: '', organisation: '', interest_type: 'Individual' });
  const [consent, setConsent] = useState({ report: false, analytics: false });
  const [stage, setStage] = useState('welcome');
  const [activeSection, setActiveSection] = useState(0);
  const [dashboard, setDashboard] = useState(null);
  const [concerns, setConcerns] = useState([]);
  const [selectedPriorities, setSelectedPriorities] = useState([]);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const [chatOpen, setChatOpen] = useState(false);
  const [memberAccess, setMemberAccess] = useState({ email: '', access_code: '', authenticated: false });
  const [history, setHistory] = useState([]);
  const resultsRef = useRef(null);

  useEffect(() => {
    fetch(`${API}/api/questions`)
      .then((response) => {
        if (!response.ok) throw new Error('Questions unavailable');
        return response.json();
      })
      .then((data) => setQuestions(data.questions || []))
      .catch(() => setNotice('The assessment could not connect to the local service. Please start the Python backend.'));
  }, []);

  const visibleQuestions = useMemo(() => questions.filter((question) => questionIsVisible(question, answers)), [questions, answers]);
  const grouped = useMemo(() => visibleQuestions.reduce((all, question) => {
    all[question.section] ||= [];
    all[question.section].push(question);
    return all;
  }, {}), [visibleQuestions]);
  const answeredCount = visibleQuestions.filter((question) => answers[question.id]).length;
  const progress = visibleQuestions.length ? Math.round((answeredCount / visibleQuestions.length) * 100) : 0;

  function answerQuestion(id, value) {
    const next = { ...answers, [id]: value };
    const visibleIds = new Set(questions.filter((question) => questionIsVisible(question, next)).map((question) => question.id));
    setAnswers(Object.fromEntries(Object.entries(next).filter(([key]) => visibleIds.has(key))));
  }

  function beginAssessment(event) {
    event.preventDefault();
    if (!profile.name.trim() || !profile.postcode.trim() || !waitlist.email.trim() || !profile.dob) {
      setNotice('Please add your first name, date of birth, email address and postcode.');
      return;
    }
    if (!consent.report) {
      setNotice('Please confirm that ACT may use your answers to create your report.');
      return;
    }
    setNotice('');
    setStage('assessment');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function preparePriorities() {
    const missing = visibleQuestions.filter((question) => !answers[question.id]);
    if (missing.length) {
      setActiveSection(Math.max(0, sectionOrder.indexOf(missing[0].section)));
      setNotice(`Please answer the remaining ${missing.length} question${missing.length === 1 ? '' : 's'} before choosing your priorities.`);
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }
    try {
      setBusy(true);
      setNotice('Finding the concerns that matter most...');
      const response = await fetch(`${API}/api/concerns`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ answers }) });
      if (!response.ok) throw new Error(`Concern review failed: ${response.status}`);
      const data = await response.json();
      setConcerns(data.concerns || []);
      setSelectedPriorities([]);
      setStage('priorities');
      setNotice('');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch {
      setNotice('We could not prepare your priorities. Please check the local Python service and try again.');
    } finally { setBusy(false); }
  }

  async function submitAssessment() {
    const target = Math.min(3, concerns.length);
    if (selectedPriorities.length !== target) {
      setNotice(`Please choose ${target} priorit${target === 1 ? 'y' : 'ies'} before creating your plan.`);
      return;
    }
    try {
      setBusy(true);
      setNotice('Creating your personal wellness picture...');
      const response = await fetch(`${API}/api/assessments`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile: { ...profile, postcode: profile.postcode.toUpperCase() }, answers, selected_priorities: selectedPriorities, consent, waitlist, member_access: memberAccess.authenticated ? memberAccess : undefined }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || `Assessment failed: ${response.status}`);
      setDashboard(data);
      setHistory(data.history || []);
      setMemberAccess({ email: waitlist.email, access_code: data.member_access_code || memberAccess.access_code, authenticated: true });
      setStage('results');
      setNotice('');
      window.setTimeout(() => resultsRef.current?.focus(), 80);
    } catch (error) {
      setNotice(error.message || 'We could not create your report. Please check that the local Python service is running and try again.');
    } finally { setBusy(false); }
  }

  async function openProgress(event) {
    event?.preventDefault();
    if (!memberAccess.email.trim() || !memberAccess.access_code.trim()) {
      setNotice('Please enter the email address and ACT access code from your report email.');
      return;
    }
    try {
      setBusy(true); setNotice('Opening your private progress record...');
      const response = await fetch(`${API}/api/members/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(memberAccess) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'We could not open your progress record.');
      const { user_id, ...latestProfile } = data.latest_profile || {};
      setProfile((current) => ({ ...current, ...latestProfile }));
      setWaitlist((current) => ({ ...current, email: memberAccess.email }));
      setHistory(data.history || []);
      setMemberAccess((current) => ({ ...current, authenticated: true }));
      setStage('progress'); setNotice('');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
      setNotice(error.message || 'We could not open your progress record.');
    } finally { setBusy(false); }
  }

  function startRetake() {
    window.speechSynthesis?.cancel();
    setDashboard(null); setAnswers({}); setConcerns([]); setSelectedPriorities([]); setActiveSection(0);
    setConsent({ report: false, analytics: false }); setStage('welcome');
    setNotice('Welcome back. Check your details, confirm consent, then start your next wellness check.');
    window.setTimeout(() => document.getElementById('registration')?.scrollIntoView({ behavior: 'smooth' }), 80);
  }

  function restart() {
    window.speechSynthesis?.cancel();
    setDashboard(null); setAnswers({}); setConcerns([]); setSelectedPriorities([]); setActiveSection(0); setStage('welcome'); setNotice('');
  }

  return (
    <div className="site-shell">
      <Header stage={stage} progress={progress} answered={answeredCount} total={visibleQuestions.length} />
      {stage === 'welcome' && <Welcome profile={profile} setProfile={setProfile} waitlist={waitlist} setWaitlist={setWaitlist} consent={consent} setConsent={setConsent} notice={notice} onBegin={beginAssessment} memberAccess={memberAccess} setMemberAccess={setMemberAccess} onOpenProgress={openProgress} busy={busy} onViewProgress={() => setStage('progress')} history={history} />}
      {stage === 'assessment' && <Assessment grouped={grouped} answers={answers} onAnswer={answerQuestion} activeSection={activeSection} setActiveSection={setActiveSection} notice={notice} onSubmit={preparePriorities} busy={busy} />}
      {stage === 'priorities' && <PrioritySelection concerns={concerns} selected={selectedPriorities} setSelected={setSelectedPriorities} notice={notice} busy={busy} onBack={() => { setStage('assessment'); setActiveSection(sectionOrder.length - 1); setNotice(''); }} onSubmit={submitAssessment} />}
      {stage === 'progress' && <ProgressDashboard history={history} profile={profile} onRetake={startRetake} onClose={() => setStage(dashboard ? 'results' : 'welcome')} />}
      {stage === 'results' && dashboard && <Results dashboard={dashboard} onRestart={startRetake} onViewProgress={() => setStage('progress')} history={history} resultsRef={resultsRef} />}
      {dashboard && <Chat dashboard={dashboard} open={chatOpen} setOpen={setChatOpen} />}
      <Footer />
    </div>
  );
}

function Header({ stage, progress, answered, total }) {
  return <header className="header"><button className="brand" type="button" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}><span className="brand-mark">ACT</span><span><strong>Wellness Check</strong><small>Healthy Longevity</small></span></button><div className="header-status"><span><ShieldCheck size={18} /> Private wellness check</span>{stage === 'assessment' && <div className="header-progress" aria-label={`${answered} of ${total} questions answered`}><small>{answered} of {total} answered</small><i><b style={{ width: `${progress}%` }} /></i></div>}</div></header>;
}

function Welcome({ profile, setProfile, waitlist, setWaitlist, consent, setConsent, notice, onBegin, memberAccess, setMemberAccess, onOpenProgress, busy, onViewProgress, history }) {
  const update = (key) => (event) => setProfile({ ...profile, [key]: event.target.value });
  return <main>
    <section className="hero" id="top">
      <div className="hero-copy"><p className="eyebrow">ACT Assess + Wellness</p><h1>Know what matters.<br /><em>Live well, for longer.</em></h1><p className="lede">A friendly check-in that asks a little more only when it matters, then turns your answers into a clear picture of your wellbeing and practical next steps.</p><div className="hero-points"><span><CheckCircle2 /> Five-part wellness picture</span><span><CheckCircle2 /> Your three priorities</span><span><CheckCircle2 /> Local support near you</span></div></div>
      <div className="hero-visual" aria-hidden="true"><MiniRadar /><div><strong>Your whole-life view</strong><p>See strengths and opportunities together, not as isolated symptoms.</p></div></div>
    </section>
    <section className="steps-band" aria-label="How it works">{['Complete the check', 'Choose what matters most', 'Build your action plan'].map((step, index) => <div key={step}><b>0{index + 1}</b><span>{step}</span></div>)}</section>
    <ReturningAccess memberAccess={memberAccess} setMemberAccess={setMemberAccess} onSubmit={onOpenProgress} busy={busy} notice={notice} onViewProgress={onViewProgress} history={history} />
    <section className="registration" id="registration">
      <div className="registration-intro"><p className="eyebrow">Let’s begin</p><h2>Tell us a little about you</h2><p>Your age and home situation help us interpret your answers with more context. Your postcode is used to find suitable services and older-adult activities nearby.</p><div className="privacy-note"><ShieldCheck /><span>We only ask for details that help personalise your report. This is a wellness guide, not a diagnosis.</span></div></div>
      <form className="registration-form" onSubmit={onBegin}>
        <h3>Your essential details</h3>
        <div className="form-grid">
          <label>First name<input value={profile.name} onChange={update('name')} autoComplete="given-name" placeholder="For example, Jane" /></label>
          <label>Date of birth<input type="date" value={profile.dob} onChange={update('dob')} /></label>
        </div>
        <div className="form-divider"><span>Contact and location</span></div>
        <div className="form-grid">
          <label>Email address<input type="email" value={waitlist.email} onChange={(event) => setWaitlist({ ...waitlist, email: event.target.value })} autoComplete="email" placeholder="jane@example.com" /></label>
          <label>Phone number <small className="label-note">Optional</small><input type="tel" value={profile.phone} onChange={update('phone')} autoComplete="tel" placeholder="For example, 07123 456789" /></label>
          <label className="wide">Address <small className="label-note">Optional</small><input value={profile.address} onChange={update('address')} autoComplete="street-address" placeholder="House number and street" /></label>
          <label>UK postcode<input value={profile.postcode} onChange={update('postcode')} autoComplete="postal-code" placeholder="For example, SW6 1LY" /><small>Used to find relevant support near you.</small></label>
          <label>Country<select value={profile.country} onChange={update('country')} autoComplete="country-name"><option>United Kingdom</option><option>Ireland</option><option>Other</option></select></label>
        </div>
        <div className="form-divider"><span>About your life</span></div>
        <div className="form-grid profile-fields">
          <label>Gender<select value={profile.gender} onChange={update('gender')}><option value="">Choose one</option><option>Female</option><option>Male</option><option>Non-binary</option><option>Prefer not to say</option></select></label>
          <label>Marital status<select value={profile.marital_status} onChange={update('marital_status')}><option value="">Choose one</option><option>Single</option><option>Married</option><option>Partnered</option><option>Widowed</option><option>Divorced</option></select></label>
          <label>Who do you live with?<select value={profile.living_arrangement} onChange={update('living_arrangement')}><option value="">Choose one</option><option>Alone</option><option>With a partner</option><option>With extended family</option><option>Assisted living</option><option>Care home</option></select></label>
          <label>Does someone help care for you?<select value={profile.care_support} onChange={update('care_support')}><option value="">Choose one</option><option>No</option><option>Yes - partner</option><option>Yes - children</option><option>Yes - other family or friends</option><option>Yes - paid carer</option></select></label>
          <label>Employment status<select value={profile.employment_status} onChange={update('employment_status')}><option value="">Choose one</option><option>Retired</option><option>Employed - full time</option><option>Employed - part time</option><option>Self-employed</option><option>Volunteering</option><option>Not currently working</option></select></label>
          <label>Main career sector<select value={profile.employment_sector} onChange={update('employment_sector')}><option value="">Choose one</option><option>Healthcare</option><option>Education</option><option>Public sector</option><option>Retail</option><option>Manufacturing</option><option>Finance</option><option>Homemaker</option><option>Other</option><option>Not applicable</option></select></label>
        </div>
        <label className="check-row"><input type="checkbox" checked={waitlist.join} onChange={(event) => setWaitlist({ ...waitlist, join: event.target.checked })} /><span><strong>Keep me informed.</strong> Add me to the early list for ACT’s AI-powered Healthy Longevity support.</span></label>
        <label className="check-row"><input type="checkbox" checked={consent.report} onChange={(event) => setConsent({ ...consent, report: event.target.checked })} /><span>I agree that ACT may use my answers to create and email my personal wellness report.</span></label>
        <label className="check-row optional"><input type="checkbox" checked={consent.analytics} onChange={(event) => setConsent({ ...consent, analytics: event.target.checked })} /><span>ACT may use my anonymised answers to understand population wellbeing. This is optional.</span></label>
        {notice && <p className="notice" role="status">{notice}</p>}
        <button className="primary-button" type="submit">Start my wellness check <ArrowRight /></button><p className="time-note">About 8 minutes · Free</p>
      </form>
    </section>
  </main>;
}

function ReturningAccess({ memberAccess, setMemberAccess, onSubmit, busy, notice, onViewProgress, history }) {
  if (memberAccess.authenticated) return <section className="returning-access signed-in"><div><span className="returning-icon"><CheckCircle2 /></span><div><p className="eyebrow">Welcome back</p><h2>Your next check will join your progress timeline</h2><p>{history.length} previous assessment{history.length === 1 ? '' : 's'} available to compare.</p></div></div><button className="secondary-button" type="button" onClick={onViewProgress}><History /> View my progress</button></section>;
  return <section className="returning-access"><div className="returning-copy"><span className="returning-icon"><History /></span><div><p className="eyebrow">Completed ACT before?</p><h2>See how your wellness has changed</h2><p>Use the email address and private access code from your ACT report email.</p></div></div><form onSubmit={onSubmit}><label>Email address<input type="email" value={memberAccess.email} onChange={(event) => setMemberAccess({ ...memberAccess, email: event.target.value })} autoComplete="email" placeholder="jane@example.com" /></label><label>ACT access code<input value={memberAccess.access_code} onChange={(event) => setMemberAccess({ ...memberAccess, access_code: event.target.value.toUpperCase() })} autoComplete="one-time-code" placeholder="ACT-ABCD-2345" /></label><button className="secondary-button" type="submit" disabled={busy}><LockKeyhole /> {busy ? 'Opening...' : 'Open my progress'}</button>{notice && <p className="returning-notice" role="status">{notice}</p>}</form></section>;
}

function Assessment({ grouped, answers, onAnswer, activeSection, setActiveSection, notice, onSubmit, busy }) {
  const section = sectionOrder[activeSection]; const items = grouped[section] || [];
  const completed = items.filter((question) => answers[question.id]).length;
  const goNext = () => { if (activeSection < sectionOrder.length - 1) { setActiveSection(activeSection + 1); window.scrollTo({ top: 0, behavior: 'smooth' }); } else onSubmit(); };
  return <main className="assessment-page"><div className="score-preview-row">{sectionOrder.map((name, index) => <button key={name} className={index === activeSection ? 'score-preview active' : 'score-preview'} onClick={() => setActiveSection(index)} type="button"><span>0{index + 1}</span><strong>{name}</strong><small>{(grouped[name] || []).filter((q) => answers[q.id]).length}/{(grouped[name] || []).length}</small></button>)}</div><nav className="section-tabs" aria-label="Assessment sections">{sectionOrder.map((name, index) => <button type="button" className={index === activeSection ? 'active' : ''} onClick={() => setActiveSection(index)} key={name}>{name}</button>)}</nav><section className="assessment-panel"><header className="section-heading"><div><p className="eyebrow">Section 0{activeSection + 1} · {sectionCopy[section][0]}</p><h1>{section}</h1><p>{sectionCopy[section][1]}. Choose the answer that best reflects life at the moment.</p></div><div className="section-count"><strong>{activeSection + 1}</strong><span>/ 3</span></div></header>{!items.length ? <p className="notice">Questions are still loading. Please wait a moment.</p> : <div className="question-list">{items.map((question, index) => <Question key={question.id} index={index} question={question} value={answers[question.id]} onChange={(value) => onAnswer(question.id, value)} />)}</div>}{notice && <p className="notice assessment-notice" role="status">{notice}</p>}<div className="assessment-actions">{activeSection > 0 ? <button className="secondary-button" type="button" onClick={() => setActiveSection(activeSection - 1)}><ArrowLeft /> Back</button> : <span />}<div><small>{completed} of {items.length} answered in this section</small><button className="primary-button" type="button" onClick={goNext} disabled={busy}>{busy ? 'Reviewing your answers...' : activeSection === sectionOrder.length - 1 ? 'Choose my priorities' : 'Continue'} <ArrowRight /></button></div></div></section></main>;
}

function Question({ question, value, onChange, index }) {
  const ability = question.type === 'ability';
  const hint = ability ? 'Choose the level of help that feels most accurate.' : question.type === 'positive_yesno' ? 'Think about a usual week.' : question.options?.length > 2 ? 'Choose the answer that feels most accurate.' : 'Please answer yes or no.';
  return <div className={question.follow_up ? 'question-row follow-up' : 'question-row'}><div className="question-copy"><span>{String(index + 1).padStart(2, '0')}</span><div>{question.follow_up && <small className="follow-up-label">A little more about {question.follow_up}</small>}<strong>{question.text}</strong><small>{hint}</small></div></div><div className={ability ? 'choice-grid ability' : 'choice-grid'}>{(question.options || []).map((option) => <button type="button" key={option} className={value === option ? 'choice active' : 'choice'} onClick={() => onChange(option)} aria-pressed={value === option}>{value === option && <Check size={18} />}{option}</button>)}</div></div>;
}

function PrioritySelection({ concerns, selected, setSelected, notice, busy, onBack, onSubmit }) {
  const target = Math.min(3, concerns.length);
  function toggle(id) {
    if (selected.includes(id)) setSelected(selected.filter((item) => item !== id));
    else if (selected.length < target) setSelected([...selected, id]);
  }
  return <main className="priority-page"><section className="priority-panel"><header><p className="eyebrow">One final step</p><h1>What matters most to you?</h1><p>{target ? `We found ${concerns.length} area${concerns.length === 1 ? '' : 's'} where support may help. Choose ${target === 3 ? 'three' : target} to put at the heart of your plan.` : 'No immediate concerns were identified. We will help you maintain what is working well.'}</p>{concerns.some((item) => item.clinical) && <p className="priority-guidance"><HeartPulse /> Important health flags will always appear clearly in your report, whether or not you select them here.</p>}</header>{concerns.length > 0 && <div className="priority-options">{concerns.map((item) => { const active = selected.includes(item.id); const disabled = !active && selected.length >= target; return <button type="button" className={active ? 'priority-option active' : 'priority-option'} onClick={() => toggle(item.id)} disabled={disabled} aria-pressed={active} key={item.id}><span>{active && <Check />}</span><div>{item.clinical && <small>Important health flag</small>}<strong>{item.title}</strong><p>{item.detail}</p></div></button>; })}</div>}{notice && <p className="notice" role="status">{notice}</p>}<div className="priority-actions"><button className="secondary-button" type="button" onClick={onBack}><ArrowLeft /> Back to answers</button><div><small>{selected.length} of {target} selected</small><button className="primary-button" type="button" onClick={onSubmit} disabled={busy || selected.length !== target}>{busy ? 'Creating your plan...' : 'Create my wellness plan'} <ArrowRight /></button></div></div></section></main>;
}

function Results({ dashboard, onRestart, onViewProgress, history, resultsRef }) {
  const [speaking, setSpeaking] = useState(false);
  const movementVideos = dashboard.videos.filter((video) => video.category !== 'Food');
  const foodVideos = dashboard.videos.filter((video) => video.category === 'Food');
  const sortedScores = [...scoreMeta].sort((a, b) => dashboard.scores[a[0]] - dashboard.scores[b[0]]);
  const chosen = dashboard.selected_priorities || [];
  function speak() { if (!('speechSynthesis' in window)) return; if (speaking) { window.speechSynthesis.cancel(); setSpeaking(false); return; } const recommendations = dashboard.recommendations.map((item) => `${item.title}. ${item.body}`).join(' '); const utterance = new SpeechSynthesisUtterance(`Hello ${dashboard.profile.name}. Here is your wellness summary. ${dashboard.persona} ${recommendations}`); utterance.rate = 0.86; utterance.pitch = 1.02; utterance.onend = () => setSpeaking(false); utterance.onerror = () => setSpeaking(false); setSpeaking(true); window.speechSynthesis.speak(utterance); }
  return <main className="results-page" ref={resultsRef} tabIndex="-1">
    <section className="results-heading"><div><p className="eyebrow">Your wellness picture</p><h1>{dashboard.profile.name}’s personalised plan</h1><p>Higher scores mean fewer needs were reported. Start with one achievable next step.</p></div><div className="results-actions"><button className="secondary-button" type="button" onClick={onViewProgress}><History /> View progress</button><button className="secondary-button" type="button" onClick={onRestart}>Take another check</button></div></section>
    <section className="result-score-row">{scoreMeta.map(([key, label, Icon, colour]) => <div className={`result-score ${colour}`} key={key}><Icon /><span>{label}</span><strong>{dashboard.scores[key]}</strong><small>/100</small></div>)}</section>
    <section className="results-overview"><article className="radar-card"><Radar scores={dashboard.scores} /><p><i /> Your current wellness scores</p></article><article className="summary-card"><p className="eyebrow">Your personal summary</p><h2>{summaryHeadline(dashboard.scores)}</h2><p>{dashboard.persona}</p><div className="priority-list">{chosen.length ? chosen.map((item, index) => <div key={item.id}><span>{index + 1}</span><p><strong>{item.title}</strong><small>Your choice</small></p></div>) : sortedScores.slice(0, 3).map(([key, label], index) => <div key={key}><span>{index + 1}</span><p><strong>{label}</strong><small>{dashboard.scores[key]} / 100</small></p></div>)}</div><button className="listen-button" type="button" onClick={speak}>{speaking ? <Pause /> : <Volume2 />} {speaking ? 'Stop reading' : 'Listen to my plan'}</button></article></section>
    <DeliveryStatus delivery={dashboard.delivery} />
    {dashboard.member_access_code && <MemberAccessCode code={dashboard.member_access_code} emailed={dashboard.delivery?.email?.sent} />}
    {history.length > 1 && <ProgressPreview history={history} onViewProgress={onViewProgress} />}
    <ClinicalRiskSummary risks={dashboard.clinical_risks} />
    <ContentHeading eyebrow="Your next best steps" title="Small actions, thoughtfully chosen" copy="Clinical needs first, followed by your choices and practical support." />
    <section className="recommendation-grid">{dashboard.recommendations.map((item, index) => <Recommendation item={item} index={index} key={item.title} />)}</section>
    <ContentHeading eyebrow="Understand your results" title="Your five areas in more detail" copy="What each score may mean and where support could help." />
    <section className="category-grid">{scoreMeta.map(([key, label, Icon, colour]) => <CategoryCard key={key} score={dashboard.scores[key]} label={label} Icon={Icon} colour={colour} />)}</section>
    <section className="report-columns"><ReportSection icon={ClipboardList} eyebrow="Your choices" title="Your three priorities" items={chosen} emptyText="No support priorities were selected." /><ReportSection icon={ShieldCheck} eyebrow="Prevention" title="Prevention opportunities" items={dashboard.prevention_opportunities} emptyText="Your core prevention routines appear broadly on track." /><ReportSection icon={HeartPulse} eyebrow="For your doctor" title="Clinical points to discuss" items={dashboard.clinical_risks} emptyText="No major clinical discussion points were identified." /></section>
    <ResourceGroups resources={dashboard.resources} postcode={dashboard.profile.postcode} />
    <ContentHeading eyebrow="Do it at home" title="Gentle movement videos" copy="Choose a level that feels safe today." />
    <section className="media-grid">{movementVideos.map((item) => <VideoCard item={item} key={item.title} />)}</section>
    {foodVideos.length > 0 && <><ContentHeading eyebrow="Nourish your day" title="Simple recipe ideas" copy="Healthy, low-effort meals chosen for your results." /><section className="media-grid">{foodVideos.map((item) => <VideoCard item={item} key={item.title} />)}</section></>}
    <section className="report-ready"><div><span className="report-icon"><FileText /></span><div><p className="eyebrow">Take your plan with you</p><h2>Your PDF report is ready</h2><p>{dashboard.delivery?.email?.sent ? `We emailed a copy to ${dashboard.delivery.email.to}.` : 'Your PDF has been prepared. Add valid email settings to send it automatically.'}</p></div></div><div className="report-sheet" aria-hidden="true"><b>ACT</b><span>My wellness<br />report</span></div></section>
  </main>;
}

function MemberAccessCode({ code, emailed }) {
  const [copied, setCopied] = useState(false);
  async function copyCode() { await navigator.clipboard?.writeText(code); setCopied(true); window.setTimeout(() => setCopied(false), 1800); }
  return <section className="member-code"><span><LockKeyhole /></span><div><p className="eyebrow">Your private progress access</p><h2>Keep this code for your next check</h2><p>{emailed ? 'It is also included in your report email.' : 'Keep it somewhere safe with the email address you used today.'}</p></div><button type="button" onClick={copyCode}><b>{code}</b><small>{copied ? 'Copied' : 'Copy code'}</small><Copy /></button></section>;
}

function ProgressPreview({ history, onViewProgress }) {
  const previous = history.at(-2); const latest = history.at(-1);
  const improved = scoreMeta.filter(([key]) => latest.scores[key] > previous.scores[key]).length;
  return <section className="progress-preview"><div><p className="eyebrow">Since your last check</p><h2>{improved ? `${improved} of your five areas moved upward` : 'Your latest scores are ready to compare'}</h2><p>Changes are a prompt for reflection, not a diagnosis. Small movements may simply reflect how life felt on the day.</p></div><button className="primary-button" type="button" onClick={onViewProgress}>See all trends <ArrowRight /></button></section>;
}

function ProgressDashboard({ history, profile, onRetake, onClose }) {
  const latest = history.at(-1); const previous = history.at(-2);
  return <main className="progress-page">
    <section className="progress-heading"><div><p className="eyebrow">My ACT progress</p><h1>{profile.name ? `${profile.name}’s wellness over time` : 'Your wellness over time'}</h1><p>Compare each check-in without losing sight of the whole picture. Higher scores mean fewer needs were reported.</p></div><div><button className="secondary-button" type="button" onClick={onClose}><ArrowLeft /> Back</button><button className="primary-button" type="button" onClick={onRetake}>Take another check <ArrowRight /></button></div></section>
    {!latest ? <section className="empty-progress"><History /><h2>No assessments are linked yet</h2><p>Complete a wellness check to begin your timeline.</p><button className="primary-button" type="button" onClick={onRetake}>Start my first check</button></section> : <>
      <section className="progress-summary"><div><CalendarDays /><span><small>Check-ins recorded</small><strong>{history.length}</strong></span></div><div><History /><span><small>First check</small><strong>{formatDate(history[0].created_at)}</strong></span></div><div><CheckCircle2 /><span><small>Latest check</small><strong>{formatDate(latest.created_at)}</strong></span></div></section>
      <section className="trend-panel"><header><div><p className="eyebrow">Five-area trend</p><h2>Your scores, check by check</h2></div><p>Look for the overall direction. One change alone does not confirm that health has improved or worsened.</p></header><TrendChart history={history} /><div className="trend-legend">{scoreMeta.map(([key, label, Icon, colour]) => <span className={colour} key={key}><i /><Icon /> {label}</span>)}</div></section>
      <section className="change-grid">{scoreMeta.map(([key, label, Icon, colour]) => <ChangeCard key={key} label={label} Icon={Icon} colour={colour} latest={latest.scores[key]} previous={previous?.scores[key]} />)}</section>
      <ContentHeading eyebrow="Assessment history" title="Every check-in, kept separately" copy="Open dates and scores side by side. Your latest assessment is shown first." />
      <section className="history-list">{[...history].reverse().map((item, index) => <AssessmentHistoryItem item={item} latest={index === 0} key={item.assessment_id} />)}</section>
    </>}
  </main>;
}

function ChangeCard({ label, Icon, colour, latest, previous }) {
  const delta = previous == null ? null : latest - previous;
  const Direction = delta > 0 ? TrendingUp : delta < 0 ? TrendingDown : Minus;
  return <article className={`change-card ${colour}`}><div><Icon /><span>{label}</span></div><strong>{latest}<small>/100</small></strong><p className={delta > 0 ? 'up' : delta < 0 ? 'down' : ''}><Direction /> {delta == null ? 'First result' : delta > 0 ? `${delta} points higher` : delta < 0 ? `${Math.abs(delta)} points lower` : 'No score change'}</p></article>;
}

function AssessmentHistoryItem({ item, latest }) {
  const [open, setOpen] = useState(false);
  return <article className={latest ? 'history-item latest' : 'history-item'}><button type="button" onClick={() => setOpen(!open)} aria-expanded={open}><span><CalendarDays /><b>{formatDate(item.created_at)}</b>{latest && <small>Latest</small>}</span><span>{scoreMeta.map(([key, label]) => <i key={key} title={label}><b>{item.scores[key]}</b><small>{label}</small></i>)}</span><ArrowRight className={open ? 'open' : ''} /></button>{open && <div className="history-detail"><div><strong>Summary from this check</strong><p>{item.summary}</p></div><div><strong>Priorities chosen</strong><p>{item.selected_priorities?.length ? item.selected_priorities.map((priority) => priority.title).join(', ') : 'No priorities selected.'}</p></div></div>}</article>;
}

function TrendChart({ history }) {
  const width = 900, height = 330, left = 54, right = 24, top = 28, bottom = 55;
  const plotWidth = width - left - right, plotHeight = height - top - bottom;
  const x = (index) => history.length === 1 ? left + plotWidth / 2 : left + index * plotWidth / (history.length - 1);
  const y = (value) => top + (100 - value) * plotHeight / 100;
  const colours = { staying_healthy: '#d96f55', independence: '#397c9b', wellbeing: '#c28a25', social_resources: '#59865a', clinical_risk: '#76518b' };
  return <div className="trend-chart-scroll"><svg className="trend-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Line chart showing the five wellness scores across assessments">{[0, 25, 50, 75, 100].map((value) => <g key={value}><line x1={left} x2={width - right} y1={y(value)} y2={y(value)} /><text x={left - 12} y={y(value) + 5} textAnchor="end">{value}</text></g>)}{scoreMeta.map(([key, label]) => { const points = history.map((item, index) => `${x(index)},${y(item.scores[key])}`).join(' '); return <g key={key}><polyline points={points} style={{ stroke: colours[key] }} />{history.map((item, index) => <circle key={item.assessment_id} cx={x(index)} cy={y(item.scores[key])} r="6" style={{ fill: colours[key] }}><title>{`${label}: ${item.scores[key]} on ${formatDate(item.created_at)}`}</title></circle>)}</g>; })}{history.map((item, index) => <text className="trend-date" x={x(index)} y={height - 18} textAnchor="middle" key={item.assessment_id}>{shortDate(item.created_at)}</text>)}</svg></div>;
}

function formatDate(value) { return value ? new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(value)) : 'Date unavailable'; }
function shortDate(value) { return value ? new Intl.DateTimeFormat('en-GB', { month: 'short', year: '2-digit' }).format(new Date(value)) : ''; }

function summaryHeadline(scores) { const values = scoreMeta.map(([key]) => scores[key]); const average = values.reduce((total, score) => total + score, 0) / values.length; if (average >= 85) return 'Your overall wellness picture is strong.'; if (average >= 65) return 'You are doing well, with a few useful opportunities.'; if (average >= 40) return 'Some coordinated support could make daily life easier.'; return 'Timely support in a few areas could make a meaningful difference.'; }
function ContentHeading({ eyebrow, title, copy }) { return <header className="content-heading"><div><p className="eyebrow">{eyebrow}</p><h2>{title}</h2></div><p>{copy}</p></header>; }
function ClinicalRiskSummary({ risks = [] }) { const significant = risks.filter((item) => item.significant); if (!significant.length) return null; return <section className="clinical-alert"><header><span><HeartPulse /></span><div><p className="eyebrow">Please address these first</p><h2>Important health points</h2><p>These findings are not a diagnosis, but they deserve timely professional advice.</p></div></header><div>{significant.map((item) => <article key={item.title}><strong>{item.title}</strong><p>{item.body}</p></article>)}</div></section>; }
function Recommendation({ item, index }) { return <article className={item.type === 'clinical' ? 'recommendation-card clinical' : 'recommendation-card'}><div><ResourceIcon type={item.type} /><small>{item.type === 'clinical' ? 'Discuss first' : item.type || 'Your plan'}</small></div><h3>{item.title}</h3><p>{item.body}</p>{index === 0 && <span className="first-step">Suggested first step</span>}</article>; }
function CategoryCard({ score, label, Icon, colour }) { const band = score >= 85 ? ['Strong', 'Keep doing what is working.'] : score >= 65 ? ['Generally well', 'A small amount of support may help.'] : score >= 40 ? ['Some support may help', 'This is a useful area to focus on.'] : ['Priority for support', 'Consider practical or professional follow-up.']; return <article className={`category-card ${colour}`}><div className="category-score"><Icon /><strong>{score}</strong><small>/100</small></div><h3>{label}</h3><b>{band[0]}</b><p>{band[1]}</p></article>; }
function ReportSection({ icon: Icon, eyebrow, title, items = [], emptyText }) { const rows = items.length ? items : [{ title: 'All steady', body: emptyText }]; return <article className="report-section"><header><span><Icon /></span><div><p className="eyebrow">{eyebrow}</p><h3>{title}</h3></div></header>{rows.map((item) => <div className="report-item" key={item.title}><strong>{item.title}</strong><p>{item.body || item.detail}</p></div>)}</article>; }
function ResourceGroups({ resources = [], postcode }) {
  const groups = [
    ['Community near you', `Activities and groups to help you stay active and connected around ${postcode}.`],
    ['Practical support', 'Services that can make shopping, meals and help at home easier.'],
    ['Trusted health guidance', 'Clear information from recognised public-health organisations.'],
  ];
  return groups.map(([category, copy]) => {
    const items = resources.filter((item) => item.category === category);
    if (!items.length) return null;
    return <section className="resource-group" key={category}><ContentHeading eyebrow={category === 'Community near you' ? `Support near ${postcode}` : 'Chosen for your answers'} title={category} copy={copy} /><div className="service-grid">{items.map((item) => <ResourceCard item={item} postcode={postcode} key={item.name} />)}</div></section>;
  });
}
function ResourceCard({ item, postcode }) {
  const query = encodeURIComponent(`${item.search_query || item.name} ${postcode}`);
  const healthGuidance = item.category === 'Trusted health guidance';
  return <article className="service-card"><ResourceIcon type={item.kind} icon={item.icon} /><div><small className="resource-category">{item.category}</small><h3>{item.name}</h3><p>{item.why}</p><div><a href={item.url} target="_blank" rel="noreferrer">{healthGuidance ? 'Read trusted guidance' : 'Visit website'} <ArrowRight /></a>{item.local_search && <a href={`https://www.google.com/maps/search/?api=1&query=${query}`} target="_blank" rel="noreferrer"><MapPin /> Search near me</a>}</div></div></article>;
}
function VideoCard({ item }) { return <a className="video-card" href={item.url} target="_blank" rel="noreferrer"><div className="video-image"><img src={item.thumbnail} alt="" /><span><Play /></span></div><div><small>{item.category === 'Food' ? 'Easy recipe' : 'Gentle movement'}</small><h3>{item.title}</h3><p>{item.why}</p><b>Watch on YouTube <ArrowRight /></b></div></a>; }
function DeliveryStatus({ delivery }) { if (!delivery) return null; const sent = delivery.email?.sent; return <div className={sent ? 'delivery-status sent' : 'delivery-status pending'}><FileText /><div><strong>{sent ? 'Report emailed' : 'PDF prepared'}</strong><span>{sent ? `A copy has been sent to ${delivery.email.to}.` : delivery.email?.reason || 'Email delivery is not configured yet.'}</span></div></div>; }

function Chat({ dashboard, open, setOpen }) {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([{ role: 'bot', text: `Hello ${dashboard.profile.name}. I can help explain your scores or turn a suggestion into a simple first step.` }]);
  const [busy, setBusy] = useState(false);
  const [consent, setConsent] = useState(false);
  const [available, setAvailable] = useState(null);
  const logRef = useRef(null);
  useEffect(() => { if (open) fetch(`${API}/api/chat/status`).then((response) => response.json()).then((data) => setAvailable(data.available)).catch(() => setAvailable(false)); }, [open]);
  useEffect(() => { logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' }); }, [messages, busy, open]);
  async function send(event, prompt) {
    event?.preventDefault();
    const text = (prompt || message).trim();
    if (!text || busy || !consent || !available) return;
    setMessages((current) => [...current, { role: 'user', text }]);
    setMessage(''); setBusy(true);
    try {
      const response = await fetch(`${API}/api/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: dashboard.user_id, chat_token: dashboard.chat_token, message: text, ai_consent: true }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Ask ACT could not answer right now.');
      setMessages((current) => [...current, { role: 'bot', text: data.answer }]);
    } catch (error) {
      setMessages((current) => [...current, { role: 'bot', text: error.message || 'I cannot reach the local service right now. Please try again in a moment.' }]);
    } finally { setBusy(false); }
  }
  const canAsk = consent && available && !busy;
  return <><button className="chat-button" type="button" onClick={() => setOpen(!open)} aria-expanded={open}><Sparkles /> Ask ACT AI</button>{open && <aside className="chat-panel" aria-label="Ask ACT AI"><header><div><span><Sparkles /></span><div><strong>Ask ACT AI</strong><small>About your wellness plan</small></div></div><button type="button" onClick={() => setOpen(false)} aria-label="Close chat"><X /></button></header><div className="chat-log" ref={logRef} role="log" aria-live="polite">{messages.map((item, index) => <p className={item.role} key={`${item.role}-${index}`}>{item.text}</p>)}{busy && <p className="bot">Thinking about your question...</p>}</div>{available === false && <p className="chat-status" role="status">AI is not connected yet. The app owner needs to add an OpenAI API key.</p>}<label className="chat-consent"><input type="checkbox" checked={consent} onChange={(event) => setConsent(event.target.checked)} /><span>I agree to send my assessment answers and questions to OpenAI for a reply. ACT will save this conversation.</span></label><div className="quick-prompts">{['Why was this recommended?', 'Explain my Clinical Risk score', 'Help me take the first step'].map((prompt) => <button type="button" onClick={() => send(null, prompt)} disabled={!canAsk} key={prompt}>{prompt}</button>)}</div><form onSubmit={send}><input value={message} onChange={(event) => setMessage(event.target.value)} maxLength={600} placeholder="Ask about your plan" aria-label="Your question" disabled={!canAsk} /><button type="submit" aria-label="Send" disabled={!canAsk || !message.trim()}><Send /></button></form><p className="chat-disclaimer">Not for emergencies or diagnosis. In the UK, call 999 for an emergency or NHS 111 for urgent help.</p></aside>}</>;
}

function ResourceIcon({ type, icon }) { const key = icon || type; const Icon = { clinical: HeartPulse, movement: Activity, walking: Activity, sleep: Moon, nutrition: Salad, local: MapPin, social: Users, users: Users, learning: BookOpen, book: BookOpen, prevention: ShieldCheck, maintenance: HeartPulse, service: ShoppingBasket, shopping: ShoppingBasket, meal: Utensils, meal_delivery: Utensils, care: Home, home: Home, health_guidance: HeartPulse, heart: HeartPulse, finance: ShieldCheck }[key] || Sparkles; return <span className="card-icon"><Icon /></span>; }
function Radar({ scores }) { const size = 500, center = 250, radius = 142, labelRadius = 205; const polygon = (scale) => scoreMeta.map((_, index) => { const angle = -Math.PI / 2 + (Math.PI * 2 * index) / scoreMeta.length; return `${center + Math.cos(angle) * radius * scale},${center + Math.sin(angle) * radius * scale}`; }).join(' '); const valuePoints = scoreMeta.map(([key], index) => { const angle = -Math.PI / 2 + (Math.PI * 2 * index) / scoreMeta.length; const value = scores[key] / 100; return `${center + Math.cos(angle) * radius * value},${center + Math.sin(angle) * radius * value}`; }).join(' '); return <svg className="radar" viewBox={`0 0 ${size} ${size}`} role="img" aria-label="Five dimension Healthy Longevity profile">{[.25, .5, .75, 1].map((scale) => <polygon className="radar-grid" points={polygon(scale)} key={scale} />)}{scoreMeta.map((_, index) => { const angle = -Math.PI / 2 + (Math.PI * 2 * index) / scoreMeta.length; return <line className="radar-axis" key={index} x1={center} y1={center} x2={center + Math.cos(angle) * radius} y2={center + Math.sin(angle) * radius} />; })}<polygon className="radar-shape" points={valuePoints} />{scoreMeta.map(([key, label], index) => { const angle = -Math.PI / 2 + (Math.PI * 2 * index) / scoreMeta.length; const x = center + Math.cos(angle) * labelRadius; const y = center + Math.sin(angle) * labelRadius; const words = label.split(' '); return <text className="radar-label" textAnchor="middle" key={key} x={x} y={y}>{words.map((word, wordIndex) => <tspan x={x} dy={wordIndex ? 17 : 0} key={word}>{word}</tspan>)}</text>; })}</svg>; }
function MiniRadar() { return <svg viewBox="0 0 240 210"><polygon points="120,18 218,88 182,194 58,194 22,88" className="mini-grid" /><polygon points="120,50 186,96 162,166 72,174 50,96" className="mini-shape" /><circle cx="120" cy="50" r="5" /><circle cx="186" cy="96" r="5" /><circle cx="162" cy="166" r="5" /><circle cx="72" cy="174" r="5" /><circle cx="50" cy="96" r="5" /></svg>; }
function Footer() { return <footer><div><span className="brand-mark">ACT</span><strong>Ageing Care Technology</strong></div><p>This wellness check supports structured assessment. It does not diagnose conditions or replace clinical judgement.</p></footer>; }

createRoot(document.getElementById('root')).render(<App />);
