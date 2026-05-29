# RajISG Trust Agent — architecture

```mermaid
flowchart LR
  U[User] --> ADK[ADK Web UI]
  ADK --> AG[RajISG Trust Agent\nGemini 2.5 Flash]
  AG --> T1[validate_content_credentials]
  AG --> T2[get_policy_controls]
  AG --> T3[export_compliance_evidence]
  T1 --> API[RPCA Validator API\ncontentauthenticity.rajisg.com\nCloud Run]
  T2 --> POL[EU Art. 50 + India IT Rules\nchecklist]
  T3 --> OUT[Evidence JSON\noutput/]
```

## Flow

1. User chats in ADK → agent receives file path + jurisdiction  
2. **validate_content_credentials** → POST live RPCA C2PA validator  
3. **get_policy_controls** → EU / India control library  
4. Agent maps verdict → disclosure recommendations  
5. **export_compliance_evidence** → audit JSON pack  

**Principle:** cryptographic proof first, AI reasoning second.
