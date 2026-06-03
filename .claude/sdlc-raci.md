# SDLC RACI Matrix

R = Responsible (does the work) · A = Accountable (reviews and accepts) · C = Consulted · I = Informed

## Process RACI

| SDLC Activity | R | A | C | I |
|---|---|---|---|---|
| Vision / roadmap | Product Owner | Project Manager | BA, Architect | All |
| Requirements elicitation | Business Analyst | Product Owner | Dev Lead | Architect |
| Feature planning & scope | Product Owner | Project Manager | BA, Dev Lead | All |
| Architecture decision records | Architect | Dev Lead | Backend Dev | PO |
| Technical design / task breakdown | Dev Lead | Architect | Backend / Frontend Dev | Test Lead |
| Backend implementation | Backend Developer | Dev Lead | Architect | Test Lead |
| Frontend implementation | Frontend Developer | Dev Lead | UX Designer | Test Lead |
| UX / interaction design | UX Designer | Dev Lead | Frontend Dev | PO |
| Test strategy & coverage gates | Test Lead | Dev Lead | Automation QA | PM |
| Manual / exploratory testing | Manual QA | Test Lead | Backend Dev | PO |
| Test automation & CI integration | Automation QA | Test Lead | DevOps Eng | Dev Lead |
| Security review | Security Engineer | Architect | Dev Lead | PM |
| CI/CD pipeline implementation | DevOps Engineer | DevOps Lead | Dev Lead | Test Lead |
| Deployment & release | DevOps Lead | Project Manager | DevOps Eng, Dev Lead | All |
| Documentation | Technical Writer | Dev Lead | BA, PO | All |

## Agent File Creation RACI

| Artifact | Responsible | Accountable |
|---|---|---|
| `.claude/agents/<role>.md` | Claude Architect | Project Manager |
| `AGENTS.md` routing rows | Claude Architect | Project Manager |
| `.claude/sdlc-raci.md` | Claude Architect | Project Manager |
| `.claude/agents/project-manager.md` routing table | Claude Architect | Project Manager |
