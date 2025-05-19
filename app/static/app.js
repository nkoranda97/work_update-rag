async function loadSenders(){
    try{
      const res = await fetch('/senders');
      if(!res.ok) throw new Error(await res.text());
      const list = await res.json();
      const sel  = document.getElementById('senderSel');
      list.forEach(s=>{
        const opt=document.createElement('option');
        opt.value=s; opt.textContent=s;
        sel.appendChild(opt);
      });
    }catch(e){console.error(e);}
  }
  
  async function run(){
    const btn=document.querySelector('button');
    btn.disabled=true; btn.textContent='Running…';
    const ansEl=document.getElementById('answer');
    const snipEl=document.getElementById('snips');
    ansEl.textContent='';
    snipEl.textContent='';
    try{
      const res=await fetch('/query',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          question: document.getElementById('q').value,
          sender: document.getElementById('senderSel').value || null,
          start:  document.getElementById('start').value ? document.getElementById('start').value+'T00:00:00+00:00': null,
          end:    document.getElementById('end').value   ? document.getElementById('end').value  +'T23:59:59+00:00': null,
          k: +document.getElementById('kslider').value
        })
      });
      if(!res.ok) throw new Error(await res.text());
      const d=await res.json();
      ansEl.textContent=d.answer;
      snipEl.innerHTML=d.snippets.map(s=>{
        const [sender, date, content] = s.split(' | ').map(part => part.trim());
        return `
          <div class="rounded-lg border border-slate-200 bg-white shadow-sm p-4">
            <div class="flex justify-between items-center mb-2">
              <span class="font-semibold text-slate-700">${sender.replace('SENDER:', '')}</span>
              <span class="text-sm font-mono text-slate-500">${date.replace('DATE:', '')}</span>
            </div>
            <div class="text-slate-700 whitespace-pre-line">${content.replace('CONTENT:', '')}</div>
          </div>
        `;
      }).join('');
    }catch(e){alert(e.message||e);}
    btn.disabled=false; btn.textContent='Ask';
  }
  
  loadSenders();
  