// Apps Script HMAC verifier smoke tests in Node.js without Google credentials.
const fs = require('fs'), vm = require('vm'), crypto = require('crypto'), assert = require('assert');
const secret = 'A'.repeat(48);
const used = new Map();
const sandbox = {
  PropertiesService: {getScriptProperties: () => ({getProperty: k => k === 'OJA_HMAC_SECRET' ? secret : null})},
  CacheService: {getScriptCache: () => ({get:k => used.get(k), put:(k,v) => used.set(k,v)})},
  Utilities: {computeHmacSha256Signature:(m,s) => Array.from(crypto.createHmac('sha256',s).update(m).digest()),
    base64Decode:x => Array.from(Buffer.from(x,'base64')),
    newBlob:x => ({getDataAsString: () => Buffer.from(x).toString('utf8')})},
  console
};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(__dirname + '/../apps_script/Code.gs','utf8')+'\nthis.verify=verifyEnvelope_;',sandbox);
const payload = {schema_version:1, source:'unit_test',jobs:[]};
const timestamp = Math.floor(Date.now()/1000), nonce = '1234567890abcdef1234567890abcdef';
const payload_b64 = Buffer.from(JSON.stringify(payload)).toString('base64');
const signature = crypto.createHmac('sha256', secret).update(`${timestamp}.${nonce}.${payload_b64}`).digest('hex');
const env = {timestamp, nonce, payload_b64, signature};
assert.equal(sandbox.verify(env).schema_version, 1);
assert.throws(()=>sandbox.verify(env),/Replay/);
assert.throws(()=>sandbox.verify({...env,nonce:'a'.repeat(32),signature:'0'.repeat(64)}),/Assinatura/);
console.log('Apps Script verifier: 3 offline checks passed');
