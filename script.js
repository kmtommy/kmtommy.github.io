"use strict";

// Korean copy lives in index.html so the full CV remains readable without JS.
const english = {
  "skip": "Skip to content",
  "name": "GyeongMin Jung",
  "name.secondary": "정경민",
  "hero.description": "I am a third-year undergraduate in Mechanical System Design Engineering at Hongik University and an undergraduate researcher at HSIR Lab. My interests are legged robotics, reinforcement learning, and learning-based robot control.",
  "contact.email": "Get in touch",
  "focus.title": "Research interests",
  "focus.legged": "Legged robotics",
  "focus.learning": "Reinforcement & imitation learning",
  "focus.control": "Robot control & interaction",
  "focus.note": "Broader interests include physical intelligence systems, robotic manipulators, quadruped robots, and wearable robots.",
  "nav.research": "Research",
  "nav.projects": "Projects",
  "nav.awards": "Awards",
  "nav.education": "Education",
  "nav.activities": "Leadership & Activities",
  "nav.skills": "Technical Skills",
  "university": "Hongik University",
  "research.role": "Undergraduate Researcher · Hongik University",
  "research.date": "Jul. 2026–Present",
  "research.advisor": "Advisor: Prof. Jaeyoung Park",
  "research.link": "Lab website",
  "research.haptic": "Haptic system design",
  "status.ongoing": "Ongoing",
  "research.haptic.body": "Responsible for mechanical design, sensor and motor selection, and basic control software development for haptic systems.",
  "research.gripper": "Gripper for diverse object geometries",
  "status.preparation": "In preparation",
  "research.gripper.body": "Preparing to build a gripper that accommodates objects of different shapes and to write a paper on this work.",
  "research.robot": "Reinforcement-learning-based robot development",
  "status.planned": "Planned",
  "research.robot.body": "Planning to build a robot inspired by Pollen Robotics' Microduck and implement motion through reinforcement learning.",
  "project.stier.title": "Autonomous driving systems",
  "project.stier.date": "Dec. 2025–Present",
  "project.stier.subtitle": "Autonomous Driving Club, Hongik University · Competition projects",
  "project.stier.1": "Designed and implemented State Managers for driving states and behavior transitions.",
  "project.stier.2": "Developed a Hybrid A* path generation algorithm.",
  "project.stier.3": "Developed ROS1-based LiDAR perception and control code and an RRT path generation module, publishing planned paths and driving states to a downstream Stanley controller.",
  "project.stier.4": "Developed ROS2-based software for the 2026 9th Kookmin University Autonomous Driving Competition and validated it in simulation. Implemented an object-oriented State Manager and an RRT path generation algorithm.",
  "project.code": "View code",
  "project.hack.label": "2026 PHYSICAL AI HACKATHON",
  "project.hack.title": "Imitation-learning-based robotic arm control",
  "project.hack.1": "Trained an imitation-learning-based visuomotor policy on image data collected from an SO-ARM101 robotic arm to recognize and grasp randomly placed target objects.",
  "project.hack.2": "Deployed the trained model for real-time robotic arm control, completing pick-and-place tasks within competition time constraints.",
  "project.gimbal.label": "COURSE PROJECT · VIBRATION AND ISOLATION SYSTEMS",
  "project.gimbal.title": "Vibration isolation for a UAV camera gimbal",
  "project.gimbal.1": "Designed a two-degree-of-freedom vibration isolation system for a DJI Phantom 4 camera gimbal, including stiffness and damping parameter selection and eigenvalue-based modal analysis.",
  "project.gimbal.2": "Verified performance through Python-based numerical simulation of time-domain response, transmissibility, and nonlinear transients.",
  "award.sim.title": "Encouragement Award",
  "award.sim.division": "Simulation Division",
  "award.hl.name": "HL FMA 2026 Autonomous Driving Competition",
  "award.sim.team": "Team Odyssey (오뒷세이) · Hongik University",
  "award.certificate": "Certificate",
  "award.finish.title": "Completion Award",
  "award.scale": "1/5-Scale Division",
  "award.finish.team": "STIER Team 2 · Hongik University",
  "award.jeju.title": "Innovation Award",
  "award.jeju.name": "5th International Collegiate EV Autonomous Driving Competition",
  "award.jeju.note": "Led RRT-based path generation for the autonomous driving system",
  "award.hack.title": "Encouragement Award",
  "award.hack.issuer": "Director of Entrepreneurship Innovation Award, National Changwon University",
  "award.hack.name": "2026 Physical AI Hackathon",
  "award.hack.host": "All Of AI / National Changwon University",
  "education.degree": "B.S. in Mechanical System Design Engineering (in progress)",
  "education.year": "Currently a third-year undergraduate",
  "education.date": "Mar. 2023–Feb. 2028 (Expected)",
  "leadership.title": "Mechanical System Design Engineering Student Council",
  "leadership.university": "Hongik University",
  "leadership.role": "Director of Administration",
  "leadership.1": "Primarily responsible for the student council's budget and accounting.",
  "leadership.2": "Supported departmental event operations and student council administration.",
  "skills.robotics": "Robotics",
  "skills.programming": "Programming & Tools",
  "skills.design": "Design",
  "skills.os": "Operating Systems",
  "contact.title": "Contact",
  "footer": "Legged robotics · Reinforcement learning · Robot control",
  "back.top": "Back to top"
};

const storageKey = "gyeongmin-cv-language";
const translatableNodes = [...document.querySelectorAll("[data-i18n]")];
const korean = new Map(translatableNodes.map((node) => [node.dataset.i18n, node.textContent]));
const languageButtons = [...document.querySelectorAll("[data-lang]")];
const descriptionNode = document.querySelector('meta[name="description"]');
const ogTitleNode = document.querySelector('meta[property="og:title"]');
const ogDescriptionNode = document.querySelector('meta[property="og:description"]');
const originalDescription = descriptionNode.content;
const originalOgDescription = ogDescriptionNode.content;

function setLanguage(language, { updateUrl = true, save = true } = {}) {
  const lang = language === "en" ? "en" : "ko";
  document.documentElement.lang = lang;
  for (const node of translatableNodes) {
    const key = node.dataset.i18n;
    node.textContent = lang === "en" ? (english[key] ?? korean.get(key)) : korean.get(key);
  }
  document.querySelector(".name-secondary").lang = lang === "en" ? "ko" : "en";
  for (const button of languageButtons) {
    button.setAttribute("aria-pressed", String(button.dataset.lang === lang));
  }
  const title = lang === "en" ? "GyeongMin Jung | Robotics & Control" : "정경민 | Robotics & Control";
  document.title = title;
  ogTitleNode.content = title;
  descriptionNode.content = lang === "en" ? english["hero.description"] : originalDescription;
  ogDescriptionNode.content = lang === "en"
    ? "Hongik University · HSIR Lab. — Research, projects, and awards."
    : originalOgDescription;
  if (save) {
    try { localStorage.setItem(storageKey, lang); } catch { /* Continue when storage is blocked. */ }
  }
  if (updateUrl) {
    try {
      const url = new URL(window.location.href);
      url.searchParams.delete("lang");
      window.history.replaceState(null, "", url);
    } catch { /* Switching also works from a downloaded local file. */ }
  }
}

function getInitialLanguage() {
  const requested = new URLSearchParams(window.location.search).get("lang");
  if (requested === "ko" || requested === "en") return requested;
  try {
    const saved = localStorage.getItem(storageKey);
    if (saved === "ko" || saved === "en") return saved;
  } catch { /* Default to Korean if storage is unavailable. */ }
  return "ko";
}

for (const button of languageButtons) {
  button.addEventListener("click", () => setLanguage(button.dataset.lang));
}
setLanguage(getInitialLanguage());
window.addEventListener("popstate", () => setLanguage(getInitialLanguage(), { updateUrl: false }));

// Mark the last section whose heading has passed the reading line.
const sections = [...document.querySelectorAll(".cv-section")];
const sectionLinks = [...document.querySelectorAll(".section-nav a")];
let scrollScheduled = false;
function updateSectionNavigation() {
  const readingLine = window.innerWidth <= 760 ? 160 : 150;
  let active = sections[0];
  for (const section of sections) {
    if (section.getBoundingClientRect().top <= readingLine) active = section;
  }
  for (const link of sectionLinks) {
    if (link.hash === `#${active.id}`) link.setAttribute("aria-current", "location");
    else link.removeAttribute("aria-current");
  }
  scrollScheduled = false;
}
window.addEventListener("scroll", () => {
  if (!scrollScheduled) {
    window.requestAnimationFrame(updateSectionNavigation);
    scrollScheduled = true;
  }
}, { passive: true });
window.addEventListener("resize", updateSectionNavigation);
updateSectionNavigation();
