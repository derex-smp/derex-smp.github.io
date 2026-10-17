/**
 * Generate the list of jailed players and append it onto banlist website
 */
async function fetchPunishments() {
    const response = await fetch('docs/punishments.json');
    const punishments = await response.json();
    const banlist = document.getElementById('banlist');
  
    if (!banlist) return;
  
    punishments.forEach(punishment => {
      const card = document.createElement('div');
      card.className = 'card';
  
      const img = document.createElement('img');
      img.src = `https://mc-heads.net/avatar/${punishment.uuid}/100`;
      img.alt = `${punishment.name}'s head`;
  
      const h2 = document.createElement('h2');
      h2.textContent = punishment.name;
  
      const p = document.createElement('p');
      const date = new Date(punishment.punishmentDate);
      p.textContent = `Punishment Date: ${date.toLocaleDateString()}`;
  
      card.appendChild(img);
      card.appendChild(h2);
      card.appendChild(p);
      banlist.appendChild(card);
    });
  }

/**
 * Generate the list of players and append it onto members website
 */
async function fetchMembers() {
  const memberlist = document.getElementById('memberlist');
  
  if (!memberlist) return;
  
  try {
    const response = await fetch('https://api.github.com/repos/derex-smp/derex-smp.github.io/contents/docs/playerdata');
    const files = await response.json();
    
    for (const file of files) {
      if (file.type === 'file' && !file.name.includes('_old')) {
        const uuid = file.name.replace('.dat', '').replace(/-/g, '');
        
        try {
          const formattedUuid = uuid.replace(/(.{8})(.{4})(.{4})(.{4})(.{12})/, '$1-$2-$3-$4-$5');
          const nameResponse = await fetch(`https://api.ashcon.app/mojang/v2/user/${formattedUuid}`);
          const profile = await nameResponse.json();
          
          const card = document.createElement('div');
          card.className = 'card';
          
          const img = document.createElement('img');
          img.src = `https://mc-heads.net/avatar/${uuid}/100`;
          img.alt = `${profile.username}'s head`;
          
          const h2 = document.createElement('h2');
          h2.textContent = profile.username || uuid.substring(0, 8);
          
          card.appendChild(img);
          card.appendChild(h2);
          memberlist.appendChild(card);
        } catch (err) {
          console.error(`Error fetching profile for ${uuid}:`, err);
        }
      }
    }
  } catch (error) {
    console.error('Error fetching members:', error);
  }
}
  
if (document.getElementById('banlist')) {
  fetchPunishments();
}

if (document.getElementById('memberlist')) {
  fetchMembers();
}