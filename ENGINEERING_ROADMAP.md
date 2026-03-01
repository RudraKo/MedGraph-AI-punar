# MediGraph.AI Engineering Roadmap
**Architectural & System Evolution Plan**

This roadmap details 52 meaningful, atomic engineering improvements designed to take MediGraph.AI from a functional MVP to a production-grade, enterprise-ready healthcare AI platform. 

## 1. Backend Architecture & Refactoring

1. **`refactor(api): extract dependency injection container for better testability`**
   - *Why:* Currently relying purely on FastAPI `Depends`. A dedicated DI container (like `dependency-injector`) decouples business logic from the web framework, enabling true unit testing of services without mocking HTTP requests.
2. **`feat(core): implement domain events and an in-memory event bus`**
   - *Why:* Decouples the OCR pipeline, graph calculation, and scheduling. Instead of procedural calls, the OCR service emits a `PrescriptionExtracted` event that the Interaction Engine listens for, improving modularity.
3. **`refactor(domain): introduce value objects for drug nomenclatures (RxNorm)`**
   - *Why:* Strings represent drugs currently. Wrapping them in a `DrugEntity` value object centralizes validation, ontology mapping, and string normalization logic.
4. **`perf(db): implement async SQLAlchemy session management`**
   - *Why:* FastAPI is async, but synchronous SQLAlchemy blocks the event loop. Moving to `AsyncSession` prevents connection starvation under high concurrency.
5. **`refactor(repos): standardize repository base class with generic type hints`**
   - *Why:* Reduces boilerplate CRUD code across domain models and ensures a consistent interface for the data access layer.
6. **`feat(errors): implement a centralized domain-driven exception hierarchy`**
   - *Why:* Standardizes HTTP error responses (e.g., converting a domain `MedicalOntologyNotFoundError` into a consistent 404/400 JSON structure via a global exception handler).
7. **`refactor(config): migrate settings management to Pydantic BaseSettings v2`**
   - *Why:* Provides robust, type-safe environment variable parsing with support for `.env` files and hierarchical configuration validation.
8. **`feat(logging): integrate structured JSON logging (structlog)`**
   - *Why:* Standard console logs are hard to parse at scale. Emitting JSON logs with request IDs enables seamless integration with Datadog/ELK for observability.
9. **`refactor(graph): abstract NetworkX engine behind a generalized interface`**
   - *Why:* Allows the application to swap the graph engine (e.g., to Neo4j) in the future without touching the business logic calling the interaction analyzer.

## 2. Performance & Scalability Optimization

10. **`perf(cache): introduce Redis caching layer for drug interaction lookups`** [COMPLETED]
    - *Why:* Drug-drug interactions rarely change intraday. Caching the output of the interaction engine drastically reduces duplicate NetworkX traversal times.
11. **`perf(ocr): offload optical character recognition to Celery background workers`**
    - *Why:* OCR is CPU-heavy. Running it in the main FastAPI event loop blocks other requests. Celery isolates this workload.
12. **`perf(api): implement response ETag and Last-Modified headers`**
    - *Why:* Allows the frontend to avoid re-rendering or re-downloading static ontology assets or unchanged dashboard data, saving bandwidth.
13. **`perf(db): add composite indexes to high-frequency query patterns in SQLite`**
    - *Why:* Speeds up lookups on tables where queries filter by multiple fields simultaneously (e.g., patient ID + date range).
14. **`perf(frontend): implement React code-splitting and lazy-loading for heavy routes`**
    - *Why:* The Cytoscape and Recharts libraries are heavy. Loading them only when the user navigates to the dashboard reduces the initial Time-to-Interactive (TTI).
15. **`perf(graph): pre-compute static subgraphs for top 500 prescribed medications`**
    - *Why:* Pre-warming the interaction graph for the most common drugs skips real-time calculation entirely for standard prescriptions.
16. **`perf(images): compress and resize prescription uploads before passing to OCR`**
    - *Why:* Reduces memory consumption in the OpenCV pipeline and network payload size for the async workers.

## 3. Security Hardening

17. **`feat(auth): implement JWT-based authentication with opaque refresh tokens`** [COMPLETED]
    - *Why:* Secures API endpoints and manages user sessions safely without storing state in the database.
18. **`security(cors): rigidly restrict Cross-Origin Resource Sharing origins`**
    - *Why:* Prevents malicious domains from querying the MediGraph API. Wildcard `*` or broad regexes must be replaced with strict environment-configured frontend URLs.
19. **`feat(audit): implement HIPAA-compliant audit logging for PHI access`**
    - *Why:* Healthcare applications require immutable records documenting *who* accessed *which* patient's prescription data and *when*.
20. **`security(data): encrypt sensitive prescription metadata at rest (AES-256)`**
    - *Why:* SQLite stores data in plaintext by default. Key columns containing PHI must be encrypted before hitting the disk.
21. **`feat(rate-limit): integrate Redis-based rate limiting on OCR upload endpoints`**
    - *Why:* Prevents abuse of the most expensive CPU bottleneck (the image processing pipeline) via DoS attacks.
22. **`security(headers): enforce strict CSP and HSTS via middleware`**
    - *Why:* Protects the API and frontend against Man-in-the-Middle (MitM), Cross-Site Scripting (XSS), and data injection attacks.
23. **`test(sec): integrate Bandit to scan for Python security vulnerabilities`**
    - *Why:* Automates the detection of hardcoded secrets, dangerous `eval` calls, and insecure cryptographic setups in the CI pipeline.

## 4. Testing, Quality & Reliability

24. **`test(api): introduce contract testing via Schemathesis`**
    - *Why:* Automatically generates thousands of test cases based on the OpenAPI spec to ensure the FastAPI endpoints strictly respect their documented schemas.
25. **`test(e2e): implement Playwright end-to-end tests for the core upload workflow`**
    - *Why:* Validates the entire user journey from frontend file selection to dashboard rendering in a real browser environment.
26. **`test(perf): establish baseline load testing using Locust`**
    - *Why:* Quantifies how many concurrent OCR uploads the system can handle before response times degrade past acceptable SLAs.
27. **`ci(coverage): enforce 90% instruction coverage gate on master branch`**
    - *Why:* Prevents code from being merged if it isn't tested, guaranteeing high long-term stability for the clinical logic.
28. **`test(fixtures): replace hardcoded test data with dynamic FactoryBot/Faker fixtures`**
    - *Why:* Makes unit tests more robust and expressive by decoupling them from brittle, static JSON files.
29. **`test(graph): add property-based testing (Hypothesis) for the strategy pattern`**
    - *Why:* Tests edge cases in the interaction severity calculator by fuzzing the inputs, ensuring mathematical correctness under unexpected conditions.

## 5. API Expansion & Refinement

30. **`feat(api): expose bulk batch-processing endpoints for interactions`**
    - *Why:* Allows B2B integrations where hospital systems can send arrays of hundreds of prescriptions for analysis in a single network roundtrip.
31. **`refactor(api): implement API versioning via URL paths (v1/v2)`**
    - *Why:* Ensures backward compatibility for mobile apps or external integrations when schema-breaking changes are required.
32. **`feat(api): add a health-check endpoint probing deep dependencies (DB, Redis)`** [COMPLETED]
    - *Why:* Standard `/health` only checks if the web server is up. A "deep" check ensures necessary infrastructure is actually accessible for orchestrators like Kubernetes.
33. **`feat(api): implement cursor-based pagination for historical analyses`**
    - *Why:* Offset/limit pagination becomes extremely slow on large datasets. Cursors ensure fast, consistent database reads for infinite-scrolling frontends.
34. **`feat(schema): standardize envelope wrapper for JSON API responses`**
    - *Why:* Wrapping all responses in a standard `{ "data": ..., "meta": ... }` structure predictable parsing for frontend clients.

## 6. Frontend UI/UX Polish

35. **`feat(ui): implement skeleton loaders for individual dashboard widgets`**
    - *Why:* Instead of a global loading screen, rendering exact layouts using gray skeleton blocks improves perceived performance and layout stability.
36. **`fix(a11y): strictly adhere to WCAG 2.1 AA color contrast and ARIA labels`**
    - *Why:* Essential for compliance and usability; ensures visually impaired users and screen readers can interpret clinical alerts correctly.
37. **`feat(ux): add drag-and-drop reordering to the Medication Composer`**
    - *Why:* Allows users to visually organize their medication lists by priority or time of day before running the analysis.
38. **`perf(render): memoize React context providers and expensive graph components`**
    - *Why:* Prevents the heavy Cytoscape canvas from re-rendering unneccesarily when unrelated state (like a UI toggle) changes.
39. **`feat(ui): implement responsive drawer for mobile interaction details`**
    - *Why:* The current tooltip for graph interactions is difficult to use on touch devices. A bottom-sheet drawer solves this.
40. **`feat(ux): add toast notification system for transient system events`**
    - *Why:* Provides non-blocking feedback for asynchronous actions (e.g., "Schedule exported to PDF") without displacing the user's workflow.
41. **`feat(ux): implement undo/redo stack for medication edits`**
    - *Why:* Critical for complex regimens; prevents users from losing data if they accidentally delete a heavily configured drug schedule.

## 7. Documentation & Developer Experience

42. **`docs(arch): document the interaction graph heuristics using Mermaid.js`**
    - *Why:* Code comments explain *what*, architecture diagrams explain *why*. Essential for onboarding new data scientists.
43. **`docs(api): enrich OpenAPI swagger with detailed response examples and markdown`**
    - *Why:* Makes the `/docs` route a first-class citizen for frontend developers integrating the API.
44. **`chore(git): establish conventional commits and automated changelog generation`**
    - *Why:* Automates release notes and semantic versioning (`semantic-release`), professionalizing the repository maintainance.
45. **`docs(setup): containerize the local development environment using Docker Compose`**
    - *Why:* "It works on my machine" is eliminated. One command (`docker-compose up`) spins up the API, Frontend, Database, and Cache.

## 8. DevOps, CI/CD, & Infrastructure

46. **`ci(actions): configure matrix testing across multiple Python versions`**
    - *Why:* Ensures the application remains stable and deployable regardless of underlying environment changes.
47. **`build(docker): optimize Dockerfile using multi-stage builds and distroless base`**
    - *Why:* Reduces the image size by >80% and drastically lowers the attack surface by removing the shell and package managers from the final production container.
48. **`chore(deps): integrate Dependabot for automated security patching`**
    - *Why:* Software rots. Automated PRs for bumped library versions ensure the system stays secure without manual monitoring.
49. **`deploy(k8s): write basic Helm charts for production orchestration`**
    - *Why:* Standardizes deployments, config management, and secret injection for Kubernetes environments.
50. **`feat(telemetry): integrate OpenTelemetry for distributed request tracing`**
    - *Why:* Tracks a single request as it jumps from the Frontend → FastAPI → Celery Worker → Database, making complex microservice debugging trivial.
51. **`chore(lint): enforce strict typing (mypy --strict) across the core domain`**
    - *Why:* Eliminates entire classes of runtime errors (`NoneType` panics) by shifting verification to compile/lint time.
52. **`build(migrations): integrate Alembic for stateful database schema migrations`**
    - *Why:* Hardcoded SQLite tables do not scale. Alembic provides version control for the database schema, allowing safe rollbacks.
