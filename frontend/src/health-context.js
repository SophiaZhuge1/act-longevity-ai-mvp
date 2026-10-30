import questions from './pages-questions.json';
const safeChoice = (value, choices) => choices.includes(value) ? value : undefined;
export function buildHealthContext(dashboard, answers) {
  const profile = dashboard.profile || {};
  const dob = profile.dob && new Date(`${profile.dob}T00:00:00`);
  const now = new Date();
  const age = dob && !Number.isNaN(dob.getTime()) ? now.getFullYear() - dob.getFullYear() - (now.getMonth() < dob.getMonth() || (now.getMonth() === dob.getMonth() && now.getDate() < dob.getDate()) ? 1 : 0) : null;
  return {
    profile: {
      age_band: age !== null && age >= 18 && age <= 120 ? `${Math.floor(age / 10) * 10}s` : undefined,
      living_arrangement: safeChoice(profile.living_arrangement, ['Alone', 'With a partner', 'With extended family', 'Assisted living', 'Care home']),
      care_support: safeChoice(profile.care_support, ['No', 'Yes - partner', 'Yes - children', 'Yes - other family or friends', 'Yes - paid carer']),
    },
    answers: questions.filter(q => q.options.includes(answers[q.id])).map(q => ({ id: q.id, question: q.text, answer: answers[q.id] })),
    wellness_scores: Object.fromEntries(['staying_healthy', 'independence', 'wellbeing', 'social_resources', 'clinical_risk'].map(key => [key, dashboard.scores?.[key]])),
    selected_priorities: dashboard.selected_priorities || [],
    recommendations: dashboard.recommendations || [],
    clinical_risks: dashboard.clinical_risks || [],
    prevention_opportunities: dashboard.prevention_opportunities || [],
    suggested_resources: (dashboard.resources || []).filter(r => r.category === 'Trusted health guidance').map(r => ({ name: r.name, url: r.url })),
  };
}
