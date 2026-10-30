export const scoreLabels = { staying_healthy: 'Staying Healthy', independence: 'Independence', wellbeing: 'Wellbeing', social_resources: 'Social Resources', clinical_risk: 'Clinical Risk' };
const topics = {
  movement: /\b(exercise|movement|walk|walking|balance|fall|falls|active|activity|strength|fitness)\b/,
  nutrition: /\b(diet|nutrition|food|eat|eating|meal|meals|protein|weight|supplement|vitamin)\b/,
  sleep: /\b(sleep|sleeping|insomnia|rest|tired)\b/,
  social: /\b(lonely|loneliness|social|friends|friendship|community|connection|connected)\b/,
  independence: /\b(independen\w*|shopping|dressing|bathing|toilet|care|carer|home)\b/,
  blood_pressure: /\b(blood pressure|hypertension|bp)\b/,
  mood: /\b(mood|depress\w*|sad|anxious|anxiety|wellbeing)\b/,
  cognition: /\b(memory|forget\w*|confus\w*|thinking)\b/,
};
function findRecommendation(dashboard, topic) {
  const items = dashboard.recommendations || [];
  return items.find(item => topics[topic]?.test(`${item.title} ${item.body} ${item.type}`.toLowerCase())) || null;
}
const needs = {
  movement: [['falls_3_months', 'Yes', 'you reported a recent fall'], ['regular_exercise', 'No', 'you said you do not exercise regularly']],
  nutrition: [['diet_concern', 'Yes', 'you reported concerns about your diet'], ['lost_3kg', 'Yes', 'you reported unintentional weight loss']],
  sleep: [['sleep_trouble', 'Yes', 'you reported trouble sleeping']],
  social: [['lonely', 'Yes', 'you said you often feel lonely'], ['participation_ok', 'No', 'you said it is difficult to pursue activities that matter to you']],
  independence: [['shopping', 'No', 'you reported difficulty shopping independently'], ['bathing', 'No', 'you reported needing help with bathing'], ['dressing', 'No', 'you reported needing help dressing']],
  blood_pressure: [['bp_checked', 'No', 'you said your blood pressure has not been checked in the last year']],
  mood: [['down_depressed', 'Yes', 'you reported feeling down or hopeless'], ['little_interest', 'Yes', 'you reported less interest or pleasure in activities']],
  cognition: [['forgetting', 'Yes', 'you reported forgetting things more than usual'], ['confused_day_place', 'Yes', 'you reported sometimes feeling confused']],
};
function facts(answers, topic) { return (needs[topic] || []).filter(([id, value]) => answers[id] === value).map(([, , reason]) => reason); }
function firstStep(dashboard, topic) {
  const rec = findRecommendation(dashboard, topic) || dashboard.recommendations?.[0];
  return rec ? `A useful starting point from your plan is “${rec.title}”. ${rec.body || ''}` : 'Choose one concern that matters to you and discuss a manageable next step with a suitable health professional.';
}
function inferTopic(question, history, dashboard) {
  const match = Object.entries(topics).find(([, pattern]) => pattern.test(question));
  if (match) return match[0];
  if (/\b(that|this|it|more|start|first|begin|today|step|plan|why|recommended|recommendation)\b/.test(question)) {
    const previous = [...history].reverse().find(item => item.topic && item.topic !== 'overview');
    if (previous) return previous.topic;
    const first = `${dashboard.recommendations?.[0]?.title || ''} ${dashboard.recommendations?.[0]?.body || ''}`.toLowerCase();
    return Object.entries(topics).find(([, pattern]) => pattern.test(first))?.[0] || 'overview';
  }
  return 'overview';
}
export function demoReply(question, dashboard, answers = {}, history = []) {
  const q = question.toLowerCase().trim();
  const topic = inferTopic(q, history, dashboard);
  const respond = text => ({ text, topic });
  if (/\b(chest pain|cannot breathe|can't breathe|severe breathlessness|stroke|unconscious|overdose|suicid\w*|kill myself|hurt myself)\b/.test(q)) return respond('This demo cannot assess urgent symptoms or keep you safe in a crisis. If this describes what is happening now, or you may act on thoughts of harming yourself, call 999 or go to A&E. Do not wait for a chat reply.');
  if (/\b(diagnos\w*|do i have|am i ill|life expectancy|how long will i live|biological age)\b/.test(q)) return respond('Your ACT results are based on answers to a wellness questionnaire. They cannot diagnose a condition, estimate life expectancy or measure biological age. A clinician would need your symptoms, medical history and any appropriate tests. I can explain which of your reported answers led to a recommendation.');
  if (/\b(medic\w*|tablet\w*|dose|dosage|prescri\w*|stop taking|start taking|vitamin|supplement)\b/.test(q)) return respond('I cannot choose a medicine or supplement, suggest a dose, or advise changing treatment. Your assessment does not include a verified medication list, allergies or blood tests. Ask a pharmacist or clinician to check suitability. I can explain the nutrition recommendations already in your plan.');
  const scoreKey = /clinical\s*risk/.test(q) ? 'clinical_risk' : /staying healthy/.test(q) ? 'staying_healthy' : /social resources/.test(q) ? 'social_resources' : /independence.*score|score.*independence/.test(q) ? 'independence' : /wellbeing.*score|score.*wellbeing/.test(q) ? 'wellbeing' : null;
  if (scoreKey) {
    const score = dashboard.scores?.[scoreKey];
    const intro = Number.isFinite(score) ? `Your ${scoreLabels[scoreKey]} score is ${score}/100. ` : `There is no ${scoreLabels[scoreKey]} score in the current assessment. `;
    const flagged = (dashboard.clinical_risks || []).slice(0, 2).map(x => x.title);
    return respond(intro + 'Higher scores mean fewer concerns were reported; a lower score suggests more areas to review. This is not a diagnosis or a percentage chance of illness.' + (scoreKey === 'clinical_risk' && flagged.length ? ` Your plan flags: ${flagged.join('; ')}. Discuss these with your GP or a suitable clinician.` : ` ${firstStep(dashboard, topic)}`));
  }
  if (/\b(scores|summary|overview|results|metrics)\b/.test(q)) {
    const scores = Object.entries(scoreLabels).filter(([key]) => Number.isFinite(dashboard.scores?.[key]));
    if (!scores.length) return respond('No wellness scores are available yet. Complete a wellness check to see a personalised summary.');
    const [lowestKey, lowestLabel] = [...scores].sort(([a],[b]) => dashboard.scores[a] - dashboard.scores[b])[0];
    return respond(`Your current wellness picture:\n${scores.map(([key,label]) => `• ${label}: ${dashboard.scores[key]}/100`).join('\n')}\n\n${lowestLabel} is the lowest score (${dashboard.scores[lowestKey]}/100), so it may be a useful area to explore. Higher scores mean fewer reported concerns. Your chosen priorities and any important clinical flags also matter.`);
  }
  if (/\b(priorit\w*|matters most)\b/.test(q)) {
    const chosen = dashboard.selected_priorities || [];
    return respond(chosen.length ? `You chose these priorities:\n${chosen.map(x=>`• ${x.title}`).join('\n')}\n\nYour plan combines those choices with any important clinical concerns. ${firstStep(dashboard,topic)}` : `You have not selected any priorities in this assessment. ${firstStep(dashboard,topic)}`);
  }
  if (/\b(week|seven|7.day|routine|schedule)\b/.test(q)) return respond(`Here is a simple way to organise the next week around your plan:\n\n1. Today: read the recommendation below and write down one question.\n2. In the next day or two: contact the suggested service or choose a small practical task.\n3. Later in the week: note what felt manageable and what support you still need.\n\n${firstStep(dashboard,topic)}\n\nThis is a prepared demo plan, not a prescribed exercise or treatment programme.`);
  if (/\b(thank|thanks)\b/.test(q)) return respond('You’re welcome. One manageable step is enough to begin. You can ask about another recommendation, your scores, or your chosen priorities.');
  if (/^(hi|hello|hey)[.!\s]*$/.test(q)) return respond('Hello! I’m the ACT demo guide. I use prepared replies matched to your assessment. Try “Explain my scores”, “Why was this recommended?”, or “Help me plan my week”.');
  if (/\b(start|first|next step|begin|do today)\b/.test(q)) return respond(firstStep(dashboard,topic) + '\n\nFor today, write down who you will contact or what you will try. If a clinical concern is flagged, arrange professional advice before starting a new routine.');
  if (/\b(why|recommend|explain|tell me|what about|more about)\b/.test(q) || topic !== 'overview') {
    const reasons = facts(answers, topic);
    const rec = findRecommendation(dashboard,topic);
    if (rec || reasons.length) return respond((reasons.length ? `This relates to your answers: ${reasons.join(' and ')}. ` : 'This option appears in your current wellness plan. ') + firstStep(dashboard,topic) + (['mood','cognition'].includes(topic) || (topic === 'movement' && answers.falls_3_months === 'Yes') || (topic === 'nutrition' && answers.lost_3kg === 'Yes') ? '\n\nDiscuss the reported change with your GP or a suitable clinician; this demo cannot assess its cause.' : '\n\nWould you like to turn that recommendation into one practical next step?'));
    if (topic !== 'overview') return respond(`Your current answers do not flag a specific concern about ${topic.replaceAll('_',' ')}, and I cannot infer one. If this is a new concern, tell your GP or a suitable clinician. I can explain the recommendations that are in your plan.`);
  }
  return respond('This demo uses prepared responses, so I may not cover that question. I can explain your wellness scores, chosen priorities and recommendations, or help organise a simple next step. Try “Explain my scores” or “Why was this recommended?”');
}
