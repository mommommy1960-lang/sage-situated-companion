// Gradio's documented two-request API, no SDK or credentials.
export async function askText(question,{signal,fetcher=fetch}={}){
 const base='https://1queen-sage-agent-course.hf.space/gradio_api/call/ask_sage';
 const prompt='You are Sage, a text-only companion prototype. Answer clearly and briefly. Do not claim camera, microphone, location, browsing, memories or external actions. If unsure say so. RAG means Retrieval-Augmented Generation. User question: '+JSON.stringify(question);
 const response=await fetcher(base,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({data:[prompt]}),signal});
 if(!response.ok)throw new Error('Text service rejected the request');
 const {event_id}=await response.json();if(typeof event_id!=='string'||!event_id)throw new Error('Missing event ID');
 const stream=await fetcher(base+'/'+encodeURIComponent(event_id),{signal});if(!stream.ok||!stream.body)throw new Error('No response stream');
 const reader=stream.body.getReader(),decoder=new TextDecoder();let buffer='';
 try{while(true){const {done,value}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true}).replace(/\r\n/g,'\n');let split;while((split=buffer.indexOf('\n\n'))>=0){const frame=buffer.slice(0,split);buffer=buffer.slice(split+2);const event=frame.match(/^event:\s*(.+)$/m)?.[1];const data=frame.match(/^data:\s*(.+)$/m)?.[1];if(event==='error')throw new Error('Text model failed');if(event==='complete'){const result=JSON.parse(data||'null');if(typeof result?.[0]!=='string'||!result[0].trim())throw new Error('Empty model response');return result[0].trim();}}}throw new Error('Incomplete model response');}finally{await reader.cancel().catch(()=>{});}
}
