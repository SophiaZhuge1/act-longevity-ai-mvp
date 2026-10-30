import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { demoReply } from './demo-chat.js';
const { dashboard, answers } = JSON.parse(readFileSync(new URL('./demo-assessment.json', import.meta.url)));
test('uses current scores, not fixed sample values', () => {
  const changed = { ...dashboard, scores: { ...dashboard.scores, clinical_risk: 37 } };
  const reply = demoReply('Explain my Clinical Risk score', changed, answers).text;
  assert.match(reply, /37\/100/);
  assert.match(reply, /not a diagnosis/);
});
test('grounds movement advice in actual reported answers', () => {
  const reply = demoReply('Why exercise?', dashboard, answers).text;
  assert.match(reply, /reported a recent fall/);
  assert.match(reply, /do not exercise regularly/);
  const healthy = { ...dashboard, recommendations: [] };
  const other = demoReply('Why exercise?', healthy, { falls_3_months:'No', regular_exercise:'Yes' }).text;
  assert.doesNotMatch(other, /reported a recent fall/);
  assert.match(other, /do not flag a specific concern/);
});
test('follow-up keeps the previous topic', () => {
  const first = demoReply('Tell me about nutrition', dashboard, answers);
  const followUp = demoReply('What should I do first?', dashboard, answers, [{role:'assistant',...first}]);
  assert.equal(followUp.topic, 'nutrition');
  assert.match(followUp.text, /write down who/);
});
test('shows selected priorities and handles unsupported questions honestly', () => {
  const reply = demoReply('What are my priorities?', dashboard, answers).text;
  for(const item of dashboard.selected_priorities) assert.ok(reply.includes(item.title));
  assert.match(demoReply('Who won the football?', dashboard, answers).text, /prepared responses/);
});
test('does not prescribe or diagnose and handles urgent descriptions', () => {
  assert.match(demoReply('What dose of vitamin D?',dashboard,answers).text,/cannot choose/);
  assert.match(demoReply('Do I have dementia?',dashboard,answers).text,/cannot diagnose/);
  assert.match(demoReply('I have chest pain',dashboard,answers).text,/call 999/);
});
