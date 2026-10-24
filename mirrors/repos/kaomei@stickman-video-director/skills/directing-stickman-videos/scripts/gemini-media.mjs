#!/usr/bin/env node
// Optional one-shot adapter; no generation is performed by installation/tests.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const [kind, ...args] = process.argv.slice(2);
const value = flag => args[args.indexOf(flag) + 1];
const required = flag => { if (!args.includes(flag) || !value(flag) || value(flag).startsWith('--')) throw new Error(`Required ${flag}`); return value(flag); };
function wav(pcm, rate) {
  const h = Buffer.alloc(44); h.write('RIFF'); h.writeUInt32LE(36 + pcm.length, 4); h.write('WAVEfmt ', 8); h.writeUInt32LE(16, 16); h.writeUInt16LE(1, 20); h.writeUInt16LE(1, 22); h.writeUInt32LE(rate, 24); h.writeUInt32LE(rate * 2, 28); h.writeUInt16LE(2, 32); h.writeUInt16LE(16, 34); h.write('data', 36); h.writeUInt32LE(pcm.length, 40); return Buffer.concat([h, pcm]);
}
async function main() {
  if (!['speech', 'image'].includes(kind)) throw new Error('Use speech or image');
  if (kind === 'speech' && args.includes('--direction')) throw new Error('Autopilot uses the selected named voice without extra voice/style instructions; remove --direction');
  if (!args.includes('--allow-network')) throw new Error('Network disabled; require explicit --allow-network after user authorization');
  const key = process.env.GEMINI_API_KEY; if (!key) throw new Error('Set GEMINI_API_KEY in the environment; do not paste it in chat');
  const model = required('--model'); if (!/^[a-zA-Z0-9._-]+$/.test(model)) throw new Error('Invalid model ID');
  const output = path.resolve(required('--output')), receipt = `${output}.request.json`;
  if (fs.existsSync(output) || fs.existsSync(receipt)) throw new Error('Output or prior request receipt exists; inspect it before any retry');
  const input = fs.readFileSync(required(kind === 'speech' ? '--text' : '--prompt'), 'utf8');
  const parts = [];
  parts.push({text: input});
  for (let i = 0; i < args.length; i++) if (args[i] === '--reference') {
    if (kind !== 'image') throw new Error('References only supported for images');
    const f = path.resolve(args[++i]); if (!/\.(png|jpe?g)$/i.test(f) || fs.statSync(f).size > 10 * 1024 * 1024) throw new Error('Reference must be PNG/JPEG up to 10 MiB');
    parts.push({inlineData: {mimeType: /\.png$/i.test(f) ? 'image/png' : 'image/jpeg', data: fs.readFileSync(f).toString('base64')}});
  }
  const config = kind === 'speech' ? {responseModalities: ['AUDIO'], speechConfig: {voiceConfig: {prebuiltVoiceConfig: {voiceName: required('--voice')}}}} : {responseModalities: ['TEXT', 'IMAGE']};
  fs.mkdirSync(path.dirname(output), {recursive: true});
  const record = {kind, model, requested_at: new Date().toISOString(), request_id: crypto.randomUUID(), status: 'submitted_or_unknown', warning: 'One request only; inspect provider history before retrying'};
  fs.writeFileSync(receipt, JSON.stringify(record, null, 2), {flag: 'wx'});
  try {
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {method: 'POST', headers: {'Content-Type': 'application/json', 'x-goog-api-key': key}, body: JSON.stringify({contents: [{role: 'user', parts}], generationConfig: config}), signal: AbortSignal.timeout(180000)});
    if (!response.ok) throw new Error(`Provider HTTP ${response.status}; response body deliberately omitted`);
    const data = await response.json(), candidates = data.candidates?.[0]?.content?.parts || [];
    const payload = candidates.map(p => p.inlineData || p.inline_data).find(p => p && (kind === 'speech' ? p.mimeType?.startsWith('audio/') : p.mimeType?.startsWith('image/')));
    if (!payload?.data) throw new Error('No native media payload returned; inspect request receipt/provider history');
    let bytes = Buffer.from(payload.data, 'base64');
    if (kind === 'speech') {
      if (!/\.wav$/i.test(output) || !/^audio\/(?:L16|pcm)/i.test(payload.mimeType)) throw new Error('Expected PCM audio and .wav destination');
      const rate = Number(payload.mimeType.match(/rate=(\d+)/)?.[1] || 24000); bytes = wav(bytes, rate);
    } else if (!(payload.mimeType === 'image/png' && /\.png$/i.test(output) || payload.mimeType === 'image/jpeg' && /\.jpe?g$/i.test(output))) throw new Error(`Output extension must match native ${payload.mimeType}`);
    fs.writeFileSync(output, bytes, {flag: 'wx'}); Object.assign(record, {status: 'complete', output, sha256: crypto.createHash('sha256').update(bytes).digest('hex')});
  } catch (e) { record.status = 'failed_or_unknown'; record.error = e.message; throw e; }
  finally { fs.writeFileSync(receipt, JSON.stringify(record, null, 2)); }
  console.log(JSON.stringify({output, receipt}));
}
main().catch(e => { console.error(e.message); process.exitCode = 1; });
