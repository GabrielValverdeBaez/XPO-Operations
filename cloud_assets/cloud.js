'use strict';
const logout=document.getElementById('cloud-logout');
if(logout)logout.addEventListener('click',async()=>{if(!confirm('Cerrar sesion? Los borradores sin guardar se perderan.'))return;try{const r=await fetch('/auth/logout',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});if(r.ok||r.status===401){sessionStorage.removeItem('xpo-token');location.replace('/login');}else throw new Error('No se pudo cerrar la sesion');}catch(error){document.getElementById('notice').textContent=error.message;}});
