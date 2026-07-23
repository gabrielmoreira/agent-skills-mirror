// mimocode agent configuration
// Perception via mimocode Plugin SDK (@mimo-ai/plugin): event hook → HTTP POST to Clawd
// Plugin registered in ~/.config/mimocode/mimocode.jsonc "plugin" array (global scope)
//
// eventMap/capabilities are the shared opencode-family contract — identical
// for every family member, sourced from ./opencode-family so they can't drift
// (docs/plans/plan-opencode-family-shared-integration.md §3.1).

const { FAMILY_EVENT_MAP, FAMILY_CAPABILITIES } = require("./opencode-family");

module.exports = {
  id: "mimocode",
  name: "MiMo Code",
  processNames: { win: ["mimo.exe"], mac: ["mimo"], linux: ["mimo"] },
  startupRecoveryProcessNames: { win: ["mimo.exe"], mac: ["mimo"], linux: ["mimo"] },
  eventSource: "plugin-event",
  eventMap: FAMILY_EVENT_MAP,
  capabilities: FAMILY_CAPABILITIES,
  pidField: "mimocode_pid",
};
