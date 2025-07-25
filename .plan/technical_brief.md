Below is a **developer‑ready, high‑level technical brief** for the **uai** Python package. It distills the design decisions we discussed, explains how disparate frameworks are detected and wrapped, and maps every public method to the REST endpoints in your Unified Agent Interface (UAI) spec.  A developer can use this document as the blueprint for the first implementation phase.

---

## 1  | Purpose & Scope

The **uai** package provides a **thin, opinionated wrapper** that turns *any* Python‑instantiated agent—CrewAI, LangChain, LangGraph, Letta, Nomos, or future frameworks—into a single, predictable surface.
It focuses exclusively on **client‑serving concerns** (chat, streaming, task submission, progress polling, artifact retrieval). Orchestration, prompt design, and internal tool routing remain inside the upstream framework.  This mirrors CrewAI’s “crews/tasks” abstractions ([docs.crewai.com][1]) and LangChain’s `Runnable` contract ([LangChain][2]).

---

## 2  | Core Concepts & Terminology

| Term                           | Meaning                                                                                                                                                                               |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Conversational Agent**       | Supports `chat()` and/or token‑level `stream()`. Typical example: a LangChain chatbot that yields chunks via `Runnable.stream()` ([LangChain][2]).                                    |
| **Workflow Agent**             | Purely task‑oriented (`run → task_id → status → results`). E.g., a long‑running research CrewAI pipeline that emits PDFs and JSON files ([docs.crewai.com][3], [docs.crewai.com][4]). |
| **Interactive Workflow Agent** | Workflow agent that can *pause for human input* using CrewAI’s `human_input` flag or similar ([docs.crewai.com][5], [CrewAI][6]).                                                     |
| **Adapter**                    | Small class translating framework‑specific calls into UAI’s normalized interface.                                                                                                     |
| **UnifiedAgent**               | Facade returned by `wrap_agent()`; exposes only the capabilities the underlying adapter implements.                                                                                   |

---

## 3  | Public API Surface

```python
from uai import wrap_agent
agent = wrap_agent(my_framework_agent)     # auto‑detects correct adapter

# Conversational pattern
if agent.supports("chat"):
    print(agent.chat("Hello"))
    for tok in agent.stream("Tell me more"):
        ...

# Workflow pattern
if agent.supports("run"):
    tid = agent.run("Scrape 50 SEC filings")
    while agent.status(tid)["state"] != "completed":
        time.sleep(2)
    print(agent.results(tid))
```

### Capability Matrix

| UAI Method               | Conversational | Workflow | Interactive Workflow |
| ------------------------ | -------------- | -------- | -------------------- |
| `chat`                   | ✔️             | –        | –                    |
| `stream`                 | ✔️             | –        | –                    |
| `run`                    | –              | ✔️       | ✔️                   |
| `status`                 | –              | ✔️       | ✔️                   |
| `results`                | –              | ✔️       | ✔️                   |
| `artifacts`              | –              | ✔️       | ✔️                   |
| `await_prompt` / `reply` | –              | –        | ✔️                   |

---

## 4  | Adapter Discovery & Registration

### 4.1  Heuristic Detection

```python
def wrap_agent(obj):
    if hasattr(obj, "crew_agents"):                  # CrewAI Crew
        if getattr(obj, "human_input", False):
            return UnifiedAgent(CrewAIHybridAdapter(obj))
        return UnifiedAgent(CrewAIWorkflowAdapter(obj))
    if "langchain" in type(obj).__module__:
        return UnifiedAgent(LangChainChatAdapter(obj))
    if "langgraph" in type(obj).__module__:
        return UnifiedAgent(LangGraphWorkflowAdapter(obj))
    ...
```

### 4.2  Decorator Extension

Framework authors add:

```python
@uai.register_adapter(capabilities=["run","status"])
class MyCoolFrameworkAdapter(BaseAdapter):
    ...
```

---

## 5  | Adapter Responsibilities

Every adapter subclasses `BaseAdapter`:

```python
class BaseAdapter(ABC):
    framework: str
    type: str             # conversational | workflow | interactive_workflow
    capabilities: set[str]

    def chat(self, msg): ...
    def stream(self, msg): ...
    def run(self, input, **kw): ...
    def status(self, task_id): ...
    def results(self, task_id): ...
    def artifacts(self, task_id): ...
    def await_prompt(self, task_id): ...
    def reply(self, task_id, answer): ...
```

**CrewAIWorkflowAdapter**

* Calls `crew.execute()`; returns `task_id`, then polls `task.status` until `done` ([docs.crewai.com][3]).
* Normalizes each `TaskOutput` artifact to `{artifact_id,file_name,url,mime_type}` ([docs.crewai.com][4]).

**CrewAIHybridAdapter**

* Inherits the above; additionally yields `{"type":"user_prompt","message":…}` when the task hits a human‑input checkpoint ([docs.crewai.com][5]).
* Implements `reply()` by invoking the CrewAI UserInput tool channel ([CrewAI][6]).

**LangChainChatAdapter**

* Invokes `agent.invoke({"input":msg})` for `chat()`.
* Uses `agent.stream()` (or `astream()`) for `stream()`; each yielded chunk passes straight through ([LangChain][2], [LangChain][7]).

**LangGraphWorkflowAdapter**

* Submits a graph run and wraps LangGraph’s run‑id & polling API ([Medium][8], [changelog.langchain.com][9]).

---

## 6  | Artifact Normalisation

CrewAI stores paths (`relative_path`) and names ([docs.crewai.com][4]), while other frameworks may hand back raw bytes.
UAI always surfaces:

```json
{
  "artifact_id": "uuid",
  "file_name": "research.pdf",
  "url": "https://...",
  "mime_type": "application/pdf",
  "size": 893211
}
```

Adapters are free to implement presigned URLs, temp files, or in‑memory bytes as needed.

---

## 7  | Mapping to REST Endpoints

| UAI Method     | REST verb+path (from your spec)                                 |
| -------------- | --------------------------------------------------------------- |
| `chat`         | `POST /conversational/sessions/{id}/messages`                   |
| `stream`       | Same as above with *SSE or WS* transport                        |
| `run`          | `POST /workflow/tasks`                                          |
| `status`       | `GET  /workflow/tasks/{task_id}/status`                         |
| `results`      | `GET  /workflow/tasks/{task_id}/results`                        |
| `artifacts`    | `GET  /workflow/tasks/{task_id}/artifacts`                      |
| `await_prompt` | `GET  /workflow/tasks/{task_id}` (yields `pending_user_prompt`) |
| `reply`        | `POST /workflow/tasks/{task_id}/reply`                          |

This 1‑to‑1 alignment lets the same **UnifiedAgent** object back both the Python SDK **and** a future FastAPI server.

---

## 8  | Error Handling & Capability Introspection

* Unsupported methods raise `NotImplementedError` with `{"error":"capability_not_supported"}`—mirrors HTTP 501.
* `supports("stream")` checks the adapter’s capability set at runtime; clients can branch accordingly.

---

## 9  | Async & Streaming Notes

* LangChain provides token streaming via `Runnable.stream()` (sync) and `astream()` (async) ([LangChain][2]).
* CrewAI generates a final output only; adapters therefore chunk the **whole** string once for compatibility.
* REST layer should prefer **Server‑Sent Events** for simplicity; WebSockets optional for back‑pressure management.

---

## 10  | Implementation Roadmap

| Phase | Deliverables                                                                      |
| ----- | --------------------------------------------------------------------------------- |
| **0** | Repo scaffold (`uai/`, `tests/`, `examples/`).                                    |
| **1** | Core abstractions (`BaseAdapter`, `UnifiedAgent`, `wrap_agent`, capability enum). |
| **2** | **CrewAIWorkflowAdapter** + integration tests using a minimal local Crew example. |
| **3** | **LangChainChatAdapter** (chat + stream).                                         |
| **4** | **CrewAIHybridAdapter** (await\_prompt/reply).                                    |
| **5** | **LangGraphWorkflowAdapter**.                                                     |
| **6** | FastAPI reference server showcasing all endpoints with any wrapped agent.         |
| **7** | Docs site (mkdocs) and example notebooks.                                         |

---

## 11  | Extensibility & Future Work

* **Plugin registry** (`entry_points = "uai.adapters"`) lets external packages publish new adapters (e.g., Letta ([letta.com][10], [GitHub][11]) or Nomos ([Reddit][12], [LinkedIn][13])).
* Support **batch runs** (`run_many`) and **stream‑of‑tasks** once LangGraph and CrewAI mature batching APIs.
* Add **telemetry hooks** so downstream REST layer can surface metrics.

---

### References

CrewAI docs on human‑in‑the‑loop ([docs.crewai.com][5]) · CrewAI task outputs ([docs.crewai.com][3]) · LangChain streaming (`Runnable.stream`) ([LangChain][2]) · LangChain executor streaming discussion ([GitHub][14]) · LangGraph workflow fundamentals ([Medium][8]) · Letta framework overview ([letta.com][10]) · Nomos state‑machine engine overview ([Reddit][12]) · CrewAI FileReadTool (artifact meta) ([docs.crewai.com][4]) · CrewAI pause/resume flows thread ([CrewAI][6]) · CrewAI “crews” concept ([docs.crewai.com][1]) · LangChain general streaming concepts ([LangChain][7]) · LangGraph run status/streaming changelog ([changelog.langchain.com][9]) · Letta GitHub repo ([GitHub][11]) · Nomos launch article ([LinkedIn][13]) · CrewAI DirectoryReadTool example (relative paths) ([CrewAI][15])

[1]: https://docs.crewai.com/en/concepts/crews?utm_source=chatgpt.com "Crews - CrewAI Documentation"
[2]: https://python.langchain.com/docs/how_to/streaming/?utm_source=chatgpt.com "How to stream runnables | 🦜️ LangChain"
[3]: https://docs.crewai.com/en/concepts/tasks?utm_source=chatgpt.com "Tasks - CrewAI"
[4]: https://docs.crewai.com/tools/filereadtool?utm_source=chatgpt.com "File Read - CrewAI"
[5]: https://docs.crewai.com/en/learn/human-input-on-execution?utm_source=chatgpt.com "Human Input on Execution - CrewAI Documentation"
[6]: https://community.crewai.com/t/how-do-you-pause-and-resume-flows/6376?utm_source=chatgpt.com "How do you pause and resume flows? - General - CrewAI"
[7]: https://python.langchain.com/docs/concepts/streaming/?utm_source=chatgpt.com "Streaming - ️ LangChain"
[8]: https://medium.com/%40shudongai/langgraph-in-action-building-custom-ai-workflows-168ed34aa9f8?utm_source=chatgpt.com "LangGraph in Action: Building Custom AI Workflows - Medium"
[9]: https://changelog.langchain.com/announcements/reliable-streaming-and-efficient-state-management-in-langgraph?utm_source=chatgpt.com "Reliable streaming and efficient state management in LangGraph"
[10]: https://www.letta.com/?utm_source=chatgpt.com "Letta"
[11]: https://github.com/letta-ai/letta?utm_source=chatgpt.com "Letta (formerly MemGPT) is the stateful agents framework ... - GitHub"
[12]: https://www.reddit.com/r/Python/comments/1lsw6ka/we_built_an_aiagent_with_a_state_machine_instead/?utm_source=chatgpt.com "We built an AI-agent with a state machine instead of a giant prompt"
[13]: https://www.linkedin.com/posts/webappia_show-hn-introducing-our-ai-agent-powered-activity-7346896177964961792-pAwG?utm_source=chatgpt.com "Introducing NOMOS: A State-Machine Engine for LLMs - LinkedIn"
[14]: https://github.com/langchain-ai/langchain/discussions/17070?utm_source=chatgpt.com "Streaming with agent executor #17070 - GitHub"
[15]: https://community.crewai.com/t/pass-file-path-for-directoryreadtool/2744?utm_source=chatgpt.com "Pass file path for DirectoryReadTool - CrewAI Community Support"
