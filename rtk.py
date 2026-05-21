"""
RTK - Request Token Killer
PostToolUse hook: compresses tool output before it enters context.
Handles: Read, Bash, Grep, Glob, WebFetch, WebSearch
Cross-turn dedup: remembers file reads by session+path (state in rtk_state.json)
"""
import sys, json, os, hashlib, re

STATE_FILE = os.path.join(os.path.dirname(__file__), "rtk_state.json")

# Limits
READ_MAX      = 200   # lines kept from Read output
BASH_MAX      = 150   # lines kept from Bash output
BASH_HEAD     = 80
BASH_TAIL     = 50
GREP_MAX      = 80    # match lines
GLOB_MAX      = 150   # file paths
WEB_MAX       = 300   # lines from web content

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass

def truncate_head_tail(lines, head, tail, label="lines"):
    total = len(lines)
    if total <= head + tail:
        return lines
    omitted = total - head - tail
    return lines[:head] + [f"[RTK: omitted {omitted} {label}]"] + lines[total - tail:]

def compress_bash(text):
    lines = text.splitlines()
    # Deduplicate consecutive identical lines
    deduped = []
    run = 1
    for i, line in enumerate(lines):
        if i > 0 and line == lines[i - 1]:
            run += 1
        else:
            if run > 1:
                deduped.append(f"[RTK: previous line repeated {run}x]")
            deduped.append(line)
            run = 1
    if run > 1:
        deduped.append(f"[RTK: previous line repeated {run}x]")

    if len(deduped) > BASH_MAX:
        deduped = truncate_head_tail(deduped, BASH_HEAD, BASH_TAIL, "lines")

    return "\n".join(deduped)

def compress_read(text, session_id, file_path, state):
    # Cross-turn dedup
    key = f"{session_id}:{file_path}"
    content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    if key in state and state[key]["hash"] == content_hash:
        prev_turn = state[key].get("turn", "earlier")
        return f"[RTK: identical to read in turn {prev_turn} — content unchanged]"

    state[key] = {"hash": content_hash, "turn": state.get("_turn", "?")}
    save_state(state)

    lines = text.splitlines()
    if len(lines) <= READ_MAX:
        return text
    return "\n".join(truncate_head_tail(lines, 120, 60, "lines"))

def compress_grep(text):
    lines = text.splitlines()
    if len(lines) <= GREP_MAX:
        return text
    omitted = len(lines) - GREP_MAX
    return "\n".join(lines[:GREP_MAX]) + f"\n[RTK: omitted {omitted} more matches]"

def compress_glob(text):
    lines = [l for l in text.splitlines() if l.strip()]
    if len(lines) <= GLOB_MAX:
        return text
    omitted = len(lines) - GLOB_MAX
    return "\n".join(lines[:GLOB_MAX]) + f"\n[RTK: omitted {omitted} more paths]"

def compress_web(text):
    lines = text.splitlines()
    if len(lines) <= WEB_MAX:
        return text
    return "\n".join(truncate_head_tail(lines, 200, 80, "lines"))

def extract_content(response):
    """Extract text content from tool response regardless of shape."""
    if isinstance(response, str):
        return response, "str"
    if isinstance(response, dict):
        c = response.get("content", "")
        if isinstance(c, str):
            return c, "dict_str"
        if isinstance(c, list):
            # find first text block
            for block in c:
                if isinstance(block, dict) and block.get("type") == "text":
                    return block.get("text", ""), "list_text"
    return None, None

def inject_content(response, new_text, shape):
    if shape == "str":
        return new_text
    if shape == "dict_str":
        response["content"] = new_text
        return response
    if shape == "list_text":
        for block in response.get("content", []):
            if isinstance(block, dict) and block.get("type") == "text":
                block["text"] = new_text
                break
        return response
    return response

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    response = data.get("tool_response", data.get("tool_result", ""))
    session_id = data.get("session_id", "default")

    content, shape = extract_content(response)
    if content is None or len(content) < 500:
        sys.exit(0)  # too small to bother

    state = load_state()
    state.setdefault("_turn", 0)
    state["_turn"] = state["_turn"] + 1

    compressed = None

    if tool_name == "Read":
        file_path = tool_input.get("file_path", "")
        compressed = compress_read(content, session_id, file_path, state)
    elif tool_name == "Bash":
        compressed = compress_bash(content)
    elif tool_name in ("Grep",):
        compressed = compress_grep(content)
    elif tool_name in ("Glob",):
        compressed = compress_glob(content)
    elif tool_name in ("WebFetch", "WebSearch"):
        compressed = compress_web(content)

    if compressed is None or compressed == content:
        sys.exit(0)

    saved = len(content) - len(compressed)
    pct = int(saved / len(content) * 100)
    if pct < 5:
        sys.exit(0)  # not worth it

    new_response = inject_content(response, compressed, shape)
    print(json.dumps({"tool_response": new_response}))

if __name__ == "__main__":
    main()
