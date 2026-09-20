export const site = {
  name: "derex smp",
  homeUrl: "https://derex-smp.github.io/",
  worldMapUrl: "https://mc.longhorns.dev/map/",
  youtubeUrl: "https://www.youtube.com/hashtag/derexsmp",
};

export const navigationLinks = [
  { label: "Home", href: site.homeUrl },
  { label: "World Map", href: site.worldMapUrl },
  { label: "Members", href: "/members" },
  { label: "Wall of Shame", href: "/notbanlist" },
  { label: "Youtube", href: site.youtubeUrl },
  { label: "Legacy Rules", href: "/serverrules.html" },
] as const;
