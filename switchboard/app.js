// app.js — entry point.
//
// Reads URL params, hands them to the two panels. No DOM here; each panel
// finds its own mount points by id (see index.html).
//
// URL params:
//   ?live=1        enables polling state-switchboard.json + comms + chat.ndjson.
//                  Without it the page renders an inert shell — useful for
//                  inspecting layout without a running hook.
//   ?sid8=<id>     highlights the row matching this sid8 with a gold outline,
//                  labelling it "(this)" in the switchboard panel.
//   ?crt=1         enables the CRT/scanline overlay on load (also toggleable
//                  at runtime via the ▦ CRT button, bottom-left).

import { initSwitchboard } from './switchboard.js';
import { initChat } from './chat.js';

const params = new URLSearchParams(location.search);
const live = params.get('live') === '1' || params.has('live');
const sid8 = params.get('sid8') || null;
const crt = params.get('crt') === '1' || params.has('crt');

initSwitchboard({ live, sid8 });
initChat({ live });

// CRT mode — pure garnish. Param sets the initial state; the button toggles.
if (crt) document.body.classList.add('crt');
const crtBtn = document.getElementById('crtToggle');
if (crtBtn) {
  crtBtn.addEventListener('click', () => {
    const on = document.body.classList.toggle('crt');
    crtBtn.classList.toggle('on', on);
  });
  crtBtn.classList.toggle('on', crt);
}
