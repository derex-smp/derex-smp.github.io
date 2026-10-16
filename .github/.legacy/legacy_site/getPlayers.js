const IP = 'mc.longhorns.dev';

async function getServerData() {
    try {
        const response = await fetch(`https://api.mcsrvstat.us/3/${IP}`);
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

function getPlayerCount(data) { return data?.online ? `${data.players.online}/${data.players.max}` : 'Offline'; }
function getPlayerList(data) { return data?.players?.list || []; }
function getPlayerNames(data) { return data?.players?.list?.map(p => p.name) || []; }
function getMOTD(data) { return data?.motd?.clean?.[0] || ''; }
function getVersion(data) { return data?.version || 'Unknown'; }
function getIcon(data) { return data?.icon || ''; }
function isOnline(data) { return data?.online || false; }

getServerData().then(data => {
    if (data) {
        console.log('Players:', getPlayerCount(data));
        console.log('Names:', getPlayerNames(data));
        console.log('MOTD:', getMOTD(data));
        console.log('Version:', getVersion(data));
    }
});
