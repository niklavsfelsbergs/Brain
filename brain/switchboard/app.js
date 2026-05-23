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

import { initSwitchboard } from './switchboard.js';
import { initChat } from './chat.js';

const params = new URLSearchParams(location.search);
const live = params.get('live') === '1' || params.has('live');
const sid8 = params.get('sid8') || null;

initSwitchboard({ live, sid8 });
initChat({ live });
