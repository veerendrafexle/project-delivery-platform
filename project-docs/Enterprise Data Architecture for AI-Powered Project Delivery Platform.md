# 🧠 Single Source of Truth (SSOT) Schema

## Enterprise Data Architecture for AI-Powered Project Delivery Platform

---

# 📌 1. Introduction

The **Single Source of Truth (SSOT)** is the **core foundation** of the AI-powered project delivery platform. It defines how all project data is structured, stored, related, validated, and consumed across the entire lifecycle.

This document provides a **deep, technical, and conceptual definition** of the SSOT schema, including:

* Data model design
* Entity relationships
* Schema structure
* Governance rules
* Versioning strategy
* Traceability model
* AI interaction patterns

---

# 🎯 2. Purpose of SSOT

## Why SSOT is Critical

In traditional project delivery:

* Data exists in multiple disconnected systems
* Requirements are duplicated
* Documents are inconsistent
* Traceability is lost
* AI outputs are unreliable

---

## What SSOT Solves

| Problem              | SSOT Solution                 |
| -------------------- | ----------------------------- |
| Scattered data       | Centralized structured schema |
| Inconsistency        | Standardized data definitions |
| Lack of traceability | Relationship-driven model     |
| AI hallucination     | Structured input constraints  |
| Governance gaps      | Controlled lifecycle states   |

---

## Core Principle

> **Every piece of information must exist exactly once, and everything else must reference it.**

---

# 🧱 3. SSOT Architecture Overview

The SSOT is built as a **normalized relational + hierarchical hybrid schema**.

---

## High-Level Structure

```text
Project
 ├── Stakeholders
 ├── Inputs
 ├── Pain Points
 ├── Requirements
 │     ├── User Stories
 │     │     ├── Tasks
 │     │     ├── Test Cases
 │     ├── UX Designs
 │     ├── Technical Components
 │
 ├── Documents (BRD, URS)
 ├── Governance
 ├── Timeline
 ├── Risks
```

---

# 🧠 4. Core Design Principles

---

## 1. Normalization

* No duplicate data
* Each entity has a unique purpose

---

## 2. Referential Integrity

* All entities linked via IDs
* No orphan records

---

## 3. Version Control

* Every entity is versioned
* History is preserved

---

## 4. AI-Readable Format

* JSON-based schema
* Strict structure
* Predictable keys

---

## 5. Extensibility

* New entities can be added
* Schema evolves without breaking existing data

---

# 🧩 5. Core Entities (Deep Definition)

---

# 🏗️ 5.1 Project Entity

## Definition

The **root entity** representing the entire delivery lifecycle.

---

## Schema

```json
{
  "project_id": "string",
  "project_name": "string",
  "description": "string",
  "status": "Discovery | Design | Build | Test | Deploy",
  "created_at": "datetime",
  "updated_at": "datetime",
  "version": "string"
}
```

---

## Purpose

* Anchor for all relationships
* Context for all data
* Enables multi-project scalability

---

# 👥 5.2 Stakeholder Entity

---

## Schema

```json
{
  "stakeholder_id": "string",
  "project_id": "string",
  "name": "string",
  "role": "BA | Architect | Developer | PM",
  "responsibilities": []
}
```

---

## Purpose

* Defines ownership
* Enables governance
* Supports approval workflows

---

# 📥 5.3 Input Entity

---

## Definition

Raw discovery data.

---

## Schema

```json
{
  "input_id": "string",
  "project_id": "string",
  "type": "Transcript | SOW | RFP | Notes",
  "content": "string",
  "source": "string",
  "created_at": "datetime"
}
```

---

## Purpose

* Source of truth for all downstream processing
* Enables traceability

---

# ⚠️ 5.4 Pain Point Entity

---

## Schema

```json
{
  "pain_point_id": "string",
  "project_id": "string",
  "description": "string",
  "source_input_id": "string",
  "severity": "Low | Medium | High"
}
```

---

## Purpose

* Captures business problems
* Drives requirement creation

---

# 📋 5.5 Requirement Entity (CORE ENTITY)

---

## Definition

Central entity connecting business, design, and development.

---

## Schema

```json
{
  "requirement_id": "string",
  "project_id": "string",
  "title": "string",
  "description": "string",
  "type": "Functional | Non-Functional",
  "priority": "High | Medium | Low",
  "source_pain_point_id": "string",
  "status": "Draft | Approved | Rejected",
  "version": "string"
}
```

---

## Relationships

* Linked to Pain Points
* Parent of User Stories
* Linked to UX and Technical components

---

# 🧾 5.6 User Story Entity

---

## Schema

```json
{
  "user_story_id": "string",
  "requirement_id": "string",
  "title": "string",
  "description": "string",
  "acceptance_criteria": [],
  "status": "Draft | Approved"
}
```

---

## Purpose

* Bridges requirement → execution
* Enables agile workflows

---

# 🧪 5.7 Test Case Entity

---

## Schema

```json
{
  "test_case_id": "string",
  "user_story_id": "string",
  "title": "string",
  "steps": [],
  "expected_result": "string"
}
```

---

## Purpose

* Ensures validation
* Supports QA automation

---

# 🎨 5.8 UX Design Entity

---

## Schema

```json
{
  "design_id": "string",
  "requirement_id": "string",
  "screen_name": "string",
  "components": [],
  "figma_link": "string"
}
```

---

## Purpose

* Connects requirement → UI
* Enables design consistency

---

# 💻 5.9 Technical Component Entity

---

## Schema

```json
{
  "component_id": "string",
  "requirement_id": "string",
  "type": "Object | Field | Flow | Apex",
  "name": "string",
  "details": {}
}
```

---

## Purpose

* Defines system implementation
* Bridges requirement → code

---

# 📄 5.10 Document Entity

---

## Schema

```json
{
  "document_id": "string",
  "project_id": "string",
  "type": "BRD | URS",
  "content": "string",
  "version": "string",
  "status": "Draft | Approved"
}
```

---

## Purpose

* Stores generated outputs
* Supports version control

---

# 🧭 5.11 Governance Entity

---

## Schema

```json
{
  "governance_id": "string",
  "project_id": "string",
  "phase": "Discovery | Design | Build",
  "status": "Pending | Approved",
  "approver": "string"
}
```

---

---

# ⏱️ 5.12 Timeline Entity

---

## Schema

```json
{
  "milestone_id": "string",
  "project_id": "string",
  "name": "string",
  "due_date": "datetime",
  "status": "Pending | Completed"
}
```

---

# ⚠️ 5.13 Risk Entity

---

## Schema

```json
{
  "risk_id": "string",
  "project_id": "string",
  "description": "string",
  "impact": "High | Medium | Low",
  "mitigation": "string"
}
```

---

# 🔗 6. Relationship Model (CRITICAL)

---

## Core Mapping

```text
Input → Pain Point → Requirement → User Story → Task → Test Case
Requirement → UX Design
Requirement → Technical Component
```

---

## Relationship Rules

* One Pain Point → Many Requirements
* One Requirement → Many User Stories
* One User Story → Many Test Cases

---

# 🔄 7. Versioning Strategy

---

## Model

Each entity includes:

```json
{
  "version": "v1",
  "previous_version_id": "string"
}
```

---

## Rules

* No overwrite
* Always create new version
* Maintain history

---

# 🧠 8. AI Interaction Model

---

## Input to AI

* Structured schema only
* Context pulled via relationships

---

## Output from AI

* Must match schema exactly
* JSON enforced

---

## Validation

* Schema validation
* Business rule validation

---

# 🔐 9. Governance Rules

---

## Rules

* No requirement without pain point
* No design without requirement
* No build without approval

---

# 📊 10. Data Lifecycle

---

## Stages

```text
Created → Validated → Approved → Versioned → Archived
```

---

# 🚀 11. Scalability Design

---

## Future Extensions

* Multi-project linking
* Reusable components
* Cross-project analytics

---

# 🏁 12. Final Conclusion

The SSOT schema is:

👉 The backbone of the entire platform

It ensures:

* Consistency
* Traceability
* AI reliability
* Governance
* Scalability

---

## Final Thought

> Without SSOT, this system becomes chaos.
> With SSOT, this system becomes intelligence.

---

**End of Document**
