// A bounded FAQ lookup, not a language model or a server authorization layer.
export const normalize = text => String(text).toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
export function lookup(profile, question) {
  if(typeof question !== 'string' || !question.trim() || question.length > 500) throw new Error('Enter a question of 1–500 characters.');
  const key = normalize(question);
  const matches = profile.faqs.filter(f => [f.question,...f.aliases].some(a => normalize(a) === key));
  if(matches.length !== 1) return {kind:'unknown',id:null,text:"I don’t have an approved answer to that question. A person should help rather than having me guess.",sourceLabel:'No approved match',sourceUrl:''};
  const f=matches[0];
  return {kind:'answer',id:f.id,text:f.answer,sourceLabel:f.sourceLabel,sourceUrl:f.sourceUrl};
}
export class AmbassadorSession {
  constructor(profiles,{clock=()=>Date.now(),delay=()=>new Promise(r=>setTimeout(r,450)),lifecycle=null}={}) {
    this.profiles=profiles;this.clock=clock;this.delay=delay;this.lifecycle=lifecycle;this.active=false;this.epoch=0;this.sequence=0;this.pending=null;this.receipts=[];this.profile=profiles[0];
  }
  record(type,detail={}) {const r={sequence:++this.sequence,time:new Date(this.clock()).toISOString(),type,...detail};this.receipts.push(r);if(this.receipts.length>100)this.receipts.shift();return r;}
  start(){if(this.active)return;this.active=true;this.epoch++;this.pending=null;this.lifecycle?.start();this.record('session_started',{profile:this.profile.id});}
  stop(){this.active=false;this.epoch++;this.pending=null;this.lifecycle?.stop();this.record('session_stopped');}
  select(id){const p=this.profiles.find(p=>p.id===id);if(!p)throw new Error('Unknown business profile');this.stop();this.profile=p;}
  require(){if(!this.active)throw new Error('Start a session first.');}
  async ask(question){this.require();const epoch=this.epoch,p=this.profile;const result=lookup(p,question);await this.delay();if(!this.active||this.epoch!==epoch)return null;this.record(result.kind==='answer'?'approved_answer':'human_handoff_needed',{profile:p.id,faq:result.id});return result;}
  prepare(){this.require();const permit={id:`draft-${this.epoch}-${this.sequence+1}`,epoch:this.epoch,profile:this.profile.id,expiresAt:this.clock()+60000};this.pending=permit;this.record('draft_previewed',{permit:permit.id});return {...permit};}
  revoke(){const id=this.pending?.id;this.pending=null;if(id)this.record('approval_revoked',{permit:id});}
  confirm(id){this.require();const p=this.pending;if(!p||p.id!==id||p.epoch!==this.epoch||p.profile!==this.profile.id||this.clock()>=p.expiresAt){this.pending=null;this.record('draft_blocked');throw new Error('Approval is missing, expired or revoked. Preview a new draft.');}this.pending=null;this.record('local_draft_prepared',{permit:p.id,profile:p.profile});return {type:'LOCAL_DRAFT_ONLY',business:this.profile.name,subject:'Request for a human follow-up',message:'Please help me with a question that needs a person. Add your question and contact details yourself before sending.',notice:'Not sent. No booking, account access, payment or external action occurred.'};}
  clearReceipts(){this.receipts=[];}
}
