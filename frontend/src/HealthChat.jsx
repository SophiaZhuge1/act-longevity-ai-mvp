import React, { useEffect, useRef, useState } from 'react';
import { HeartPulse, Send, ShieldCheck, Sparkles, X } from 'lucide-react';
import { demoReply } from './demo-chat.js';

export default function HealthChat({ dashboard, answers, open, setOpen }) {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  const log = useRef(null);
  useEffect(() => { setMessages([]); setMessage(''); }, [dashboard.user_id]);
  useEffect(() => { log.current?.scrollTo({ top: log.current.scrollHeight, behavior: 'smooth' }); }, [messages, open]);
  function send(event, suggestion) {
    event?.preventDefault();
    const question = (suggestion || message).trim();
    if (!question || question.length > 600) return;
    const answer = demoReply(question, dashboard, answers, messages);
    setMessages(current => [...current, { role: 'user', text: question }, { role: 'assistant', ...answer }]);
    setMessage('');
  }
  const title = dashboard.recommendations?.[0]?.title;
  const prompts = [title ? `Why “${title}”?` : 'Why was this recommended?', 'Explain my scores', 'Explain my Clinical Risk score', 'What are my priorities?', 'Help me plan my week'];
  return <><button className="chat-button" type="button" onClick={() => setOpen(!open)} aria-expanded={open} aria-controls="health-chat"><Sparkles /> Ask ACT · Demo</button>{open && <aside id="health-chat" className="chat-panel health-chat" aria-label="Ask ACT demo assistant"><header><div><span><Sparkles /></span><div><strong>Ask ACT <b className="demo-badge">DEMO</b></strong><small>Your assessment, explained</small></div></div><button type="button" onClick={() => setOpen(false)} aria-label="Close chat"><X /></button></header>
    <div className="chat-context"><ShieldCheck size={18}/><p>Prepared replies tailored to your assessment.<small>Runs locally in your browser. No AI service, API calls or chat storage.</small></p></div>
    <div className="chat-log" ref={log} role="log" aria-live="polite"><div className="chat-intro"><HeartPulse size={27}/><h3>Let’s make your plan clearer.</h3><p>Ask about your scores, why a recommendation appeared, or a practical next step. This demo uses prepared responses, not a live AI model.</p></div>
      {messages.map((item, index) => <div className={`chat-message ${item.role === 'assistant' ? 'bot' : 'user'}`} key={index}><small>{item.role === 'assistant' ? 'Ask ACT · Prepared reply' : 'You'}</small><p>{item.text}</p></div>)}
    </div>
    <div className="quick-prompts">{prompts.map(prompt => <button key={prompt} type="button" onClick={() => send(null, prompt)}>{prompt}</button>)}</div>
    <form onSubmit={send}><input value={message} onChange={e => setMessage(e.target.value)} maxLength={600} aria-label="Your health question" placeholder="Ask about your health plan…"/><button type="submit" aria-label="Send health question" disabled={!message.trim()}><Send size={20}/></button></form>
    <div className="chat-bottom"><small>Demo wellness guidance, not diagnosis or treatment. For an emergency in the UK, call 999.</small><button className="chat-clear" onClick={() => { setMessages([]); setMessage(''); }} type="button">Clear chat</button></div>
  </aside>}</>;
}
