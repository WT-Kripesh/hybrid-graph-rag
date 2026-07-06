# Info Developers Pvt. Ltd. — Internal Operations & Policy Handbook

Version: 3.4
Last Updated: March 2026
Classification: Internal Use Only

---

# 1. Company Overview

Info Developers Pvt. Ltd. (commonly referred to internally as "InfoDev") is a Nepal-based software engineering and technology outsourcing company specializing in offshore product development, enterprise modernization, AI solutions, and fintech infrastructure.

## Core Service Areas

* Offshore Product Development
* Enterprise SaaS Engineering
* Banking & Fintech Solutions
* AI/ML Systems
* DevOps & Cloud Migration
* QA Automation
* Data Engineering
* Managed Support Services

## Headquarters

New Baneshwor, Kathmandu, Nepal

## Satellite Offices

* Pokhara Delivery Center
* Lalitpur AI Lab
* Bangalore Partner Office

## Total Employees

Approx. 640 employees globally as of Q1 2026.

---

# 2. Organizational Structure

## Engineering Division

Led by the VP of Engineering.

Sub-divisions:

* Platform Engineering
* Product Delivery
* DevOps & SRE
* Data & AI
* Quality Assurance
* Information Security

## Non-Engineering Departments

* Human Resources
* Finance & Compliance
* Client Success
* Sales & Partnerships
* Procurement
* Legal

---

# 3. Work Model Policy

## Standard Work Hours

Employees are expected to work 8 hours/day excluding lunch breaks.

### Nepal Shift

9:00 AM – 6:00 PM NPT

### US Client Overlap Shift

2:00 PM – 11:00 PM NPT

### EU Client Shift

12:00 PM – 9:00 PM NPT

Employees may not switch shifts without approval from:

1. Reporting Manager
2. HRBP (HR Business Partner)

## Remote Work Policy

Employees are allowed:

* 3 remote days per week for standard teams.
* Fully remote schedules for approved offshore support units.

Employees handling:

* PCI-regulated banking systems,
* production database access,
* or classified financial datasets

must work from:

* office premises,
* or company-approved secure environments.

## VPN Requirement

Any access to:

* staging,
* production,
* or client-managed infrastructure

requires connection through the corporate VPN.

---

# 4. Leave Policy

## Annual Leave

18 paid annual leave days per calendar year.

Unused annual leave:

* may be carried over,
* but only up to 10 days.

## Sick Leave

12 days/year.

Medical certificates are mandatory if sick leave exceeds 3 consecutive working days.

## Emergency Leave

Maximum 5 days/year.

## Maternity Leave

16 weeks paid leave.

## Paternity Leave

15 working days.

---

# 5. Information Security Policy

## Password Policy

Minimum password requirements:

* 14 characters minimum
* one uppercase letter
* one lowercase letter
* one numeric character
* one special character

Passwords expire every 90 days.

Reuse restriction:

* last 5 passwords cannot be reused.

## MFA Policy

Multi-factor authentication (MFA) is mandatory for:

* VPN access
* Git repositories
* cloud dashboards
* payroll systems

## Device Compliance

Only company-managed devices may access:

* production systems,
* internal admin dashboards,
* or financial reporting systems.

Exceptions require written approval from:

* InfoSec Team
* and the CTO.

## Data Classification Levels

### Public

Marketing material and public documentation.

### Internal

Internal operational documents.

### Confidential

Client architecture, source code, financial reports.

### Restricted

Banking credentials, encryption keys, customer PII.

Restricted data may not be:

* copied to external drives,
* uploaded to public AI tools,
* or transmitted over personal email.

---

# 6. AI Usage Policy

## Approved AI Tools

The following tools are approved for internal productivity usage:

* GitHub Copilot
* OpenAI Enterprise
* Atlassian Intelligence
* Internal RAG Assistant ("Indra")

## Restricted Usage

Employees may not paste:

* customer PII,
* banking credentials,
* source code from regulated clients,
* or unreleased financial data

into external AI systems.

## Internal RAG Assistant

The internal assistant "Indra" supports:

* policy lookup,
* codebase documentation search,
* sprint summarization,
* and onboarding support.

Indra indexes:

* Confluence,
* Jira,
* GitLab wiki,
* and HR policy documents.

### Retention Policy

Indra conversation logs are retained for 180 days.

### Access Restrictions

Only employees with:

* Level-2 clearance or above
  may access client financial project repositories through Indra.

---

# 7. Engineering Standards

## Source Control

All code must be committed through GitLab.

Direct pushes to:

* main,
* master,
* or production branches

are prohibited unless:

* emergency hotfix approval is granted.

## Pull Request Requirements

Minimum:

* 1 reviewer for normal repositories
* 2 reviewers for fintech repositories

## CI/CD Rules

All repositories must include:

* automated tests,
* SAST scanning,
* dependency vulnerability checks.

Production deployments require:

* successful pipeline execution,
* and change ticket linkage.

---

# 8. Incident Response Policy

Incident severity levels:

| Severity | Description                           | Response SLA |
| -------- | ------------------------------------- | ------------ |
| Sev-1    | Production outage affecting all users | 15 minutes   |
| Sev-2    | Major functionality degradation       | 30 minutes   |
| Sev-3    | Minor issue or workaround available   | 4 hours      |
| Sev-4    | Cosmetic or low-priority issue        | Next sprint  |

## Escalation Matrix

### Sev-1 Incidents

Must notify:

* SRE Lead
* Engineering Director
* Client Success Manager
* Security Team (if data involved)

within 15 minutes.

### Postmortem Requirement

All Sev-1 and Sev-2 incidents require RCA documentation within 72 hours.

---

# 9. Infrastructure Policy

## Cloud Providers

Primary cloud platforms:

* AWS
* Azure

## Kubernetes Standards

All production workloads must run on:

* Kubernetes version 1.28+
  unless exempted by architecture review.

## Backup Policy

Critical databases:

* backed up every 6 hours,
* retained for 35 days.

Cold archive retention:

* 1 year.

---

# 10. Access Control Policy

## Access Provisioning

Access requests must be approved by:

* reporting manager,
* and system owner.

## Access Review

Quarterly access reviews are conducted by InfoSec.

## Employee Exit Policy

All access must be revoked within:

* 4 hours for involuntary exits,
* 24 hours for voluntary resignations.

---

# 11. Procurement Guidelines

Engineering purchases under USD 500:

* manager approval sufficient.

Purchases above USD 5000 require:

* Finance Director approval,
* and Procurement review.

Cloud expenditure above monthly budget by 15% triggers automatic finance audit.

---

# 12. Client Engagement Rules

## Communication Channels

Approved client communication platforms:

* Microsoft Teams
* Slack Enterprise
* Company Email

Use of personal messaging apps for client data exchange is prohibited.

## Meeting Recording

Client meetings may only be recorded:

* with explicit client consent.

---

# 13. Compliance Standards

The company maintains compliance initiatives aligned with:

* ISO 27001
* SOC 2 Type II
* PCI-DSS support practices

Fintech teams undergo:

* mandatory quarterly security training.

---

# 14. Employee Equipment Policy

## Laptop Refresh Cycle

* Engineering: every 3 years
* Design teams: every 2 years

## Standard Engineering Machine

* MacBook Pro M3
* 32 GB RAM
* 1 TB SSD

## Asset Return

Employees must return all assets within 3 working days after exit clearance.

---

# 15. Travel & Expense Policy

Domestic travel reimbursement cap:

* NPR 8,000/day excluding hotel.

International travel:

* requires VP-level approval.

Taxi reimbursements:

* only applicable for client visits,
* late-night shifts,
* or approved emergencies.

---

# 16. Business Continuity Policy

The Disaster Recovery (DR) target objectives:

| Metric | Objective  |
| ------ | ---------- |
| RPO    | 30 minutes |
| RTO    | 4 hours    |

Annual DR drills are mandatory for:

* SRE
* Platform Engineering
* InfoSec

---

# 17. Glossary

## HRBP

Human Resources Business Partner.

## RCA

Root Cause Analysis.

## SAST

Static Application Security Testing.

## RPO

Recovery Point Objective.

## RTO

Recovery Time Objective.

## Indra

Internal enterprise RAG assistant.

---

# 18. Special Exceptions

## Banking Projects

Projects categorized under:

* Tier-A Financial Systems

must comply with:

* stricter branch protection,
* 2 mandatory reviewers,
* hardware MFA keys,
* and office-only production access.

## AI Research Sandbox

The AI Lab may use:

* experimental open-source models,
* local LLM deployments,
* and non-standard GPU environments

provided:

* no production client data is used.

---

# 19. Internal Contacts

| Team           | Contact Alias                                                 |
| -------------- | ------------------------------------------------------------- |
| HR Operations  | [hr-ops@infodev.local](mailto:hr-ops@infodev.local)           |
| Security Team  | [infosec@infodev.local](mailto:infosec@infodev.local)         |
| DevOps Support | [sre-support@infodev.local](mailto:sre-support@infodev.local) |
| Procurement    | [procurement@infodev.local](mailto:procurement@infodev.local) |

---

# 20. Revision History

| Version | Date     | Notes                         |
| ------- | -------- | ----------------------------- |
| 3.1     | Aug 2025 | Added AI usage policy         |
| 3.2     | Nov 2025 | Updated DR objectives         |
| 3.3     | Jan 2026 | Revised access revocation SLA |
| 3.4     | Mar 2026 | Added Tier-A banking controls |
