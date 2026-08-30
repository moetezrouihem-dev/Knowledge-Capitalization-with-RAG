# Spring Boot backend — rag-backend

Sits between Angular and your FastAPI RAG service, per the architecture:
Angular → **Spring Boot (this)** → FastAPI (your Python RAG pipeline)

## What's here

| File | Purpose |
|---|---|
| `entity/QueryLog.java` | One row per question — the traceability/audit log |
| `repository/QueryLogRepository.java` | Spring Data JPA — save/query the log, no SQL written by hand |
| `dto/AskRequestDto.java`, `AskResponseDto.java` | What Angular actually sends/receives (kept separate from the entity on purpose) |
| `service/RagClientService.java` | Calls your FastAPI `/ask` endpoint |
| `service/QueryLogService.java` | Persists every Q&A to the database |
| `controller/AskController.java` | Exposes `POST /api/ask` for Angular |
| `config/CorsConfig.java` | Lets Angular's dev server (`:4200`) call this API (`:8080`) |
| `config/RagServiceConfig.java` | The HTTP client bean used to call FastAPI |

## Setup

You need **Maven** and **JDK 21** installed. Check with:
```bash
mvn -version
java -version
```

## Run it (quickest path — H2, zero setup)

```bash
mvn spring-boot:run
```

This starts on `http://localhost:8080` using an in-memory H2 database —
no Postgres install needed yet, just to confirm the whole chain works.

**Important: start your FastAPI service FIRST** (`uvicorn main:app --port 8001`
in your Python project), since Spring Boot calls it — if FastAPI isn't
running, `/api/ask` will fail with a connection error.

## Test it directly (before touching Angular)

```bash
curl -X POST http://localhost:8080/api/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is SFM-PQ-001?\"}"
```

You should get back the same shape of answer FastAPI gives you directly,
proxied through Spring Boot. Then check `http://localhost:8080/h2-console`
in your browser (JDBC URL: `jdbc:h2:mem:ragdb`, username `sa`, blank
password) — you should see a `QUERY_LOG` table with your question logged.

## Switch to real Postgres later

1. Install Postgres, create a database:
   ```bash
   psql -U postgres -c "CREATE DATABASE ragdb;"
   ```
2. Edit `application-postgres.properties` — set your real username/password
3. Run with the profile active:
   ```bash
   mvn spring-boot:run -Dspring-boot.run.profiles=postgres
   ```

## Known gaps (not built yet, per your project's later phases)

- No authentication/users yet — every request is anonymous
- No pagination/search on the query log — it's write-only right now
- Error handling is minimal — a FastAPI failure currently bubbles up as
  a generic 500. Worth adding a proper `@ExceptionHandler` once the
  happy path is confirmed working.
