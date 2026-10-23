/**
 * Open Job Agent | Public portfolio edition
 * Bound Apps Script for a NEW, privately owned Google Sheet.
 * This endpoint only records vacancies. No Gmail, Drive, CV generation or applications.
 * HMAC-SHA256 over `${timestamp}.${nonce}.${payload_b64}`; 5-minute clock window.
 * Script Property OJA_HMAC_SECRET must be configured by the OWNER, never committed.
 */
const HEADERS = {
  VAGAS: ['ID', 'Primeira observacao', 'Empresa', 'Cargo', 'Score', 'Status', 'Local',
          'URL', 'Bloqueios', 'Informacoes pendentes', 'Competencias', 'Fonte', 'Atualizado em'],
  EXECUCOES: ['Data', 'Origem', 'Recebidas', 'Novas', 'Atualizadas'],
};
function setupProject() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  if (!ss) throw new Error('Abra Apps Script a partir de uma planilha nova.');
  PropertiesService.getScriptProperties().setProperty('SPREADSHEET_ID', ss.getId());
  Object.keys(HEADERS).forEach(name => getOrCreateSheet_(ss, name));
  if (!ss.getSheetByName('PAINEL')) ss.insertSheet('PAINEL', 0);
  updatePanel_(ss);
  console.log('Planilha de demonstracao preparada.');
}
function getOrCreateSheet_(ss, name) {
  let sheet = ss.getSheetByName(name);
  if (!sheet) sheet = ss.insertSheet(name);
  if (sheet.getLastRow() === 0) sheet.getRange(1, 1, 1, HEADERS[name].length).setValues([HEADERS[name]]);
  sheet.setFrozenRows(1);
  return sheet;
}
function sheet_() {
  const id = PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID');
  if (!id) throw new Error('Execute setupProject primeiro.');
  return SpreadsheetApp.openById(id);
}
function hex_(bytes) { return bytes.map(x => ('0' + (x & 255).toString(16)).slice(-2)).join(''); }
function clean_(value, size) {
  const s = String(value == null ? '' : value).replace(/[\u0000-\u001f\u007f]/g, ' ').slice(0, size || 200);
  return /^[=+@\-\t\r]/.test(s) ? "'" + s : s;
}
function respond_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function doGet() { return ContentService.createTextOutput('POST signed reports only'); }

function verifyEnvelope_(env) {
  if (!env || typeof env !== 'object') throw new Error('Envelope ausente');
  const secret = PropertiesService.getScriptProperties().getProperty('OJA_HMAC_SECRET') || '';
  if (secret.length < 32) throw new Error('HMAC nao configurado');
  const ts = Number(env.timestamp);
  if (!Number.isInteger(ts) || Math.abs(Date.now()/1000 - ts) > 300) throw new Error('Timestamp fora da janela');
  if (!/^[0-9a-f]{32}$/.test(env.nonce || '') || !/^[0-9a-f]{64}$/.test(env.signature || '')) throw new Error('Envelope invalido');
  const payload = String(env.payload_b64 || '');
  if (!payload || payload.length > 170000 || !/^[a-zA-Z0-9+/]+={0,2}$/.test(payload)) throw new Error('Payload invalido');
  const expected = hex_(Utilities.computeHmacSha256Signature(ts+'.'+env.nonce+'.'+payload, secret));
  let diff = 0;
  for (let i=0; i<64; i++) diff |= expected.charCodeAt(i) ^ env.signature.charCodeAt(i);
  if (diff !== 0) throw new Error('Assinatura invalida');
  // Called while holding script lock to make replay check/set atomic within this script.
  const cache = CacheService.getScriptCache();
  const key = 'nonce:' + env.nonce;
  if (cache.get(key)) throw new Error('Replay detectado');
  const report = JSON.parse(Utilities.newBlob(Utilities.base64Decode(payload)).getDataAsString('UTF-8'));
  if (report.schema_version !== 1 || !Array.isArray(report.jobs) || report.jobs.length > 60) throw new Error('Formato de relatorio invalido');
  cache.put(key, '1', 360);
  return report;
}
function doPost(e) {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(12000)) return respond_({ok:false, error:'busy'});
  try {
    const env = JSON.parse(e.postData.contents);
    const report = verifyEnvelope_(env);
    const ss = sheet_();
    const result = upsert_(ss.getSheetByName('VAGAS'), report.jobs);
    ss.getSheetByName('EXECUCOES').appendRow([new Date(), clean_(report.source, 40), report.jobs.length, result.inserted, result.updated]);
    updatePanel_(ss);
    return respond_({ok:true, inserted:result.inserted, updated:result.updated});
  } catch (err) {
    // Keep errors generic, no secret/HTTP payload leakage.
    console.error('Web app request rejected');
    return respond_({ok:false, error:'request_rejected'});
  } finally { lock.releaseLock(); }
}
function upsert_(sheet, jobs) {
  const values = sheet.getDataRange().getValues();
  const rowIds = new Map();
  for (let i=1;i<values.length;i++) if (values[i][0]) rowIds.set(String(values[i][0]), i+1);
  let inserted=0, updated=0;
  for (const j of jobs) {
    if (!j || typeof j.id !== 'string' || !j.id || typeof j.url !== 'string' || !/^https:\/\//i.test(j.url)) continue;
    if (typeof j.score !== 'number' || !Number.isFinite(j.score)) continue;
    if (!['BLOCKED','LOW_MATCH','REVIEW'].includes(j.status)) continue;
    const id = clean_(j.id, 180);
    const previousRow = rowIds.get(id);
    const firstSeen = previousRow ? values[previousRow-1][1] : new Date();
    const row = [id, firstSeen, clean_(j.company,160), clean_(j.title,250), Math.max(0,Math.min(100,j.score)),
      j.status, clean_(j.location,150), clean_(j.url,500), clean_((j.blockers||[]).join(' | '),900),
      clean_((j.unknowns||[]).join(' | '),900), clean_((j.matched_skills||[]).join(', '),200),
      clean_(j.provider,40), new Date()];
    if (previousRow) { sheet.getRange(previousRow,1,1,row.length).setValues([row]); updated++; }
    else { sheet.appendRow(row); inserted++; rowIds.set(id,sheet.getLastRow()); }
  }
  return {inserted,updated};
}
function updatePanel_(ss) {
  const sheet = ss.getSheetByName('PAINEL');
  sheet.getRange('A1:B1').setValues([['OPEN JOB AGENT', 'Research dashboard']]);
  sheet.getRange('A3:A6').setValues([['Vagas registradas'],['Revisao humana'],['Bloqueadas'],['Ultima sincronizacao']]);
  sheet.getRange('B3').setFormula('=MAX(0,COUNTA(VAGAS!A:A)-1)');
  sheet.getRange('B4').setFormula('=COUNTIF(VAGAS!F:F,"REVIEW")');
  sheet.getRange('B5').setFormula('=COUNTIF(VAGAS!F:F,"BLOCKED")');
  sheet.getRange('B6').setValue(new Date());
}
