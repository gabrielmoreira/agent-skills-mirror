# Isolated Verification

```sh
cd ui/netclaw-visual
node --test src/dashboard/hermes-ui.test.js src/dashboard/chat-recovery.test.js src/dashboard/chat-storage.test.js src/shared/runtime-client.test.js
```

Use supported Node24.19+. Actual React component renders under JSDOM with synthetic controlled fetch and Web Crypto, no runtime/provider. Verify unknown→edit→completed, refresh/repeated observation, exact history adoption, ambiguous refusal, unchanged/cleared draft, IDs through archive and onePOST only.
