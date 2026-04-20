# Privacy Impact Assessment (PIA) Template

## APGI Framework - Privacy Impact Assessment

### Document Control

- **Template Version**: 1.0
- **Last Updated**: 2024
- **Review Cycle**: Annual or upon significant system change
- **Owner**: Data Protection Officer / Privacy Team

---

## Section 1: Project Overview

### 1.1 Assessment Information

|Field|Details|
|---|---|
|**Project/System Name**||
|**PIA Reference Number**|PIA-YYYY-NNN|
|**Assessment Date**||
|**Assessment Lead**||
|**Department/Unit**||
|**Data Protection Officer**||

### 1.2 Project Description

**Provide a brief description of the project/system:**

```text
[Describe the purpose, scope, and functionality of the APGI system or feature being assessed]
```

### 1.3 Data Processing Activities

**What personal data will be processed?**

|Data Category|Description|Purpose|Legal Basis|
|---|---|---|---|
|Participant Data|Names, contact info, demographics|Research participant management|Consent / Legitimate interest|
|Experiment Data|Behavioral responses, physiological data|Scientific research|Consent|
|Health Data|Medical history, cognitive assessments|Clinical biomarker analysis|Explicit consent|
|Authentication Data|User credentials, access logs|Security and access control|Legitimate interest|
|System Logs|IP addresses, timestamps, activity logs|Security monitoring, debugging|Legitimate interest|

---

## Section 2: Data Flow Analysis

### 2.1 Data Collection

**How is personal data collected?**

|Source|Method|Data Types|Volume (approx.)|
|---|---|---|---|
|Direct user input|Web forms, GUI|Contact info, preferences||
|Automated collection|Sensors, APIs|Physiological data, behavior||
|Third-party imports|Data imports|External datasets||
|System generation|Logs, analytics|Usage patterns, metadata||

### 2.2 Data Flow Diagram

```text
[Insert data flow diagram showing:]
- Collection points
- Processing stages
- Storage locations
- Transmission routes
- Deletion points
```

### 2.3 Data Storage

**Where and how is data stored?**

|Storage Type|Location|Encryption|Retention Period|
|---|---|---|---|
|Primary Database|[e.g., PostgreSQL on AWS]|At-rest: AES-256|[Duration]|
|File Storage|[e.g., Local/Cloud]|At-rest: AES-256|[Duration]|
|Backup Systems|[e.g., Offsite backup]|Encrypted|[Duration]|
|Logs|[e.g., ELK Stack]|Transport: TLS 1.3|[Duration]|
|Cache|[e.g., Redis]|Memory-only|Session|

### 2.4 Data Sharing

**Is data shared with third parties?**

|Recipient|Purpose|Data Shared|Safeguards|Agreement Type|
|---|---|---|---|---|
|Cloud Provider|Infrastructure|All data|DPA, encryption|Data Processing Agreement|
|Research Partners|Collaboration|Anonymized results|Data use agreement|Data Sharing Agreement|
|Analytics Services|Monitoring|Aggregated metrics|Anonymization|Service Agreement|

---

## Section 3: Privacy Risk Assessment

### 3.1 Risk Identification Matrix

| Risk ID | Description | Likelihood (1-5) | Impact (1-5) | Risk Score | Status |
|---------|-------------|------------------|--------------|------------|--------|
| R1 | Unauthorized access to participant health data | | | | |
| R2 | Data breach exposing research data | | | | |
| R3 | Insufficient anonymization in published results | | | | |
| R4 | Over-retention of personal data | | | | |
| R5 | Inadequate consent documentation | | | | |
| R6 | Cross-border data transfer without safeguards | | | | |
| R7 | Re-identification through data linkage | | | | |
| R8 | Insecure data disposal | | | | |

**Risk Score Calculation**: Likelihood × Impact

- 1-5: Low (Acceptable)
- 6-15: Medium (Mitigation required)
- 16-25: High (Immediate action required)

### 3.2 Detailed Risk Analysis

#### Risk R1: Unauthorized Access to Health Data

| Aspect | Assessment |
|--------|------------|
| **Description** | PHI/health data accessed by unauthorized personnel |
| **Current Controls** | Role-based access, authentication, audit logs |
| **Gaps Identified** | |
| **Residual Risk** | |
| **Mitigation Required** |

#### Risk R2: Data Breach

| Aspect | Assessment |
|--------|------------|
| **Description** | Security incident exposing personal data |
| **Current Controls** | Encryption, access controls, monitoring |
| **Gaps Identified** | |
| **Residual Risk** | |
| **Mitigation Required** |

#### Risk R3: Inadequate Anonymization

| Aspect | Assessment |
|--------|------------|
| **Description** | Published research data allows re-identification |
| **Current Controls** | k-anonymity checks, data minimization |
| **Gaps Identified** | |
| **Residual Risk** | |
| **Mitigation Required** |

---

## Section 4: Compliance Assessment

### 4.1 GDPR Requirements

| Requirement | Status | Evidence | Notes |
|-------------|--------|----------|-------|
| **Lawful Basis** | [ ] Met [ ] Partial [ ] Not Met | | |
| **Consent Management** | [ ] Met [ ] Partial [ ] Not Met | | |
| **Purpose Limitation** | [ ] Met [ ] Partial [ ] Not Met | | |
| **Data Minimization** | [ ] Met [ ] Partial [ ] Not Met | | |
| **Accuracy** | [ ] Met [ ] Partial [ ] Not Met | | |
| **Storage Limitation** | [ ] Met [ ] Partial [ ] Not Met | | |
| **Integrity/Confidentiality** | [ ] Met [ ] Partial [ ] Not Met | | |
| **Accountability** | [ ] Met [ ] Partial [ ] Not Met | | |
| **Data Protection by Design** | [ ] Met [ ] Partial [ ] Not Met | | |
| **DPIA Requirement** | [ ] Met [ ] Partial [ ] Not Met | |

### 4.2 Data Subject Rights Assessment

| Right | Implementation Status | Mechanism | Timeline |
|-------|----------------------|-----------|----------|
| **Right to Access** | [ ] Implemented [ ] Partial [ ] Not Implemented | | 30 days |
| **Right to Rectification** | [ ] Implemented [ ] Partial [ ] Not Implemented | | 30 days |
| **Right to Erasure** | [ ] Implemented [ ] Partial [ ] Not Implemented | | 30 days |
| **Right to Restriction** | [ ] Implemented [ ] Partial [ ] Not Implemented | | 30 days |
| **Right to Data Portability** | [ ] Implemented [ ] Partial [ ] Not Implemented | | 30 days |
| **Right to Object** | [ ] Implemented [ ] Partial [ ] Not Implemented | | Immediate |
| **Rights Related to Automated Decision-Making** | [ ] Implemented [ ] Partial [ ] Not Implemented | | N/A |

### 4.3 Special Category Data (Health Data)

| Requirement | Status | Controls |
|-------------|--------|----------|
| **Explicit Consent Obtained** | Yes No | |
| **Enhanced Security Measures** | Yes No | Encryption, access controls |
| **Data Protection Officer Consultation** | Yes No | |
| **Legitimate Basis Documented** | Yes No |

---

## Section 5: Technical and Organizational Measures

### 5.1 Security Measures

| Category | Measure | Implementation | Effectiveness |
|----------|---------|----------------|---------------|
| **Encryption** | Data at rest (AES-256) | [ ] Implemented [ ] Planned [ ] Not Applicable | High |
| **Encryption** | Data in transit (TLS 1.3) | [ ] Implemented [ ] Planned [ ] Not Applicable | High |
| **Access Control** | Role-based access (RBAC) | [ ] Implemented [ ] Planned [ ] Not Applicable | High |
| **Access Control** | Multi-factor authentication | [ ] Implemented [ ] Planned [ ] Not Applicable | High |
| **Access Control** | Principle of least privilege | [ ] Implemented [ ] Planned [ ] Not Applicable | Medium |
| **Monitoring** | Audit logging | [ ] Implemented [ ] Planned [ ] Not Applicable | Medium |
| **Monitoring** | Intrusion detection | [ ] Implemented [ ] Planned [ ] Not Applicable | Medium |
| **Network** | Network segmentation | [ ] Implemented [ ] Planned [ ] Not Applicable | Medium |
| **Network** | Firewall/WAF | [ ] Implemented [ ] Planned [ ] Not Applicable | Medium |
| **Operations** | Regular vulnerability scanning | [ ] Implemented [ ] Planned [ ] Not Applicable | Medium |
| **Operations** | Penetration testing | [ ] Implemented [ ] Planned [ ] Not Applicable | Medium |
| **Operations** | Security incident response plan | [ ] Implemented [ ] Planned [ ] Not Applicable | High |

### 5.2 Privacy-Enhancing Technologies

| Technology | Use Case | Status |
|------------|----------|--------|
| **Pseudonymization** | Research dataset identifiers | Implemented Planned |
| **Anonymization** | Published research data | Implemented Planned |
| **Differential Privacy** | Statistical releases | Implemented Planned |
| **k-Anonymity** | Dataset publishing | Implemented Planned |
| **Data Masking** | Non-production environments | Implemented Planned |
| **Tokenization** | Payment/identifier handling | Implemented Planned |

### 5.3 Organizational Measures

| Measure | Description | Responsible Party | Status |
|---------|-------------|-------------------|--------|
| Privacy Policy | Public-facing privacy notice | Legal/DPO | Current Needs Update |
| Consent Forms | Research participant consent | Research Team | Current Needs Update |
| Data Retention Policy | Retention and deletion rules | DPO | Current Needs Update |
| Data Breach Response Plan | Incident response procedures | Security/DPO | Current Needs Update |
| Staff Training | Privacy awareness training | HR/Security | Current Needs Update |
| Processor Agreements | Third-party DPAs | Procurement/Legal | Current Needs Update |
| Records of Processing | Article 30 documentation | DPO | Current Needs Update |

---

## Section 6: Mitigation Plan

### 6.1 Required Mitigations

| Risk ID | Mitigation Action | Priority | Owner | Target Date | Status |
|---------|-------------------|----------|-------|-------------|--------|
| | | High/Med/Low | | | Not Started In Progress Complete |
| | | | | | |
| | | | | | |

### 6.2 Implementation Roadmap

```text
Phase 1 (Immediate - 0-30 days):
- [ ] Action item 1
- [ ] Action item 2

Phase 2 (Short-term - 1-3 months):
- [ ] Action item 3
- [ ] Action item 4

Phase 3 (Medium-term - 3-6 months):
- [ ] Action item 5
- [ ] Action item 6

Phase 4 (Ongoing):
- [ ] Regular review and updates
- [ ] Continuous monitoring
```

---

## Section 7: Stakeholder Consultation

### 7.1 Consultation Record

| Stakeholder | Role | Date Consulted | Feedback | Incorporated? |
|-------------|------|----------------|----------|---------------|
| Data Protection Officer | Privacy oversight | | | Yes No N/A |
| Information Security | Security controls | | | Yes No N/A |
| Legal Counsel | Legal compliance | | | Yes No N/A |
| Research Ethics Board | Ethical review | | | Yes No N/A |
| IT Operations | Technical implementation | | | Yes No N/A |
| Research Participants | Data subjects | | | Yes No N/A |

### 7.2 DPO Opinion

**Data Protection Officer Assessment:**

```text
[DPO to provide written opinion on:
- Compliance with data protection requirements
- Acceptability of residual risks
- Recommendations for improvement
- Whether processing should proceed]
```

**DPO Signature:** _________________ **Date:** _________

---

## Section 8: Approval and Review

### 8.1 Approval

| Role | Name | Signature | Date | Decision |
|------|------|-----------|------|----------|
| Project Lead | | | | Approved Approved with Conditions Not Approved |
| Data Protection Officer | | | | Approved Approved with Conditions Not Approved |
| Security Lead | | | | Approved Approved with Conditions Not Approved |
| Legal Counsel | | | | Approved Approved with Conditions Not Approved |

### 8.2 Review Schedule

| Review Type | Frequency | Last Review | Next Review | Outcome |
|-------------|-----------|-------------|-------------|---------|
| Annual Review | 12 months | | | |
| Post-Incident Review | After security/privacy incident | N/A | | |
| Change Triggered Review | Upon significant system change | N/A | | |
| Regulatory Change Review | Upon relevant law change | N/A | | |

### 8.3 Change Log

| Version | Date | Author | Changes | Approved By |
|---------|------|--------|---------|-------------|
| 1.0 | | | Initial assessment | |
| | | | | |
| | | | | |

---

## Appendix A: Data Mapping Template

### A.1 Personal Data Inventory

| Data Element | Category | Sensitivity | Source | Processors | Retention | Deletion Method |
|--------------|----------|-------------|--------|------------|-----------|-----------------|
| | | | | Low/Med/High | | |

### A.2 Data Subject Categories

| Category | Count (approx.) | Location | Consent Status | Special Needs |
|----------|-----------------|----------|----------------|---------------|
| Research Participants | | | ⬜ Consented ⬜ Withdrawn ⬜ Pending |
| System Users | | | ⬜ Consented ⬜ Withdrawn ⬜ Pending |
| Administrative Users | | | N/A |

### A.3 Processing Activity Details

**Activity 1: [Name]**

- **Purpose**:
- **Lawful Basis**:
- **Data Subjects**:
- **Personal Data**:
- **Recipients**:
- **Retention**:
- **Security Measures**:

---

## Appendix B: Risk Scoring Guide

### Likelihood Scale

| Score | Description | Criteria |
|-------|-------------|----------|
| 1 | Rare | May occur in exceptional circumstances |
| 2 | Unlikely | Could occur but not expected |
| 3 | Possible | Might occur at some time |
| 4 | Likely | Will probably occur in most circumstances |
| 5 | Almost Certain | Expected to occur in most circumstances |

### Impact Scale

| Score | Description | Criteria (Privacy) |
|-------|-------------|-------------------|
| 1 | Insignificant | Minor inconvenience, no data exposure |
| 2 | Minor | Limited data exposure, easily remediated |
| 3 | Moderate | Significant data exposure, regulatory concern |
| 4 | Major | Extensive data exposure, regulatory breach likely |
| 5 | Catastrophic | Massive data exposure, severe regulatory/safety impact |

---

## Appendix C: Regulatory References

### GDPR (General Data Protection Regulation)

- Article 35: Data Protection Impact Assessment
- Article 36: Prior consultation
- Article 9: Processing of special categories of data

### HIPAA (if applicable)

- Security Rule (45 CFR Part 160 and Subparts A and C of Part 164)
- Privacy Rule (45 CFR Part 160 and Subparts A and E of Part 164)
- Breach Notification Rule

### Research Ethics

- Declaration of Helsinki
- Belmont Report principles
- Local IRB/Ethics Committee requirements

---

**END OF TEMPLATE**

---

## Quick Reference: When to Conduct a PIA

A PIA is **required** when:

- [ ] Processing involves systematic monitoring of publicly accessible areas on a large scale
- [ ] Processing involves large-scale sensitive data (health, genetic, biometric)
- [ ] Processing involves genetic or biometric data for identification
- [ ] Using new technologies or processes that may impact privacy
- [ ] Processing that prevents data subjects from exercising rights
- [ ] Large-scale profiling with significant effects
- [ ] Cross-border transfers to countries without adequacy decisions

A PIA is **recommended** when:

- [ ] New system or significant change to existing system
- [ ] New data sharing arrangement
- [ ] Implementation of surveillance or monitoring technology
- [ ] Processing children's data
- [ ] Using data for purposes different from collection
- [ ] Any processing that may pose high risk to individuals
