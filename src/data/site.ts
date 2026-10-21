export const site = {
  name: "derex smp",
  serverIp: "mc.longhorns.dev",
  homeUrl: "/",
  worldMapUrl: "https://mc.longhorns.dev/map/",
  youtubeUrl: "https://www.youtube.com/hashtag/derexsmp",
  rulesUrl: "/rules",
  answerOverflowUrl: "https://www.answeroverflow.com/m/763554707296878633",
};

export const navigationLinks = [
  { label: "Home", href: site.homeUrl },
  { label: "World Map", href: site.worldMapUrl },
  { label: "Players", href: "/players" },
  { label: "Disciplinary Records", href: "/notbanlist" },
  { label: "Youtube", href: site.youtubeUrl },
  { label: "Rules", href: site.rulesUrl },
] as const;
