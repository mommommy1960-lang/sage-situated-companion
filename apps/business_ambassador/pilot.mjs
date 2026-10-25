import {normalize} from './engine.mjs';
export const PROFILE_KEY='sage.owner-faq.v1';
export const DISCLOSURE='User-entered, unverified; no sales or booked customer. Manual estimates only.';
function field(value,max,label){if(typeof value!=='string'||!value.trim()||value.length>max||/[\u0000-\u0008\u000b-\u001f\u007f]/.test(value))throw new Error(`${label}: enter 1–${max} plain-text characters.`);return value.trim();}
export function validateProfile(raw){
 if(!raw||typeof raw!=='object')throw new Error('Invalid profile.');
 const name=field(raw.name,80,'Business name');
 if(!Array.isArray(raw.faqs)||raw.faqs.length<1||raw.faqs.length>5)throw new Error('Use 1–5 FAQ entries.');
 const seen=new Set();
 const faqs=raw.faqs.map((f,i)=>{if(!f||typeof f!=='object')throw new Error('Invalid FAQ.');const question=field(f.question,180,'Question'),key=normalize(question);if(!key||seen.has(key))throw new Error('Questions must be distinct and contain letters or numbers.');seen.add(key);return {id:`owner-${i+1}`,question,answer:field(f.answer,700,'Answer'),sourceLabel:`Owner-entered, unverified · ${field(f.sourceLabel,100,'Source label')}`,sourceUrl:'',aliases:[]};});
 return {id:'owner',name,kind:'Owner-approved · unverified',intro:'Owner-entered FAQ. Exact question matches only; unknown questions go to a person.',faqs};
}
export function profileInput(profile){return {name:profile.name,faqs:profile.faqs.map(f=>({question:f.question,answer:f.answer,sourceLabel:f.sourceLabel.replace(/^Owner-entered, unverified · /,'')}))};}
export function saveProfile(storage,raw){const profile=validateProfile(raw);storage.setItem(PROFILE_KEY,JSON.stringify({version:1,profile:profileInput(profile)}));return profile;}
export function loadProfile(storage){const text=storage.getItem(PROFILE_KEY);if(text===null)return null;if(text.length>16000)throw new Error('Saved profile is too large. Clear saved data.');let data;try{data=JSON.parse(text);}catch{throw new Error('Saved profile is unreadable. Clear saved data.');}if(data?.version!==1)throw new Error('Unsupported saved profile. Clear saved data.');return validateProfile(data.profile);}
export function clearProfile(storage){storage.removeItem(PROFILE_KEY);}
export function evaluation(raw){if(!raw||!['correct','needs-review'].includes(raw.result))throw new Error('Choose correct or needs review.');const label=field(raw.label,180,'Test question / label');if(typeof raw.minutes!=='string'||!/^\d{1,3}(\.\d)?$/.test(raw.minutes))throw new Error('Staff minutes must be 0–480, with at most one decimal.');const minutes=Number(raw.minutes);if(minutes>480)throw new Error('Staff minutes must be 0–480.');return {label,result:raw.result,staffMinutesEstimate:minutes};}
export function addEvaluation(rows,raw,profile){if(rows.length>=100)throw new Error('Maximum 100 manual tests. Export or clear first.');return {...evaluation(raw),profile:field(profile,80,'Profile'),disclosure:DISCLOSURE};}
