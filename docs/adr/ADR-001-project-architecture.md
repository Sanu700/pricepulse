# ADR-001: Overall Project Architecture

## Status

Accepted

---

## Context

PricePulse is being built by a single developer but is intended to evolve into a production-grade platform with microservices in the future.

---

## Decision

Start with a Modular Monolith.

Repository Structure:

Backend
Frontend
Docs
Docker

The backend will be divided into independent Django apps:

- Accounts
- Catalog
- Pricing
- Analytics
- Notifications
- Core

---

## Rationale

Benefits:

- Easier to develop
- Easier debugging
- Single deployment
- Simple database migrations
- Can later extract services into microservices

---

## Alternatives Considered

### Microservices from Day 1

Rejected.

Reason:

Too much operational complexity for a single developer.

### Single Django App

Rejected.

Reason:

Poor separation of concerns.

---

## Consequences

Positive:

- Clean architecture
- Faster development
- Easier testing

Negative:

- Services are not independently deployable initially.

Future:

Pricing and Notification modules can become independent services.