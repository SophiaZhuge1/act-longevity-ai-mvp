import scoringSource from '../../backend/scoring.py?raw';
import resourcesSource from '../../backend/local_resources.py?raw';
import questions from './pages-questions.json';

export const PAGES_MODE = import.meta.env.VITE_GITHUB_PAGES === 'true';
let runtimePromise;
let history = [];
async function scoringRuntime() {
  if (!runtimePromise) runtimePromise = (async () => {
    await new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.js';
      script.onload = resolve;
      script.onerror = () => reject(new Error('The browser assessment engine could not load. Check your connection and try again.'));
      document.head.appendChild(script);
    });
    const python = await window.loadPyodide();
    python.FS.writeFile('/home/pyodide/act_scoring.py', scoringSource);
    python.FS.writeFile('/home/pyodide/act_resources.py', resourcesSource);
    await python.runPythonAsync('import json\nfrom act_scoring import sanitise_answers, score_answers, identified_concerns, persona_and_recommendations\nfrom act_resources import resources_for');
    return python;
  })().catch(error => { runtimePromise = undefined; throw error; });
  return runtimePromise;
}
export async function apiFetch(url, options = {}) {
  if (!PAGES_MODE) return fetch(url, options);
  const path = url.replace(/^.*(?=\/api\/)/, '');
  const respond = (data, status = 200) => new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json' } });
  if (path === '/api/questions') return respond({ questions });
  if (path === '/api/chat/status') return respond({ available: false });
  if (path === '/api/members/login') return respond({ error: 'Account access needs the full hosted service. This Pages version keeps progress only during your current visit.' }, 503);
  if (!['/api/concerns', '/api/assessments'].includes(path)) return respond({ error: 'This feature needs the full hosted service.' }, 503);
  const payload = JSON.parse(options.body || '{}');
  const python = await scoringRuntime();
  python.globals.set('act_request_json', JSON.stringify(payload));
  try {
    const result = JSON.parse(python.runPython(`
act_request = json.loads(act_request_json)
act_answers = sanitise_answers(act_request.get('answers', {}))
act_scores = score_answers(act_answers)
act_profile = act_request.get('profile', {})
act_result = {'concerns': identified_concerns(act_answers, act_scores)} if '${path}' == '/api/concerns' else {
    'profile': act_profile,
    'scores': act_scores,
    **persona_and_recommendations(act_profile, act_answers, act_scores, act_request.get('selected_priorities', [])),
    'resources': resources_for(act_scores, act_profile.get('postcode', ''), act_answers),
}
json.dumps(act_result)
`));
    if (path === '/api/assessments') {
      result.user_id = crypto.randomUUID();
      result.created_at = new Date().toISOString();
      history = [...history, { assessment_id: result.user_id, created_at: result.created_at, scores: result.scores, summary: result.persona, selected_priorities: result.selected_priorities }];
      result.history = history;
    }
    return respond(result);
  } finally {
    python.runPython("for act_name in ['act_request_json', 'act_request', 'act_answers', 'act_scores', 'act_profile', 'act_result']:\n    globals().pop(act_name, None)");
  }
}
