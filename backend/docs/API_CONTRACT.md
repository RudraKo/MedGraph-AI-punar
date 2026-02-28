# MedSync API Contract v1

**Base URL:** `/api/v1`

**Standard Response Envelope:**

All endpoints return a uniform JSON envelope.

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

On failure:

```json
{
  "success": false,
  "data": null,
  "error": "Human-readable error description."
}
```

---

## Authentication

### POST /api/v1/auth/register

Register a new user with a specified role.

**Request Body:**

```json
{
  "full_name": "Dr. Ananya Sharma",
  "email": "ananya.sharma@clinic.in",
  "password": "SecureP@ss123",
  "role": "doctor"
}
```

| Field     | Type   | Required | Constraints                           |
| :-------- | :----- | :------- | :------------------------------------ |
| full_name | string | Yes      | 2-128 characters                      |
| email     | string | Yes      | Valid email, unique                   |
| password  | string | Yes      | Min 8 chars, 1 uppercase, 1 special   |
| role      | string | Yes      | Enum: `patient`, `doctor`, `guardian` |

**Success Response — 201 Created:**

```json
{
  "success": true,
  "data": {
    "user_id": "a3f1b2c4-5d6e-7f89-0a1b-2c3d4e5f6a7b",
    "full_name": "Dr. Ananya Sharma",
    "email": "ananya.sharma@clinic.in",
    "role": "doctor",
    "created_at": "2026-02-28T10:30:00Z"
  },
  "error": null
}
```

**Error Response — 409 Conflict:**

```json
{
  "success": false,
  "data": null,
  "error": "A user with this email already exists."
}
```

---

### POST /api/v1/auth/login

Authenticate user and return a JWT access token.

**Request Body:**

```json
{
  "email": "ananya.sharma@clinic.in",
  "password": "SecureP@ss123"
}
```

**Success Response — 200 OK:**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "user_id": "a3f1b2c4-5d6e-7f89-0a1b-2c3d4e5f6a7b",
      "role": "doctor"
    }
  },
  "error": null
}
```

**Error Response — 401 Unauthorized:**

```json
{
  "success": false,
  "data": null,
  "error": "Invalid email or password."
}
```

---

## Prescriptions

All prescription endpoints require `Authorization: Bearer <token>`.

### POST /api/v1/prescriptions

Create a new prescription for a patient. Requires `doctor` role.

**Request Body:**

```json
{
  "patient_id": "b7e2c3d4-1a2b-3c4d-5e6f-7a8b9c0d1e2f",
  "medications": [
    {
      "drug_name": "Warfarin",
      "dosage_mg": 5,
      "frequency": "once_daily",
      "duration_days": 30
    },
    {
      "drug_name": "Aspirin",
      "dosage_mg": 75,
      "frequency": "once_daily",
      "duration_days": 30
    }
  ],
  "notes": "Monitor INR weekly."
}
```

| Field                       | Type   | Required | Constraints                                       |
| :-------------------------- | :----- | :------- | :------------------------------------------------ |
| patient_id                  | string | Yes      | Valid UUIDv7                                      |
| medications                 | array  | Yes      | Min 1 item                                        |
| medications[].drug_name     | string | Yes      | Must exist in the drug registry                   |
| medications[].dosage_mg     | number | Yes      | Positive float                                    |
| medications[].frequency     | string | Yes      | Enum: `once_daily`, `twice_daily`, `thrice_daily` |
| medications[].duration_days | int    | Yes      | 1-365                                             |
| notes                       | string | No       | Max 500 characters                                |

**Success Response — 201 Created:**

```json
{
  "success": true,
  "data": {
    "prescription_id": "c8f3d4e5-2b3c-4d5e-6f7a-8b9c0d1e2f3a",
    "patient_id": "b7e2c3d4-1a2b-3c4d-5e6f-7a8b9c0d1e2f",
    "prescribed_by": "a3f1b2c4-5d6e-7f89-0a1b-2c3d4e5f6a7b",
    "medications_count": 2,
    "created_at": "2026-02-28T10:45:00Z"
  },
  "error": null
}
```

**Error Response — 403 Forbidden:**

```json
{
  "success": false,
  "data": null,
  "error": "Only users with the 'doctor' role can create prescriptions."
}
```

**Error Response — 422 Unprocessable Entity:**

```json
{
  "success": false,
  "data": null,
  "error": "Drug 'Warfarn' not found in the registry. Did you mean 'Warfarin'?"
}
```

---

### GET /api/v1/prescriptions/{prescription_id}

Retrieve a specific prescription. Accessible by the linked `patient`, the prescribing `doctor`, or an assigned `guardian`.

**Success Response — 200 OK:**

```json
{
  "success": true,
  "data": {
    "prescription_id": "c8f3d4e5-2b3c-4d5e-6f7a-8b9c0d1e2f3a",
    "patient": {
      "patient_id": "b7e2c3d4-1a2b-3c4d-5e6f-7a8b9c0d1e2f",
      "full_name": "Rajesh Patel"
    },
    "prescribed_by": {
      "doctor_id": "a3f1b2c4-5d6e-7f89-0a1b-2c3d4e5f6a7b",
      "full_name": "Dr. Ananya Sharma"
    },
    "medications": [
      {
        "drug_name": "Warfarin",
        "dosage_mg": 5,
        "frequency": "once_daily",
        "duration_days": 30
      },
      {
        "drug_name": "Aspirin",
        "dosage_mg": 75,
        "frequency": "once_daily",
        "duration_days": 30
      }
    ],
    "notes": "Monitor INR weekly.",
    "created_at": "2026-02-28T10:45:00Z"
  },
  "error": null
}
```

**Error Response — 404 Not Found:**

```json
{
  "success": false,
  "data": null,
  "error": "Prescription not found."
}
```

---

## Interaction Graph

### POST /api/v1/interactions/check

Submit a list of drugs and receive a graph-based interaction analysis. Accessible by `doctor` and `patient` roles.

**Request Body:**

```json
{
  "drugs": ["Warfarin", "Aspirin", "Metformin"]
}
```

| Field | Type  | Required | Constraints      |
| :---- | :---- | :------- | :--------------- |
| drugs | array | Yes      | Min 2 drug names |

**Success Response — 200 OK:**

```json
{
  "success": true,
  "data": {
    "total_conflicts": 1,
    "graph": {
      "nodes": [
        { "id": "Warfarin", "group": "anticoagulant" },
        { "id": "Aspirin", "group": "nsaid" },
        { "id": "Metformin", "group": "antidiabetic" }
      ],
      "edges": [
        {
          "source": "Warfarin",
          "target": "Aspirin",
          "severity": "major",
          "description": "Concurrent use significantly increases risk of gastrointestinal and intracranial hemorrhage.",
          "recommendation": "Avoid combination. If clinically necessary, monitor INR and bleeding signs closely."
        }
      ]
    }
  },
  "error": null
}
```

**Error Response — 422 Unprocessable Entity:**

```json
{
  "success": false,
  "data": null,
  "error": "A minimum of 2 drugs is required for interaction analysis."
}
```

---

### GET /api/v1/interactions/patient/{patient_id}

Generate the full interaction graph for all active medications of a specific patient.

**Success Response — 200 OK:**

```json
{
  "success": true,
  "data": {
    "patient_id": "b7e2c3d4-1a2b-3c4d-5e6f-7a8b9c0d1e2f",
    "active_medications": 4,
    "total_conflicts": 2,
    "severity_summary": {
      "major": 1,
      "moderate": 1,
      "minor": 0
    },
    "graph": {
      "nodes": [],
      "edges": []
    }
  },
  "error": null
}
```

---

## Scheduling

### POST /api/v1/schedules/generate

Generate a conflict-free medication schedule for a patient using the scheduling engine. Requires `doctor` role.

**Request Body:**

```json
{
  "patient_id": "b7e2c3d4-1a2b-3c4d-5e6f-7a8b9c0d1e2f",
  "wake_time": "07:00",
  "sleep_time": "22:00",
  "meal_times": ["08:00", "13:00", "20:00"]
}
```

| Field      | Type   | Required | Constraints                   |
| :--------- | :----- | :------- | :---------------------------- |
| patient_id | string | Yes      | Valid UUIDv7                  |
| wake_time  | string | Yes      | HH:MM format                  |
| sleep_time | string | Yes      | HH:MM format, after wake_time |
| meal_times | array  | No       | List of HH:MM strings         |

**Success Response — 200 OK:**

```json
{
  "success": true,
  "data": {
    "patient_id": "b7e2c3d4-1a2b-3c4d-5e6f-7a8b9c0d1e2f",
    "generated_at": "2026-02-28T11:00:00Z",
    "schedule": [
      {
        "time": "07:30",
        "drug": "Metformin",
        "dosage_mg": 500,
        "instruction": "Take with breakfast."
      },
      {
        "time": "08:00",
        "drug": "Warfarin",
        "dosage_mg": 5,
        "instruction": "Take on an empty stomach, 30 minutes after Metformin."
      },
      {
        "time": "20:00",
        "drug": "Aspirin",
        "dosage_mg": 75,
        "instruction": "Take with dinner. Staggered 12 hours from Warfarin to reduce bleeding risk."
      }
    ],
    "warnings": [
      "Warfarin and Aspirin are staggered due to a major interaction (hemorrhage risk)."
    ]
  },
  "error": null
}
```

**Error Response — 404 Not Found:**

```json
{
  "success": false,
  "data": null,
  "error": "No active medications found for this patient."
}
```

---

## Guardian Alerts

### POST /api/v1/alerts/guardian

Trigger an alert to all guardians linked to a patient. Can be triggered by `doctor` role or automatically by the system on a critical interaction detection.

**Request Body:**

```json
{
  "patient_id": "b7e2c3d4-1a2b-3c4d-5e6f-7a8b9c0d1e2f",
  "alert_type": "critical_interaction",
  "message": "A major drug interaction (Warfarin + Aspirin) has been detected in the patient's active prescriptions. Immediate medical review is recommended."
}
```

| Field      | Type   | Required | Constraints                                                    |
| :--------- | :----- | :------- | :------------------------------------------------------------- |
| patient_id | string | Yes      | Valid UUIDv7                                                   |
| alert_type | string | Yes      | Enum: `critical_interaction`, `missed_dose`, `schedule_update` |
| message    | string | Yes      | 10-1000 characters                                             |

**Success Response — 201 Created:**

```json
{
  "success": true,
  "data": {
    "alert_id": "d9a4e5f6-3c4d-5e6f-7a8b-9c0d1e2f3a4b",
    "patient_id": "b7e2c3d4-1a2b-3c4d-5e6f-7a8b9c0d1e2f",
    "notified_guardians": [
      {
        "guardian_id": "e0b5f6a7-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
        "full_name": "Sunita Patel",
        "delivery_method": "in_app"
      }
    ],
    "dispatched_at": "2026-02-28T11:05:00Z"
  },
  "error": null
}
```

**Error Response — 404 Not Found:**

```json
{
  "success": false,
  "data": null,
  "error": "No guardians are linked to this patient."
}
```

---

## Health Check

### GET /health

Unauthenticated endpoint to verify system availability and database connectivity.

**Success Response — 200 OK:**

```json
{
  "success": true,
  "data": {
    "status": "operational",
    "version": "1.0.0",
    "database": "connected",
    "uptime_seconds": 84210
  },
  "error": null
}
```

**Error Response — 503 Service Unavailable:**

```json
{
  "success": false,
  "data": null,
  "error": "Database connection failed."
}
```

---

## HTTP Status Code Reference

| Code | Meaning               | Usage                                           |
| :--- | :-------------------- | :---------------------------------------------- |
| 200  | OK                    | Successful read or computation                  |
| 201  | Created               | Successful resource creation                    |
| 400  | Bad Request           | Malformed JSON or missing required fields       |
| 401  | Unauthorized          | Missing or expired JWT                          |
| 403  | Forbidden             | Valid JWT but insufficient role permissions     |
| 404  | Not Found             | Resource does not exist                         |
| 409  | Conflict              | Duplicate resource (e.g., email already exists) |
| 422  | Unprocessable Entity  | Validation failure on semantically correct JSON |
| 500  | Internal Server Error | Unhandled server exception                      |
| 503  | Service Unavailable   | Database or critical dependency offline         |

---

## Authentication Header

All protected endpoints require:

```
Authorization: Bearer <access_token>
```

Tokens are obtained via `POST /api/v1/auth/login` and expire after 3600 seconds (1 hour). Clients must re-authenticate upon expiration.

---

## Role-Based Access Summary

| Endpoint                              | Patient | Doctor | Guardian |
| :------------------------------------ | :-----: | :----: | :------: |
| POST /api/v1/auth/register            |    +    |   +    |    +     |
| POST /api/v1/auth/login               |    +    |   +    |    +     |
| POST /api/v1/prescriptions            |    -    |   +    |    -     |
| GET /api/v1/prescriptions/{id}        |    +    |   +    |    +     |
| POST /api/v1/interactions/check       |    +    |   +    |    -     |
| GET /api/v1/interactions/patient/{id} |    +    |   +    |    +     |
| POST /api/v1/schedules/generate       |    -    |   +    |    -     |
| POST /api/v1/alerts/guardian          |    -    |   +    |    -     |
| GET /health                           |    +    |   +    |    +     |
