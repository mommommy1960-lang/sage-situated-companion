// Retains the utterance, selects installed voices and reports actual browser events.
export class SpeechController {
  constructor({speech, Utterance, change=()=>{}, schedule=(fn,ms)=>setTimeout(fn,ms), unschedule=id=>clearTimeout(id)}) {
    Object.assign(this,{speech,Utterance,change,schedule,unschedule});
    this.epoch=0; this.utterance=null; this.timer=null;
  }
  voices() { return this.speech?.getVoices?.() || []; }
  stop(message='Speech stopped.') {
    this.epoch++; this.unschedule(this.timer); this.timer=null;
    this.utterance=null; this.speech?.cancel(); this.change(message);
  }
  speak(text, voiceURI='') {
    if(!this.speech || !this.Utterance) throw new Error('This browser has no speech playback. Open Sage in Chrome.');
    if(!text?.trim()) throw new Error('There is no answer to read yet. Try Test Sage’s voice first.');
    this.stop('Preparing speech…');
    const epoch=this.epoch, u=new this.Utterance(text.trim());
    const voices=this.voices();
    const selected=voices.find(v=>v.voiceURI===voiceURI)
      || voices.find(v=>v.localService&&/^en[-_]/i.test(v.lang))
      || voices.find(v=>/^en[-_]/i.test(v.lang)) || voices.find(v=>v.default);
    if(selected)u.voice=selected;
    u.lang=selected?.lang || 'en-US'; u.volume=1; u.rate=1; u.pitch=1;
    let started=false;
    u.onstart=()=>{if(epoch!==this.epoch)return;started=true;this.unschedule(this.timer);this.change('Speaking now. If silent, check tablet media volume and Bluetooth output.');};
    u.onend=()=>{if(epoch!==this.epoch)return;this.unschedule(this.timer);this.utterance=null;this.change('Browser reports speech finished. Did you hear Sage?');};
    u.onerror=e=>{if(epoch!==this.epoch)return;this.unschedule(this.timer);this.utterance=null;const hints={
      'not-allowed':'Speech was blocked. Tap Test Sage’s voice directly in this tab.',
      'audio-busy':'Audio is busy. Pause the ChatGPT voice call, then try Test Sage’s voice.',
      'audio-hardware':'The tablet audio output is unavailable. Check media volume and Bluetooth.',
      'synthesis-unavailable':'No speech engine is available. Check the tablet text-to-speech settings.',
      'voice-unavailable':'That voice is unavailable. Choose another voice or the device default.',
      'language-unavailable':'That language is unavailable. Choose an installed English voice.',
      'network':'The speech service could not connect. Try a voice labelled on device.',
    };this.change(hints[e.error]||`Speech error: ${e.error || 'unknown'}. Try the device default voice and check media volume.`);};
    this.utterance=u; // Keep a reference until completion or explicit stop.
    this.timer=this.schedule(()=>{if(epoch===this.epoch&&!started)this.change('No speech-start signal yet. Pause other voice calls, check media volume, then try another voice.');},6000);
    try { this.speech.resume?.(); this.speech.speak(u); }
    catch(error) {this.stop('Speech could not start.');throw error;}
  }
}
