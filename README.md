# Code-Agent
Code-Agent

```

                    ┌─────────────┐
                    │ User Request│
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Planner     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Implementer │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Test Agent  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Reviewer    │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
     Security Agent  Performance Agent  Docs Agent
            │              │              │
            └──────┬───────┴───────┬──────┘
                   ▼               ▼
                Decision Agent
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
   Approve      Retry       Escalate
      │            │            │
      ▼            │            ▼
 Report Agent      └──────→ Human Review

 ```