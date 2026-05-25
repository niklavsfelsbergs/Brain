"""Throwaway probe: how does headless `claude -p` stream-json expect an
AskUserQuestion to be answered so the turn continues? Mimics backend.chat_handler.
Run, watch the printed frames. Delete after."""
import asyncio, json, uuid, sys
from pathlib import Path

BRAIN = Path(__file__).resolve().parent.parent
SID = str(uuid.uuid4())
ARGS = ["claude", "-p", "--input-format", "stream-json", "--output-format",
        "stream-json", "--include-partial-messages", "--verbose",
        "--permission-mode", "bypassPermissions", "--session-id", SID]

PROMPT = ("Use the AskUserQuestion tool right now to ask me exactly one "
          "question: 'cats or dogs?' with options 'cats' and 'dogs'. "
          "Do nothing else first.")


async def main():
    proc = await asyncio.create_subprocess_exec(
        *ARGS, cwd=str(BRAIN),
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, limit=8 * 1024 * 1024)

    async def send(obj):
        proc.stdin.write((json.dumps(obj) + "\n").encode())
        await proc.stdin.drain()

    await send({"type": "user", "message": {"role": "user", "content": PROMPT}})

    answered = False
    tool_id = None
    try:
        while True:
            raw = await asyncio.wait_for(proc.stdout.readline(), timeout=60)
            if not raw:
                print("[stdout EOF]"); break
            line = raw.decode("utf-8", "replace").strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                print("[non-json]", line[:200]); continue
            t = ev.get("type")
            # find the AskUserQuestion tool_use
            if t == "assistant":
                for b in (ev.get("message") or {}).get("content", []):
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        print(f"[tool_use] name={b.get('name')} id={b.get('id')}")
                        print("  input=", json.dumps(b.get("input"))[:400])
                        if b.get("name") == "AskUserQuestion" and not answered:
                            tool_id = b.get("id")
                    elif isinstance(b, dict) and b.get("type") == "text":
                        print("[asst text]", (b.get("text") or "")[:160])
            elif t == "result":
                print("[RESULT]", json.dumps(ev)[:300]); break
            else:
                print(f"[{t}]", json.dumps(ev)[:160])

            # once we have the tool id, answer it with a tool_result user msg
            if tool_id and not answered:
                answered = True
                ans = {"type": "user", "message": {"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": tool_id,
                     "content": "dogs"}]}}
                print(">>> sending tool_result:", json.dumps(ans)[:200])
                await send(ans)
    except asyncio.TimeoutError:
        print("[TIMEOUT waiting for stdout — turn stuck]")
    finally:
        try:
            err = await asyncio.wait_for(proc.stderr.read(4000), timeout=2)
            if err:
                print("[stderr]", err.decode("utf-8", "replace")[:1000])
        except Exception:
            pass
        try:
            proc.terminate()
        except Exception:
            pass


asyncio.run(main())
