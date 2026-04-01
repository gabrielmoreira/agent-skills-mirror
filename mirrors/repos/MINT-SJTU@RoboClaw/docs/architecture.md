# RoboClaw Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Interface                              │
│               CLI · Web UI · Discord · Telegram · WeChat        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼────────────────────┐   ┌───────┐
│                    Agent Runtime                   │◄─►│  LLM  │
│        Agent loop · Memory · Tool · Spawn · Lifecycle │ └───────┘
└──────────────────────────────┬────────────────────┘
                               │ Invoke skill
┌──────────────────────────────▼──────────────────────────────────┐
│                       Skill Ecosystem                           │
│                                                                 │
│  ┌──────────────┐   ┌──────────────────┐   ┌────────────────┐  │
│  │  Primitive    │   │     Skill        │   │    Policy       │  │
│  │  Body-bound   │   │  Body-agnostic,  │   │  Learned,      │  │
│  │  actions      │   │  composable      │   │  deployable    │  │
│  └──────────────┘   └──────────────────┘   └────────────────┘  │
│                                                                 │
│          Skill Hub: share · download · reuse · auto-adapt       │
└────┬─────────────────────────┬──────────────────────┬───────────┘
     │                         │                      │
     ▼                         ▼                      ▼
┌──────────────┐   ┌────────────────────┐   ┌─────────────────┐
│  Embodiment  │   │     Learning       │   │   Perception    │
│              │   │                    │   │                 │
│  Control     │   │  Data collector    │   │  Camera +       │
│   dispatch   │   │  Policy library    │   │   Detection     │
│  Embodiment  │   │  Train + Deploy    │   │  VLM scene      │
│   registry   │   │                    │   │   understanding │
│  Safety      │   │                    │   │  Spatial memory │
│   gateway    │   │                    │   │                 │
└──────┬───────┘   └─────────┬──────────┘   └────────┬────────┘
       │                     │                       │
┌──────▼─────────────────────▼───────────────────────▼────────┐
│                         Transport                           │
└─────────────┬───────────────────────────────────────────────┘
              │
       ┌──────▼──────┐            ┌──────────────┐
       │  Real World │◄──────────►│  Simulation  │
       │             │  sim-to-   │              │
       │  Robot +    │  real      │              │
       │  Sensors    │            │              │
       └──────┬──────┘            └──────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                   Embodiment Onboarding                     │
│           Zero-code: describe hardware via dialog           │
└─────────────────────────────────────────────────────────────┘
```
