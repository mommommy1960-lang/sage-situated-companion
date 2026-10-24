import {DeviceController} from './device-controller.mjs';
import {askText} from './model-client.mjs';
import {SpeechController} from './speech-controller.mjs?v=03b';
const $=id=>document.getElementById(id);
let lastTranscript='',modelEpoch=0,job=null,busy=false,hasAnswer=false,timer;
function notice(text){$('notice').textContent=text;}
const voice=new SpeechController({speech:window.speechSynthesis,Utterance:window.SpeechSynthesisUtterance,
  change:text=>{$('voiceStatus').textContent=text;}});
const dc=new DeviceController({mediaDevices:navigator.mediaDevices,
  Recognition:window.SpeechRecognition||window.webkitSpeechRecognition,
  geolocation:navigator.geolocation,speech:window.speechSynthesis,Utterance:window.SpeechSynthesisUtterance},
  message=>{render();if(message)notice(message);});
function render(){
  const on=dc.active;
  $('light').classList.toggle('on',on);
  $('sessionLabel').textContent=on?'Sage is on · you choose her senses':'Sage is off';
  $('start').disabled=on;
  $('cameraOn').disabled=!on||!!dc.stream;
  $('micOn').disabled=!on||!$('speechConsent').checked||!!dc.recognition;
  $('locationOn').disabled=!on||dc.watch!==null;
  $('ask').disabled=!on||busy||!$('cloud').checked;
  $('read').disabled=!on||!hasAnswer;
  $('testVoice').disabled=!on;
  $('cameraState').textContent=dc.stream?'PREVIEW ON':'OFF';
  $('micState').textContent=dc.recognition?'LISTENING':'OFF';
  $('locationState').textContent=dc.watch!==null?'ON · LOCAL':'OFF';
  $('cameraEmpty').hidden=!!dc.stream;
  if(!dc.stream)$('video').srcObject=null;
  const p=dc.location;
  $('locationValue').textContent=p?`${p.latitude.toFixed(5)}, ${p.longitude.toFixed(5)} · accuracy ±${Math.round(p.accuracy)} m · updated ${new Date(p.timestamp).toLocaleTimeString()}. Local display only.`:'Location is off or waiting for a fix. Coordinates are not sent to Sage.';
  if(dc.transcript&&dc.transcript!==lastTranscript){lastTranscript=dc.transcript;$('question').value=dc.transcript;notice('Your words are in the question box. Press Ask Sage to get an answer.');}
}
function safe(fn){return async()=>{try{await fn();}catch(error){notice(error?.message||'That feature could not start. Check browser permissions.');}render();};}
function cancelModel(){modelEpoch++;clearTimeout(timer);try{job?.abort();}catch{}job=null;busy=false;}
function stop(){
  cancelModel();dc.stop();voice.stop();
  $('cloud').checked=false;$('speechConsent').checked=false;$('autoSpeak').checked=false;
  lastTranscript='';$('question').value='';$('answer').textContent='Session stopped. Start Sage to begin again.';hasAnswer=false;
  $('modelStatus').textContent='Stopped. Text already sent to the service cannot be retracted.';
  render();notice('Everything stopped. Camera, voice input and location are off; speech is cancelled.');
}
function populateVoices(){
  const select=$('voiceChoice'),previous=select.value;
  select.replaceChildren();
  const defaultOption=document.createElement('option');defaultOption.value='';defaultOption.textContent='Device default voice';select.append(defaultOption);
  for(const v of voice.voices()){
    const option=document.createElement('option');option.value=v.voiceURI;
    option.textContent=`${v.name} · ${v.lang}${v.localService?' · on device':''}`;select.append(option);
  }
  if([...select.options].some(o=>o.value===previous))select.value=previous;
  $('voiceCount').textContent=voice.voices().length?`${voice.voices().length} voices found on this browser.`:'No voice list yet. The device default may still work. Tap Test Sage’s voice.';
}
$('start').onclick=()=>{dc.start();populateVoices();notice('Sage is on. Switching tabs will keep this session and your text.');};
$('stop').onclick=stop;
$('cloud').onchange=()=>{if(!$('cloud').checked)cancelModel();render();};
$('speechConsent').onchange=()=>{if(!$('speechConsent').checked)dc.stopMic();render();};
$('cameraOn').onclick=safe(async()=>{notice('Waiting for camera permission…');const stream=await dc.camera();if(stream){$('video').srcObject=stream;notice('Camera preview is on. Images stay on this device; Sage is not analysing them.');}});
$('cameraOff').onclick=()=>{dc.stopCamera();notice('Camera off.');};
$('micOn').onclick=safe(()=>{lastTranscript='';dc.transcript='';dc.listen();notice('Listening to one phrase. Review your words above, then press Ask Sage.');});
$('micOff').onclick=()=>{dc.stopMic();notice('Voice input off.');};
$('locationOn').onclick=safe(()=>{dc.locate();notice('Waiting for location permission. Coordinates remain local.');});
$('locationOff').onclick=()=>{dc.stopLocation();notice('Location off and cleared.');};
$('quiet').onclick=()=>voice.stop();
$('testVoice').onclick=safe(()=>{dc.require();voice.speak('Hello Queen. I am Sage. This is my voice test.', $('voiceChoice').value);});
$('read').onclick=safe(()=>{dc.require();voice.speak($('answer').textContent,$('voiceChoice').value);});
$('ask').onclick=async()=>{
  if(!dc.active||!$('cloud').checked||busy)return;
  const q=$('question').value.trim();if(!q){notice('Enter or speak a question first.');return;}
  const epoch=++modelEpoch;busy=true;hasAnswer=false;render();
  $('modelStatus').textContent='Waiting for Sage’s written answer…';notice('Only the text you entered is being sent.');
  timer=setTimeout(()=>{if(epoch===modelEpoch){cancelModel();$('modelStatus').textContent='Timed out. You can try again; no automatic retry.';render();}},90000);
  try{
    job=new AbortController();const answer=await askText(q,{signal:job.signal});
    if(epoch!==modelEpoch||!dc.active)return;
    $('answer').textContent=answer;hasAnswer=true;
    $('modelStatus').textContent='Sage answered. Tap Read answer aloud to hear this answer.';
    if($('autoSpeak').checked&&!document.hidden){try{voice.speak(answer,$('voiceChoice').value);}catch(error){$('voiceStatus').textContent=error.message;}}
    else if($('autoSpeak').checked){$('voiceStatus').textContent='Answer ready. Return to Sage and tap Read answer aloud.';}
  }catch(error){if(epoch===modelEpoch){$('modelStatus').textContent='Sage could not answer. The free Space may be asleep, busy or at quota. No paid fallback.';notice('Model unavailable. Device controls still work.');}}
  finally{if(epoch===modelEpoch){clearTimeout(timer);job=null;busy=false;render();}}
};
// Ordinary tab switches do not call Stop, cancel inference or reset any choices.
document.addEventListener('visibilitychange',()=>{
  if(document.hidden){if(dc.active)notice('Sage session kept while you switch tabs. Your browser may limit background device access.');}
  else{if(dc.stream&&dc.stream.getTracks().every(t=>t.readyState==='ended'))dc.stopCamera();render();if(dc.active)notice('Welcome back. Your session, question, answer and approvals are still here.');}
});
// Actual navigation or closing releases devices, without deleting the visible conversation.
window.addEventListener('pagehide',()=>{cancelModel();dc.stopCamera();dc.stopMic();dc.stopLocation();voice.stop();});
window.speechSynthesis?.addEventListener?.('voiceschanged',populateVoices);
populateVoices();render();
