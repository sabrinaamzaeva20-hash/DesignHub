const $ = sel => document.querySelector(sel);
const statuses = ['В работе','На проверке','Завершён'];
$('#today').textContent=new Intl.DateTimeFormat('ru-RU',{day:'numeric',month:'long',year:'numeric'}).format(new Date());
const escapeHtml = value => String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function request(url,options={}) {
 const response=await fetch(url,{...options,headers:{'Content-Type':'application/json',...(options.headers||{})}});
 if(!response.ok){let detail={};try{detail=await response.json()}catch{};throw new Error(typeof detail.detail==='string'?detail.detail:'Ошибка HTTP '+response.status)}
 return response.status===204?null:response.json();
}
function showError(err){$('#message').textContent=err.message||String(err)}
async function loadProjects(){
 try{
  $('#message').textContent='';
  const items=await request('/api/projects');
  $('#total-count').textContent=items.length;
  $('#metric-total').textContent=items.length;
  $('#metric-active').textContent=items.filter(x=>x.status==='В работе').length;
  $('#metric-review').textContent=items.filter(x=>x.status==='На проверке').length;
  $('#metric-done').textContent=items.filter(x=>x.status==='Завершён').length;
  $('#projects').innerHTML=items.length?items.map(item=>
   '<tr><td>'+escapeHtml(item.name)+'<br><small>'+(item.deadline?'до '+escapeHtml(item.deadline):'Без дедлайна')+'</small></td><td>'+escapeHtml(item.client)+'</td><td>'+escapeHtml(item.category)+'</td><td><span class="badge" data-status="'+escapeHtml(item.status)+'">'+escapeHtml(item.status)+'</span></td><td><div class="actions"><select data-id="'+item.id+'" aria-label="Изменить статус">'+statuses.map(s=>'<option '+(s===item.status?'selected':'')+'>'+s+'</option>').join('')+'</select><button class="delete" data-delete="'+item.id+'" aria-label="Удалить проект">✕</button></div></td></tr>'
  ).join(''):'<tr><td colspan="5">Пока нет проектов.</td></tr>';
 }catch(err){showError(err);$('#projects').innerHTML='<tr><td colspan="5">Не удалось загрузить проекты.</td></tr>'}
}
$('#projects').addEventListener('change',async ev=>{
 const el=ev.target.closest('select[data-id]');if(!el)return;
 try{await request('/api/projects/'+el.dataset.id,{method:'PATCH',body:JSON.stringify({status:el.value})});await loadProjects()}catch(err){showError(err);await loadProjects()}
});
$('#projects').addEventListener('click',async ev=>{
 const el=ev.target.closest('button[data-delete]');if(!el||!confirm('Удалить этот проект?'))return;
 try{await request('/api/projects/'+el.dataset.delete,{method:'DELETE'});await loadProjects()}catch(err){showError(err)}
});
$('#show-form').addEventListener('click',()=>$('#project-dialog').showModal());
$('#close-dialog').addEventListener('click',()=>$('#project-dialog').close());
$('#project-form').addEventListener('submit',async ev=>{
 ev.preventDefault();const data=Object.fromEntries(new FormData(ev.target));if(!data.deadline)data.deadline=null;
 try{await request('/api/projects',{method:'POST',body:JSON.stringify(data)});$('#project-dialog').close();ev.target.reset();await loadProjects()}catch(err){showError(err)}
});
$('#estimate-form').addEventListener('submit',async ev=>{
 ev.preventDefault();$('#estimate-result').textContent='Выполняется расчёт…';
 try{
  const result=await request('/api/estimate',{method:'POST',body:JSON.stringify({category:$('#estimate-category').value,quantity:Number($('#estimate-quantity').value),urgency:$('#estimate-urgent').checked})});
  $('#estimate-result').innerHTML='Стоимость заказа: <strong>$'+result.total_usd.toFixed(2)+'</strong> · '+result.quantity+' шт. × $'+result.price_per_item_usd.toFixed(2)+(result.urgency?' (+25% за срочность)':'');
 }catch(err){$('#estimate-result').textContent='Ошибка расчёта: '+err.message}
});
$('#refresh').addEventListener('click',loadProjects);
loadProjects();
