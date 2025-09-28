# Redis + MCP Helper (mcp-server-redis) Setup and Troubleshooting Guide

This document captures the exact steps used to make the Redis-backed MCP helper run reliably on Windows, including configuration, verification, typical errors, and fixes.

Links to key files in this repository:
- [`.roo/mcp.json`](.roo/mcp.json:1)
- [`.env`](.env:1)
- [`docker-compose.yml`](docker-compose.yml:1)

Overview

- Redis itself needs no application-level configuration beyond host, port, optional password, and DB index.
- The MCP helper package requires explicit environment variables: REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD. If any are missing, it exits with a Pydantic ValidationError.
- When launching via the MCP runner, set these variables in [`.roo/mcp.json`](.roo/mcp.json:1). When launching manually, export them in the same shell before invoking uvx.

1) Verify Redis is running and reachable

- If you use Docker Compose, the repository’s service exposes port 6379 on the host: see [`docker-compose.yml`](docker-compose.yml:48).
- Quick Windows connectivity check (PowerShell):

```powershell
Test-NetConnection -ComputerName 127.0.0.1 -Port 6379 | Select-Object TcpTestSucceeded
```

Expect TcpTestSucceeded = True. If False, ensure Docker Desktop is running and `docker-compose up -d` has started the redis service.

2) Understand what the MCP helper expects

The mcp-server-redis helper reads the following environment variables at startup (it does not parse REDIS_URL):

- REDIS_HOST (example: 127.0.0.1 for host-run, or redis when inside the Compose network)
- REDIS_PORT (example: 6379)
- REDIS_DB (example: 0)
- REDIS_PASSWORD (empty string if no auth)

If those are not present, you will see a Pydantic error like:

```text
ValidationError: 4 validation errors for RedisSettings
REDIS_HOST  Field required
REDIS_PORT  Field required
REDIS_DB    Field required
REDIS_PASSWORD Field required
```

3) Configure the MCP runner (recommended)

Edit [`.roo/mcp.json`](.roo/mcp.json:1) so the redis server entry provides the required env vars. Example (host-run):

```json
{
  "mcpServers": {
    "redis": {
      "command": "uvx",
      "args": ["mcp-server-redis", "--url", "redis://127.0.0.1:6379"],
      "env": {
        "REDIS_HOST": "127.0.0.1",
        "REDIS_PORT": "6379",
        "REDIS_DB": "0",
        "REDIS_PASSWORD": ""
      }
    }
  }
}
```

Notes:
- If the helper will run in a container with Compose, use `"REDIS_HOST": "redis"` to leverage Docker DNS inside the hmlv_net network.
- After editing, restart the MCP runner process so it reloads [`.roo/mcp.json`](.roo/mcp.json:1).

4) Ensure `.env` defines a password key (optional but consistent)

Add a password key (empty or a real secret) so the variable always exists across tooling. Example in [`.env`](.env:1):

```dotenv
# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=
```

Reminder: mcp-server-redis expects the individual REDIS_* variables; it does not read REDIS_URL. Keep REDIS_URL for app code that uses it, but make sure REDIS_HOST/PORT/DB/PASSWORD are present for the helper.

5) Launch the helper manually (alternative to runner)

Verify uvx is on PATH:

```cmd
where uvx
```

PowerShell (Windows) — set env per-process and run:

```powershell
$env:REDIS_HOST='127.0.0.1'
$env:REDIS_PORT='6379'
$env:REDIS_DB='0'
$env:REDIS_PASSWORD=''
uvx mcp-server-redis --url 'redis://127.0.0.1:6379'
```

CMD (Windows) — set env inline and run:

```cmd
set REDIS_HOST=127.0.0.1 && set REDIS_PORT=6379 && set REDIS_DB=0 && set REDIS_PASSWORD= && uvx mcp-server-redis --url redis://127.0.0.1:6379
```

Optional — capture logs to files (PowerShell):

```powershell
$p = Start-Process -FilePath 'uvx' -ArgumentList 'mcp-server-redis','--url','redis://127.0.0.1:6379' `
     -RedirectStandardOutput '.roo\mcp_redis.out.log' `
     -RedirectStandardError  '.roo\mcp_redis.err.log' `
     -NoNewWindow -PassThru
Start-Sleep -Seconds 6
if (-not $p.HasExited) { $p.Kill() }
Get-Content '.roo\mcp_redis.err.log' -Raw
```

Important: Do not redirect stdout and stderr to the same path with Start-Process; PowerShell requires different files.

6) Common errors and fixes

- Pydantic validation errors for RedisSettings (missing REDIS_*): ensure all 4 variables are present in the helper’s process environment (see sections 3 and 5).
- “Input redirection is not supported” when using cmd start with redirection: prefer PowerShell’s Start-Process or run uvx directly in the current shell.
- PowerShell parsing errors when exporting from `.env`: set variables with `Set-Item -Path Env:NAME -Value VALUE` or `$env:NAME='VALUE'`.
- Loading env from `.roo/mcp.json` in PowerShell: iterate properties via PSObject:

```powershell
$cfg = Get-Content '.roo/mcp.json' -Raw | ConvertFrom-Json
$cfg.mcpServers.redis.env.PSObject.Properties | ForEach-Object { Set-Item -Path Env:$($_.Name) -Value $_.Value }
uvx mcp-server-redis --url 'redis://127.0.0.1:6379'
```

7) Docker Compose notes

- Host access: Compose maps container port 6379 to the host: [`docker-compose.yml`](docker-compose.yml:51) → "6379:6379".
- Inside containers: use hostname `redis` (Compose service name) rather than 127.0.0.1.
- The API/worker use [`.env`](.env:1) via `env_file`; the MCP helper started on the host will not read `.env` automatically — supply env via [`.roo/mcp.json`](.roo/mcp.json:1) or your shell.

8) Validate end-to-end

- Runner flow:
  - Edit [`.roo/mcp.json`](.roo/mcp.json:1) per section 3.
  - Restart the MCP runner.
  - Confirm no ValidationError appears; the process stays running.

- Manual flow:
  - Export env in shell (section 5) and run uvx.
  - Confirm no ValidationError; if using Start-Process, stderr log is empty.

- Compose-only flow:
  - If you package the helper in a container, set `"REDIS_HOST": "redis"` and pass env via Compose.

9) Quick checklist

- [ ] Redis container is running and port 6379 is exposed on the host: [`docker-compose.yml`](docker-compose.yml:48).
- [ ] Connectivity check passes: `Test-NetConnection 127.0.0.1 -Port 6379`.
- [ ] [`.env`](.env:1) contains `REDIS_PASSWORD=` (empty or real secret).
- [ ] [`.roo/mcp.json`](.roo/mcp.json:1) has the redis server entry with REDIS_HOST/PORT/DB/PASSWORD.
- [ ] Hostname matches your context: 127.0.0.1 for host-run; redis inside Compose.
- [ ] MCP runner restarted after editing [`.roo/mcp.json`](.roo/mcp.json:1).
- [ ] Manual test succeeds: env set + `uvx mcp-server-redis --url redis://127.0.0.1:6379`.
- [ ] No Pydantic ValidationError in logs; helper runs cleanly.

Appendix: example error signature (for search)

```text
ValueError: Failed to load Redis settings: 4 validation errors for RedisSettings
REDIS_HOST ... Field required
REDIS_PORT ... Field required
REDIS_DB ... Field required
REDIS_PASSWORD ... Field required
```

That error means the helper process did not receive one or more required REDIS_* environment variables. Re-check section 3 or 5.
