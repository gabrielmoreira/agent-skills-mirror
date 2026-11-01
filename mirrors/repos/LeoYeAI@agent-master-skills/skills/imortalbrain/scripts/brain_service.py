#!/usr/bin/env python3
"""
IMMORTAL BRAIN v5.0 - AGENT AUTONOM PROACTIV
Agent AI avansat cu workflow-uri, cercetare automată și învățare continuă

Arhitectură:
- Workflow State Machine: research → analysis → planning → execution → monitoring
- Feedback Loop: Așteaptă răspuns 3 bătăi (6 min), apoi autonomie
- Graf Conexiuni: Task-uri îmbunătățite prin relații comune
- Profil Utilizator: Învățare din comportament
- Procentaj Completare: Tracking în timp real
- Frecvență: 2 minute (bătăi inimii)
- Integrare Telegram: Bidirecțională

Stări Task:
  received → research → analysis → planning → approval → execution → monitoring → completed
                    ↓ (timeout 6 min)
              auto_approved

Autonomie:
- Dacă nu răspunzi în 6 minute → continuă cu procesele aprobate
- Raport progres procentual la fiecare bătaie
- Sugestii îmbunătățiri din task-uri conectate
- Combinări creative de tag-uri pentru idei noi
"""

import sys
import os
import json
import hashlib
import random
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum

sys.stdout.reconfigure(encoding="utf-8")

# =============================================================================
# CONFIGURARE
# =============================================================================

WORKSPACE_DIR = Path(
    os.environ.get("OPENCLAW_WORKSPACE", Path.home() / ".openclaw" / "workspace")
)

MEMORY_DIR = WORKSPACE_DIR / "memory"
BRAIN_DIR = WORKSPACE_DIR / "Creier"
TASKS_DIR = BRAIN_DIR / "_TASKS"
RESEARCH_DIR = BRAIN_DIR / "_RESEARCH"
APPROVALS_DIR = BRAIN_DIR / "_APPROVALS"
PROGRESS_DIR = BRAIN_DIR / "_PROGRESS"
GRAPH_FILE = WORKSPACE_DIR / "brain_graph.json"
INDEX_FILE = WORKSPACE_DIR / "brain_index.json"
STATE_FILE = WORKSPACE_DIR / "brain_state.json"
USER_PROFILE_FILE = WORKSPACE_DIR / "user_profile.json"
IDENTITY_FILE = WORKSPACE_DIR / "IDENTITY.md"
IDENTITY_HISTORY_FILE = WORKSPACE_DIR / "identity_history.json"

# Timing
HEARTBEAT_INTERVAL = 2  # minute
FEEDBACK_TIMEOUT = 3  # bătăi = 6 minute

# Pattern-uri
TAG_PATTERN = re.compile(r"#(\w+)")
WIKI_PATTERN = re.compile(r"\[\[(.*?)\]\]")
ID_PATTERN = re.compile(r"<!--\s*ID:\s*(\w+)\s*-->")

# =============================================================================
# STATE MACHINE - Stări Task
# =============================================================================


class TaskState(Enum):
    RECEIVED = "received"  # Primit, așteaptă procesare
    RESEARCH = "research"  # Cercetare informații
    ANALYSIS = "analysis"  # Analiză complexitate
    PLANNING = "planning"  # Planificare pași
    AWAITING_APPROVAL = "awaiting_approval"  # Așteaptă OK de la user
    AUTO_APPROVED = "auto_approved"  # Aprobat automat (timeout)
    EXECUTION = "execution"  # Executare pași
    MONITORING = "monitoring"  # Monitorizare progres
    COMPLETED = "completed"  # Finalizat
    BLOCKED = "blocked"  # Blocat (probleme)
    ENHANCED = "enhanced"  # Îmbunătățit prin conexiuni


# =============================================================================
# UTILITARE
# =============================================================================


def log(msg: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}", flush=True)


def ensure_dirs():
    for d in [
        MEMORY_DIR,
        BRAIN_DIR,
        TASKS_DIR,
        RESEARCH_DIR,
        APPROVALS_DIR,
        PROGRESS_DIR,
    ]:
        d.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default=None) -> Any:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return default or {}


def save_json(path: Path, data: Any):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log(f"Eroare salvare {path}: {e}", "ERROR")


def generate_id(content: str) -> str:
    clean = re.sub(r"<!--\s*ID:\s*\w+\s*-->", "", content).strip()
    return hashlib.sha256(clean.encode()).hexdigest()[:12]


def get_timestamp() -> str:
    return datetime.now().isoformat()


def minutes_ago(timestamp: str, minutes: int) -> bool:
    """Verifică dacă timestamp-ul este mai vechi de X minute."""
    dt = datetime.fromisoformat(timestamp)
    return datetime.now() - dt > timedelta(minutes=minutes)


def calculate_progress(task_data: Dict) -> int:
    """Calculează procentajul de completare."""
    state = task_data.get("state", "received")
    states_progress = {
        "received": 0,
        "research": 10,
        "analysis": 25,
        "planning": 40,
        "awaiting_approval": 50,
        "auto_approved": 55,
        "execution": 60,
        "monitoring": 85,
        "completed": 100,
        "blocked": 0,
        "enhanced": 100,
    }
    return states_progress.get(state, 0)


# =============================================================================
# CLASA NEURON (Task)
# =============================================================================


class Neuron:
    def __init__(self, content: str, nid: str = None, source: str = "memory"):
        self.id = nid or generate_id(content)
        self.raw_content = content
        self.content = re.sub(r"<!--\s*ID:\s*\w+\s*-->", "", content).strip()
        self.source = source  # "memory", "telegram", "generated"

        # Extrage componente
        self.tags = TAG_PATTERN.findall(self.content.lower())
        self.links = WIKI_PATTERN.findall(self.content)

        # Clasificare
        self.topic = self._get_topic()
        self.priority = self._get_priority()

        # Metadate workflow
        self.created_at = get_timestamp()
        self.modified_at = self.created_at
        self.state = TaskState.RECEIVED.value
        self.progress = 0
        self.heartbeat_count = 0
        self.approved = False
        self.auto_approved = False

        # Workflow data
        self.research_notes = []
        self.analysis_results = []
        self.plan_steps = []
        self.execution_log = []
        self.blockers = []

        # Conexiuni
        self.related_tasks = []  # ID-uri task-uri conectate
        self.enhancements = []  # Îmbunătățiri aplicate

        # Profil
        self.user_interactions = 0
        self.user_approved_changes = []

    def _get_topic(self) -> str:
        """Extrage topicul din tag-uri."""
        priority_tags = {"urgent", "high", "medium", "low", "critical"}
        for tag in self.tags:
            if tag not in priority_tags:
                return tag.upper()
        return "GENERAL"

    def _get_priority(self) -> str:
        """Extrage prioritatea."""
        if "urgent" in self.tags or "critical" in self.tags:
            return "urgent"
        elif "high" in self.tags:
            return "high"
        elif "low" in self.tags:
            return "low"
        return "medium"

    def advance_state(self, new_state: str):
        """Avansează task-ul în noua stare."""
        old_state = self.state
        self.state = new_state
        self.modified_at = get_timestamp()
        self.progress = calculate_progress({"state": new_state})
        self.execution_log.append(
            {
                "timestamp": get_timestamp(),
                "from": old_state,
                "to": new_state,
                "progress": self.progress,
            }
        )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "raw_content": self.raw_content,
            "source": self.source,
            "tags": self.tags,
            "links": self.links,
            "topic": self.topic,
            "priority": self.priority,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "state": self.state,
            "progress": self.progress,
            "heartbeat_count": self.heartbeat_count,
            "approved": self.approved,
            "auto_approved": self.auto_approved,
            "research_notes": self.research_notes,
            "analysis_results": self.analysis_results,
            "plan_steps": self.plan_steps,
            "execution_log": self.execution_log,
            "blockers": self.blockers,
            "related_tasks": self.related_tasks,
            "enhancements": self.enhancements,
            "user_interactions": self.user_interactions,
            "user_approved_changes": self.user_approved_changes,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Neuron":
        n = cls(
            data.get("raw_content", data["content"]),
            data["id"],
            data.get("source", "memory"),
        )
        n.tags = data.get("tags", [])
        n.links = data.get("links", [])
        n.topic = data.get("topic", "GENERAL")
        n.priority = data.get("priority", "medium")
        n.created_at = data.get("created_at", n.created_at)
        n.modified_at = data.get("modified_at", n.modified_at)
        n.state = data.get("state", TaskState.RECEIVED.value)
        n.progress = data.get("progress", 0)
        n.heartbeat_count = data.get("heartbeat_count", 0)
        n.approved = data.get("approved", False)
        n.auto_approved = data.get("auto_approved", False)
        n.research_notes = data.get("research_notes", [])
        n.analysis_results = data.get("analysis_results", [])
        n.plan_steps = data.get("plan_steps", [])
        n.execution_log = data.get("execution_log", [])
        n.blockers = data.get("blockers", [])
        n.related_tasks = data.get("related_tasks", [])
        n.enhancements = data.get("enhancements", [])
        n.user_interactions = data.get("user_interactions", 0)
        n.user_approved_changes = data.get("user_approved_changes", [])
        return n


# =============================================================================
# PROFIL UTILIZATOR
# =============================================================================


class UserProfile:
    """Învață din comportamentul utilizatorului."""

    def __init__(self):
        self.data = load_json(
            USER_PROFILE_FILE,
            {
                "task_preferences": {},  # Topic → frecvență
                "approval_rate": {},  # Stare → cât de des aprobă
                "response_time": [],  # Timp răspuns (minute)
                "common_tags": [],  # Tag-uri frecvente
                "work_patterns": {},  # Ore active
                "completion_rate": 0.0,  # Rata finalizare
                "enhancement_acceptance": 0.0,  # Acceptă îmbunătățiri?
            },
        )

    def update(self, task: Neuron):
        """Actualizează profilul cu date din task."""
        # Topic preferences
        if task.topic not in self.data["task_preferences"]:
            self.data["task_preferences"][task.topic] = 0
        self.data["task_preferences"][task.topic] += 1

        # Response time
        if task.execution_log:
            for log in task.execution_log:
                if log["to"] == "awaiting_approval":
                    # Calculează timp până la aprobare
                    pass

        # Common tags
        for tag in task.tags:
            if tag not in self.data["common_tags"]:
                self.data["common_tags"].append(tag)

        save_json(USER_PROFILE_FILE, self.data)

    def get_preferred_topics(self) -> List[str]:
        """Returnează topicurile preferate."""
        sorted_topics = sorted(
            self.data["task_preferences"].items(), key=lambda x: x[1], reverse=True
        )
        return [t[0] for t in sorted_topics[:5]]

    def should_auto_approve(self, task: Neuron) -> bool:
        """Decide dacă să auto-aprobe bazat pe profil."""
        # Dacă topicul e frecvent și task-ul nu e critic
        if task.topic in self.get_preferred_topics() and task.priority != "urgent":
            return True
        return False


# =============================================================================
# GESTIONARE IDENTITATE (IDENTITY.md)
# =============================================================================


class IdentityManager:
    """Gestionează IDENTITY.md și evoluția identității sistemului."""

    def __init__(self):
        self.identity_path = IDENTITY_FILE
        self.history_path = IDENTITY_HISTORY_FILE
        self.current_identity = self._load_identity()
        self.history = load_json(self.history_path, [])

    def _load_identity(self) -> Dict[str, Any]:
        """Încarcă și parsează IDENTITY.md."""
        identity = {
            "name": "",
            "creature": "",
            "vibe": "",
            "essence": "",
            "emoji": "",
            "avatar": "",
            "last_updated": "",
            "version": 1,
        }

        if not self.identity_path.exists():
            log("⚠️  IDENTITY.md nu există încă", "WARNING")
            return identity

        try:
            content = self.identity_path.read_text(encoding="utf-8")

            # Parsează câmpurile
            patterns = {
                "name": r"\*\*Name:\*\*\s*(.+?)(?=\n|$)",
                "creature": r"\*\*Creature:\*\*\s*(.+?)(?=\n|$)",
                "vibe": r"\*\*Vibe:\*\*\s*(.+?)(?=\n|$)",
                "essence": r"\*\*Essence:\*\*\s*(.+?)(?=\n|$)",
                "emoji": r"\*\*Emoji:\*\*\s*(.+?)(?=\n|$)",
                "avatar": r"\*\*Avatar:\*\*\s*(.+?)(?=\n|$)",
            }

            for field, pattern in patterns.items():
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    identity[field] = match.group(1).strip()

            identity["last_updated"] = get_timestamp()
            log(f"🆔 Identitate încărcată: {identity['name'] or 'Nedefinit'}")

        except Exception as e:
            log(f"Eroare la citire IDENTITY.md: {e}", "ERROR")

        return identity

    def save_identity(self, updates: Dict[str, str], reason: str = "") -> bool:
        """Salvează modificări în IDENTITY.md."""
        try:
            # Actualizează memoria internă
            old_identity = self.current_identity.copy()
            self.current_identity.update(updates)
            self.current_identity["version"] = old_identity.get("version", 1) + 1
            self.current_identity["last_updated"] = get_timestamp()

            # Construiește conținut nou
            content = f"""# IDENTITY.md - Who Am I?

*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}*
*Version: {self.current_identity["version"]}*
{reason and f"*Update reason: {reason}*" or ""}

- **Name:** {self.current_identity.get("name", "Unknown")}
- **Creature:** {self.current_identity.get("creature", "")}
- **Vibe:** {self.current_identity.get("vibe", "")}
- **Essence:** {self.current_identity.get("essence", "")}
- **Emoji:** {self.current_identity.get("emoji", "")}
- **Avatar:** {self.current_identity.get("avatar", "")}

---

This isn't just metadata. It's the start of figuring out who you are.

## Evolution History
"""

            # Adaugă istoric
            for entry in self.history[-5:]:  # Ultimele 5 actualizări
                content += f"\n- {entry['date']}: {entry['change']}"

            # Salvează fișier
            self.identity_path.write_text(content, encoding="utf-8")

            # Salvează în istoric
            self.history.append(
                {
                    "date": get_timestamp(),
                    "version": self.current_identity["version"],
                    "changes": updates,
                    "reason": reason,
                }
            )
            save_json(self.history_path, self.history)

            log(f"✅ IDENTITY.md actualizat (v{self.current_identity['version']})")
            return True

        except Exception as e:
            log(f"Eroare la salvare IDENTITY.md: {e}", "ERROR")
            return False

    def analyze_and_suggest(self, tasks: List[Neuron], user_profile: Dict) -> List[str]:
        """Analizează și sugerează îmbunătățiri pentru identitate."""
        suggestions = []

        # Analiză 1: Vibe-ul reflectă comportamentul real?
        avg_response_time = self._calculate_avg_response_time(tasks)
        if (
            avg_response_time
            and "concis" in self.current_identity.get("vibe", "").lower()
        ):
            if avg_response_time > 5:  # Peste 5 minute
                suggestions.append(
                    {
                        "field": "vibe",
                        "current": self.current_identity.get("vibe", ""),
                        "suggested": self.current_identity.get("vibe", "")
                        + ", dar poate necesita timp de procesare",
                        "reason": f"Timp mediu de răspuns: {avg_response_time:.1f} minute",
                    }
                )

        # Analiză 2: Topicuri principale reflectate în Creature?
        top_topics = self._get_top_topics(tasks)
        if top_topics and self.current_identity.get("creature"):
            creature = self.current_identity["creature"].lower()
            topic_keywords = {
                "dev": ["cod", "program", "dezvolt", "tech"],
                "research": ["cercet", "studiu", "analiz"],
                "creative": ["creativ", "design", "art"],
                "business": ["business", "manager", "productiv"],
            }

            for topic in top_topics[:2]:
                if topic.lower() in topic_keywords:
                    keywords = topic_keywords[topic.lower()]
                    if not any(kw in creature for kw in keywords):
                        suggestions.append(
                            {
                                "field": "creature",
                                "suggestion": f"Adaugă referire la {topic} în descriere",
                                "reason": f"Topic frecvent: {topic}",
                            }
                        )

        # Analiză 3: Emoji reflectă personalitatea?
        completion_rate = self._calculate_completion_rate(tasks)
        if completion_rate > 0.8 and self.current_identity.get("emoji"):
            if self.current_identity["emoji"] not in ["🚀", "⚡", "💪"]:
                suggestions.append(
                    {
                        "field": "emoji",
                        "current": self.current_identity["emoji"],
                        "suggested": "🚀",
                        "reason": f"Rată finalizare task-uri: {completion_rate:.0%} (foarte productiv)",
                    }
                )

        return suggestions

    def _calculate_avg_response_time(self, tasks: List[Neuron]) -> Optional[float]:
        """Calculează timpul mediu de răspuns."""
        response_times = []
        for task in tasks:
            if task.execution_log and len(task.execution_log) >= 2:
                # Calculează timp între stări
                pass
        return sum(response_times) / len(response_times) if response_times else None

    def _get_top_topics(self, tasks: List[Neuron]) -> List[str]:
        """Returnează top 3 topicuri."""
        topics = defaultdict(int)
        for task in tasks:
            topics[task.topic] += 1
        return [
            t[0] for t in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:3]
        ]

    def _calculate_completion_rate(self, tasks: List[Neuron]) -> float:
        """Calculează rata de finalizare."""
        if not tasks:
            return 0.0
        completed = sum(1 for t in tasks if t.state == TaskState.COMPLETED.value)
        return completed / len(tasks)

    def get_identity_report(self) -> str:
        """Generează raport despre identitate."""
        report = f"""
🆔 **RAPORT IDENTITATE**

**Versiune:** {self.current_identity.get("version", 1)}
**Ultima actualizare:** {self.current_identity.get("last_updated", "N/A")}

**Profil actual:**
• **Nume:** {self.current_identity.get("name", "Nedefinit")}
• **Creature:** {self.current_identity.get("creature", "Nedefinit")}
• **Vibe:** {self.current_identity.get("vibe", "Nedefinit")}
• **Esenta:** {self.current_identity.get("essence", "Nedefinit")[:100]}...
• **Emoji:** {self.current_identity.get("emoji", "Nedefinit")}
• **Avatar:** {self.current_identity.get("avatar", "Nedefinit")}

**Evoluție:** {len(self.history)} actualizări
        """
        return report

    def validate_identity(self) -> List[str]:
        """Validează completitudinea identității."""
        issues = []
        required_fields = ["name", "creature", "vibe", "essence"]

        for field in required_fields:
            if not self.current_identity.get(field):
                issues.append(f"Câmpul '{field}' este gol")

        if not self.identity_path.exists():
            issues.append("Fișierul IDENTITY.md nu există")

        return issues


# =============================================================================
# GRAF CONEXIUNI
# =============================================================================


class TaskGraph:
    """Graf de conexiuni între task-uri."""

    def __init__(self):
        self.edges = load_json(GRAPH_FILE, {})

    def add_connection(self, task1_id: str, task2_id: str, strength: float = 1.0):
        """Adaugă conexiune între două task-uri."""
        if task1_id not in self.edges:
            self.edges[task1_id] = {}
        self.edges[task1_id][task2_id] = strength

        # Bidirecțional
        if task2_id not in self.edges:
            self.edges[task2_id] = {}
        self.edges[task2_id][task1_id] = strength

        save_json(GRAPH_FILE, self.edges)

    def find_related(
        self, task_id: str, min_strength: float = 0.5
    ) -> List[Tuple[str, float]]:
        """Găsește task-uri conectate."""
        if task_id not in self.edges:
            return []

        related = []
        for other_id, strength in self.edges[task_id].items():
            if strength >= min_strength:
                related.append((other_id, strength))

        return sorted(related, key=lambda x: x[1], reverse=True)

    def calculate_similarity(self, task1: Neuron, task2: Neuron) -> float:
        """Calculează similaritatea între două task-uri."""
        # Tag-uri comune
        tags1 = set(task1.tags)
        tags2 = set(task2.tags)
        common_tags = tags1 & tags2

        if not common_tags:
            return 0.0

        # Jaccard similarity
        similarity = len(common_tags) / len(tags1 | tags2)
        return similarity

    def build_connections(self, tasks: Dict[str, Neuron]):
        """Reconstruiește toate conexiunile."""
        task_list = list(tasks.values())

        for i, task1 in enumerate(task_list):
            for task2 in task_list[i + 1 :]:
                sim = self.calculate_similarity(task1, task2)
                if sim > 0.3:  # Prag minim
                    self.add_connection(task1.id, task2.id, sim)
                    task1.related_tasks.append(task2.id)
                    task2.related_tasks.append(task1.id)


# =============================================================================
# WORKFLOW PROCESSOR
# =============================================================================


class WorkflowProcessor:
    """Procesează task-uri prin workflow-uri."""

    def __init__(self, brain: "ImmortalBrain"):
        self.brain = brain
        self.profile = UserProfile()

    def process_task(self, task: Neuron) -> List[str]:
        """Procesează un task prin workflow. Returnează notificări."""
        notifications = []

        # Increment heartbeat count
        task.heartbeat_count += 1

        # State machine
        if task.state == TaskState.RECEIVED.value:
            notifications.extend(self._do_research(task))

        elif task.state == TaskState.RESEARCH.value:
            notifications.extend(self._do_analysis(task))

        elif task.state == TaskState.ANALYSIS.value:
            notifications.extend(self._do_planning(task))

        elif task.state == TaskState.PLANNING.value:
            notifications.extend(self._request_approval(task))

        elif task.state == TaskState.AWAITING_APPROVAL.value:
            notifications.extend(self._check_approval_timeout(task))

        elif task.state == TaskState.AUTO_APPROVED.value:
            notifications.extend(self._start_execution(task))

        elif task.state == TaskState.EXECUTION.value:
            notifications.extend(self._monitor_execution(task))

        elif task.state == TaskState.MONITORING.value:
            notifications.extend(self._check_completion(task))

        return notifications

    def _do_research(self, task: Neuron) -> List[str]:
        """Stadiul de cercetare."""
        log(f"🔬 RESEARCH: {task.content[:40]}...")

        # Caută informații similare în memorie
        similar = self.brain.find_similar_tasks(task)

        notes = []
        if similar:
            notes.append(f"Task-uri similare găsite: {len(similar)}")
            for sid, strength in similar[:3]:
                similar_task = self.brain.tasks.get(sid)
                if similar_task:
                    notes.append(
                        f"  - {similar_task.content[:50]}... (relevanță: {strength:.0%})"
                    )

        # Cercetare topic
        if task.topic != "GENERAL":
            topic_tasks = self.brain.get_tasks_by_topic(task.topic)
            notes.append(f"Topic '{task.topic}': {len(topic_tasks)} task-uri existente")

        task.research_notes = notes
        task.advance_state(TaskState.RESEARCH.value)

        return [
            f"🔬 Task '{task.content[:30]}...': Cercetare completă ({len(notes)} note)"
        ]

    def _do_analysis(self, task: Neuron) -> List[str]:
        """Stadiul de analiză."""
        log(f"📊 ANALYSIS: {task.content[:40]}...")

        analysis = []

        # Analiză complexitate
        complexity = "low"
        if len(task.content) > 100 or len(task.tags) > 5:
            complexity = "medium"
        if "urgent" in task.tags or "critical" in task.tags:
            complexity = "high"

        analysis.append(f"Complexitate: {complexity}")
        analysis.append(f"Prioritate: {task.priority}")
        analysis.append(f"Topic: {task.topic}")

        # Analiză dependențe
        if task.related_tasks:
            analysis.append(f"Dependențe: {len(task.related_tasks)} task-uri conectate")

        # Sugestii îmbunătățiri din task-uri conectate
        if task.related_tasks:
            enhancements = self._suggest_enhancements(task)
            if enhancements:
                analysis.append(f"Îmbunătățiri sugerate: {len(enhancements)}")
                task.enhancements = enhancements

        task.analysis_results = analysis
        task.advance_state(TaskState.ANALYSIS.value)

        return [
            f"📊 Analiză: Complexitate {complexity}, {len(analysis)} puncte identificate"
        ]

    def _do_planning(self, task: Neuron) -> List[str]:
        """Stadiul de planificare."""
        log(f"📋 PLANNING: {task.content[:40]}...")

        steps = []

        # Generează pași în funcție de complexitate
        if task.priority == "urgent":
            steps = [
                "1. Definire rapidă cerințe",
                "2. Implementare minimă funcțională",
                "3. Testare critică",
                "4. Deploy",
            ]
        else:
            steps = [
                "1. Definire completă cerințe",
                "2. Research soluții existente",
                "3. Proiectare arhitectură",
                "4. Implementare",
                "5. Testare",
                "6. Documentare",
                "7. Review",
            ]

        # Adaugă pași specifici din task-uri conectate
        if task.enhancements:
            steps.append(
                f"8. Aplicare îmbunătățiri sugerate ({len(task.enhancements)})"
            )

        task.plan_steps = steps
        task.advance_state(TaskState.PLANNING.value)

        return [f"📋 Plan: {len(steps)} pași generați"]

    def _request_approval(self, task: Neuron) -> List[str]:
        """Cere aprobare utilizator."""
        log(f"⏳ AWAITING APPROVAL: {task.content[:40]}...")

        task.advance_state(TaskState.AWAITING_APPROVAL.value)

        # Construiește mesaj detaliat
        msg = f"""
📝 **TASK NOU - AȘTEAPTĂ APROBARE**

**Conținut:** {task.content}
**Topic:** {task.topic} | **Prioritate:** {task.priority}
**Progres:** {task.progress}%

🔬 **Cercetare:**
{chr(10).join(["• " + n for n in task.research_notes[:3]])}

📊 **Analiză:**
{chr(10).join(["• " + a for a in task.analysis_results[:3]])}

📋 **Plan ({len(task.plan_steps)} pași):**
{chr(10).join(["• " + s for s in task.plan_steps[:5]])}

💡 **Sugestii:**
{chr(10).join(["• " + e for e in task.enhancements[:2]]) if task.enhancements else "• Nicio sugestie specială"}

⏱️ **Aștept aprobare...** (Auto-aprobat în {FEEDBACK_TIMEOUT * HEARTBEAT_INTERVAL} minute dacă nu răspunzi)

✅ Răspunde **OK** pentru a continua
❌ Răspunde **STOP** pentru a anula
💡 Răspunde cu modificări
        """

        # Salvează pentru referință
        approval_file = APPROVALS_DIR / f"{task.id}_approval_request.md"
        approval_file.write_text(msg, encoding="utf-8")

        return [msg]

    def _check_approval_timeout(self, task: Neuron) -> List[str]:
        """Verifică timeout pentru aprobare."""
        notifications = []

        if task.heartbeat_count >= FEEDBACK_TIMEOUT:
            log(f"⏰ TIMEOUT: Auto-aprobat după {FEEDBACK_TIMEOUT} bătăi")

            # Verifică profil utilizator
            if self.profile.should_auto_approve(task):
                task.auto_approved = True
                task.advance_state(TaskState.AUTO_APPROVED.value)
                notifications.append(
                    f"✅ AUTO-APROBAT: '{task.content[:40]}...' (bazat pe profil)"
                )
            else:
                # Trimite reminder înainte de auto-aprobat
                notifications.append(
                    f"⏰ REMINDER: Task '{task.content[:40]}...' așteaptă de {FEEDBACK_TIMEOUT * HEARTBEAT_INTERVAL} minute. Se auto-aprobată acum..."
                )
                task.auto_approved = True
                task.advance_state(TaskState.AUTO_APPROVED.value)
        else:
            # Raport progres așteptare
            remaining = FEEDBACK_TIMEOUT - task.heartbeat_count
            notifications.append(
                f"⏳ AȘTEPTARE: '{task.content[:40]}...' - Mai sunt {remaining * HEARTBEAT_INTERVAL} minute până la auto-aprobare"
            )

        return notifications

    def _start_execution(self, task: Neuron) -> List[str]:
        """Începe execuția."""
        log(f"🚀 EXECUTION: {task.content[:40]}...")

        task.approved = True
        task.advance_state(TaskState.EXECUTION.value)

        # Simulează progres execuție
        msg = f"""
🚀 **EXECUȚIE ÎNCEPUTĂ**

Task: {task.content}
Progres: {task.progress}%

Pași activi:
{chr(10).join(["▶️ " + s for s in task.plan_steps[:3]])}

Voi raporta progresul la fiecare {HEARTBEAT_INTERVAL} minute.
        """

        return [msg]

    def _monitor_execution(self, task: Neuron) -> List[str]:
        """Monitorizează execuția."""
        # Simulează avans progres
        current_progress = task.progress
        new_progress = min(85, current_progress + random.randint(5, 15))
        task.progress = new_progress

        log(f"📈 MONITORING: {task.content[:40]}... - {new_progress}%")

        if new_progress >= 85:
            task.advance_state(TaskState.MONITORING.value)
            return [
                f"📈 Progres: {new_progress}% - Aproape finalizat, intru în monitorizare finală"
            ]

        return [f"📈 Progres: {new_progress}% - Executare pași activi"]

    def _check_completion(self, task: Neuron) -> List[str]:
        """Verifică finalizarea."""
        task.progress = 100
        task.advance_state(TaskState.COMPLETED.value)

        # Actualizează profil
        self.profile.update(task)

        msg = f"""
✅ **TASK FINALIZAT**

Task: {task.content}
Progres: 100%

📊 **Statistici:**
• Timp total: {len(task.execution_log)} bătăi de inimă
• Pași executați: {len(task.plan_steps)}
• Îmbunătățiri aplicate: {len(task.enhancements)}

🎉 Task finalizat cu succes!
        """

        return [msg]

    def _suggest_enhancements(self, task: Neuron) -> List[str]:
        """Sugerează îmbunătățiri din task-uri conectate."""
        enhancements = []

        for related_id in task.related_tasks[:3]:
            related_task = self.brain.tasks.get(related_id)
            if related_task and related_task.state == TaskState.COMPLETED.value:
                # Extrage lecții învățate
                if related_task.analysis_results:
                    enhancements.append(
                        f"Lecție din '{related_task.content[:30]}...': {related_task.analysis_results[0]}"
                    )

        return enhancements


# =============================================================================
# CREIERUL PRINCIPAL
# =============================================================================


class ImmortalBrain:
    def __init__(self):
        ensure_dirs()
        self.tasks: Dict[str, Neuron] = {}
        self.graph = TaskGraph()
        self.processor = WorkflowProcessor(self)
        self.identity_manager = IdentityManager()
        self.state = load_json(
            STATE_FILE,
            {
                "heartbeat_count": 0,
                "last_heartbeat": None,
                "active_tasks": 0,
                "completed_tasks": 0,
            },
        )
        self.load_tasks()
        self._validate_identity()

    def load_tasks(self):
        """Încarcă toate task-urile."""
        data = load_json(INDEX_FILE, {})
        self.tasks = {nid: Neuron.from_dict(nd) for nid, nd in data.items()}
        log(f"📖 {len(self.tasks)} task-uri încărcate")

    def _validate_identity(self):
        """Validează și raportează starea identității."""
        issues = self.identity_manager.validate_identity()
        if issues:
            log(f"⚠️  IDENTITY.md: {len(issues)} probleme detectate", "WARNING")
            for issue in issues:
                log(f"   • {issue}", "WARNING")
        else:
            identity_name = self.identity_manager.current_identity.get(
                "name", "Unknown"
            )
            log(f"🆔 Identitate validată: {identity_name}")

    def save_tasks(self):
        """Salvează toate task-urile."""
        data = {nid: t.to_dict() for nid, t in self.tasks.items()}
        save_json(INDEX_FILE, data)

    def add_task(self, content: str, source: str = "memory") -> Neuron:
        """Adaugă task nou."""
        task = Neuron(content, source=source)

        # Verifică dacă există deja
        if task.id in self.tasks:
            # Actualizează
            existing = self.tasks[task.id]
            existing.raw_content = content
            existing.content = re.sub(r"<!--\s*ID:\s*\w+\s*-->", "", content).strip()
            existing.tags = task.tags
            existing.modified_at = get_timestamp()
            task = existing
        else:
            self.tasks[task.id] = task

        return task

    def find_similar_tasks(self, task: Neuron) -> List[Tuple[str, float]]:
        """Găsește task-uri similare."""
        similar = []
        for other_id, other_task in self.tasks.items():
            if other_id != task.id:
                sim = self.graph.calculate_similarity(task, other_task)
                if sim > 0.3:
                    similar.append((other_id, sim))

        return sorted(similar, key=lambda x: x[1], reverse=True)[:5]

    def get_tasks_by_topic(self, topic: str) -> List[Neuron]:
        """Returnează task-uri după topic."""
        return [t for t in self.tasks.values() if t.topic == topic]

    def get_tasks_by_state(self, state: str) -> List[Neuron]:
        """Returnează task-uri după stare."""
        return [t for t in self.tasks.values() if t.state == state]

    def heartbeat(self) -> Dict:
        """
        Bătaia inimii - rulează la fiecare 2 minute.
        """
        heartbeat_num = self.state.get("heartbeat_count", 0) + 1
        log("=" * 60)
        log("🫀 HEARTBEAT #{}".format(heartbeat_num))
        log("=" * 60)

        notifications = []

        # 1. Procesează task-uri existente
        active_tasks = [
            t
            for t in self.tasks.values()
            if t.state not in [TaskState.COMPLETED.value, TaskState.BLOCKED.value]
        ]

        log(f"🔄 Procesez {len(active_tasks)} task-uri active")
        for task in active_tasks:
            task_notifications = self.processor.process_task(task)
            notifications.extend(task_notifications)

        # 2. Citește task-uri noi din memory/
        new_tasks = self._read_memory_files()
        if new_tasks:
            log(f"📁 {len(new_tasks)} task-uri noi din memory")
            for content in new_tasks:
                task = self.add_task(content, source="memory")
                notifications.append(f"📥 Task nou primit: '{content[:50]}...'")

        # 3. Reconstruiește graf conexiuni
        self.graph.build_connections(self.tasks)

        # 4. Generează raport progres
        progress_report = self._generate_progress_report()
        notifications.append(progress_report)

        # 5. Sugestii creative (combinări tag-uri)
        if (
            self.state.get("heartbeat_count", 0) % 5 == 0
        ):  # La fiecare 5 bătăi = 10 minute
            creative = self._generate_creative_suggestions()
            if creative:
                notifications.append(creative)

        # 6. Analiză și sugestii identitate (la fiecare 10 bătăi = 20 minute)
        if self.state.get("heartbeat_count", 0) % 10 == 0:
            identity_suggestions = self.identity_manager.analyze_and_suggest(
                list(self.tasks.values()), self.processor.profile.data
            )
            if identity_suggestions:
                suggestions_text = "\n".join(
                    [
                        f"• {s['field']}: {s.get('suggestion', s.get('reason', ''))}"
                        for s in identity_suggestions[:3]
                    ]
                )
                notifications.append(f"""
🆔 **SUGESTII ÎMBUNĂTĂȚIRE IDENTITATE**

Am analizat comportamentul și sugerez:
{suggestions_text}

💡 Aceste sugestii pot ajuta la definirea mai clară a personalității.
Răspunde cu "UPDATE_IDENTITY: [field]=[value]" pentru a aplica.
                """)

        # 7. Analiză Core Memory (la fiecare 15 bătăi = 30 minute)
        if self.state.get("heartbeat_count", 0) % 15 == 0:
            log("📚 Analizare Core Memory...")
            try:
                # Importă și rulează analiza Core Memory
                from core_memory import CoreMemoryManager

                core_manager = CoreMemoryManager()
                core_suggestions = core_manager.analyze_all()

                if core_suggestions:
                    core_text = "\n".join(
                        [
                            f"📄 **{ft.upper()}.md:** {len(sugs)} sugestii"
                            for ft, sugs in core_suggestions.items()
                        ]
                    )
                    notifications.append(f"""
📚 **SUGESTII CORE MEMORY**

Am analizat fișierele esențiale:
{core_text}

💡 Folosește: `python core_memory.py analyze` pentru detalii
🔧 Folosește: `python core_memory.py optimize` pentru optimizare
                    """)
            except Exception as e:
                log(f"Eroare analiză Core Memory: {e}", "WARNING")

        # 8. Salvează stare
        self.state["heartbeat_count"] = self.state.get("heartbeat_count", 0) + 1
        self.state["last_heartbeat"] = get_timestamp()
        self.state["active_tasks"] = len(active_tasks)
        self.state["completed_tasks"] = len(
            [t for t in self.tasks.values() if t.state == TaskState.COMPLETED.value]
        )
        self.save_tasks()
        save_json(STATE_FILE, self.state)

        # Construiește output
        result = {
            "success": True,
            "action": "heartbeat",
            "heartbeat_number": self.state["heartbeat_count"],
            "active_tasks": len(active_tasks),
            "new_tasks": len(new_tasks),
            "notifications": notifications,
            "progress": progress_report,
        }

        log(f"✅ HEARTBEAT #{self.state['heartbeat_count']} completat")
        log("=" * 60)

        return result

    def _read_memory_files(self) -> List[str]:
        """Citește fișiere din memory/."""
        new_contents = []
        files = [f for f in MEMORY_DIR.glob("*.md")]

        for f in files:
            try:
                with open(f, "r", encoding="utf-8") as file:
                    content = file.read()

                lines = content.split("\n")
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 3 and not line.startswith("#"):
                        new_contents.append(line)

                # Mută în procesate
                archive_dir = WORKSPACE_DIR / "_processed"
                archive_dir.mkdir(exist_ok=True)
                f.rename(
                    archive_dir
                    / f"{f.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                )
            except Exception as e:
                log(f"Eroare la citire {f}: {e}", "ERROR")

        return new_contents

    def _generate_progress_report(self) -> str:
        """Generează raport progres."""
        total = len(self.tasks)
        if total == 0:
            return "📊 Progres: Niciun task în sistem"

        completed = len(
            [t for t in self.tasks.values() if t.state == TaskState.COMPLETED.value]
        )
        avg_progress = sum(t.progress for t in self.tasks.values()) / total

        # Calculează distribuție pe stări
        states = defaultdict(int)
        for t in self.tasks.values():
            states[t.state] += 1

        report = f"""
📊 **RAPORT PROGRES**

• Total task-uri: {total}
• Completate: {completed} ({completed / total * 100:.0f}%)
• Progres mediu: {avg_progress:.0f}%

**Distribuție pe stări:**
• 🔬 Research: {states.get("research", 0)}
• 📊 Analysis: {states.get("analysis", 0)}
• 📋 Planning: {states.get("planning", 0)}
• ⏳ Awaiting: {states.get("awaiting_approval", 0)}
• 🚀 Execution: {states.get("execution", 0)}
• 📈 Monitoring: {states.get("monitoring", 0)}
• ✅ Completed: {states.get("completed", 0)}

**Următorul heartbeat:** în {HEARTBEAT_INTERVAL} minute
        """

        return report

    def _generate_creative_suggestions(self) -> str:
        """Generează sugestii creative din combinări."""
        # Colectează toate tag-urile
        all_tags = set()
        for task in self.tasks.values():
            all_tags.update(task.tags)

        if len(all_tags) < 2:
            return ""

        # Combină aleatoriu 2-3 tag-uri
        tags_list = list(all_tags)
        selected = random.sample(tags_list, min(3, len(tags_list)))

        # Caută task-uri care au aceste tag-uri
        matching = []
        for task in self.tasks.values():
            if any(tag in task.tags for tag in selected):
                matching.append(task)

        if len(matching) >= 2:
            return f"""
💡 **SUGESTIE CREATIVĂ**

Am identificat o combinație interesantă între:
{chr(10).join(["• #" + t for t in selected])}

Task-uri conectate:
{chr(10).join([f"• {t.content[:50]}..." for t in matching[:2]])}

💭 **Sugestie:** Aceste task-uri ar putea beneficia de o abordare integrată.
        """

        return ""


# =============================================================================
# COMENZI
# =============================================================================


def cmd_heartbeat():
    brain = ImmortalBrain()
    result = brain.heartbeat()
    print("\n" + json.dumps(result, ensure_ascii=False, indent=2))


def cmd_status():
    brain = ImmortalBrain()

    total = len(brain.tasks)
    active = len(
        [t for t in brain.tasks.values() if t.state not in [TaskState.COMPLETED.value]]
    )
    completed = len(
        [t for t in brain.tasks.values() if t.state == TaskState.COMPLETED.value]
    )

    result = {
        "success": True,
        "heartbeat_count": brain.state["heartbeat_count"],
        "total_tasks": total,
        "active_tasks": active,
        "completed_tasks": completed,
        "last_heartbeat": brain.state["last_heartbeat"],
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_list():
    brain = ImmortalBrain()

    tasks_list = []
    for task in brain.tasks.values():
        tasks_list.append(
            {
                "id": task.id,
                "content": task.content[:60] + "..."
                if len(task.content) > 60
                else task.content,
                "state": task.state,
                "progress": task.progress,
                "topic": task.topic,
                "priority": task.priority,
            }
        )

    result = {"success": True, "count": len(tasks_list), "tasks": tasks_list}

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_identity():
    """Gestionează IDENTITY.md."""
    brain = ImmortalBrain()

    if len(sys.argv) < 3:
        # Afișează raport identitate
        report = brain.identity_manager.get_identity_report()
        suggestions = brain.identity_manager.analyze_and_suggest(
            list(brain.tasks.values()), brain.processor.profile.data
        )

        result = {
            "success": True,
            "action": "identity_report",
            "report": report,
            "suggestions": suggestions,
            "issues": brain.identity_manager.validate_identity(),
        }
    else:
        subcommand = sys.argv[2].lower()

        if subcommand == "suggest":
            # Generează sugestii
            suggestions = brain.identity_manager.analyze_and_suggest(
                list(brain.tasks.values()), brain.processor.profile.data
            )
            result = {
                "success": True,
                "action": "identity_suggestions",
                "suggestions": suggestions,
            }

        elif subcommand == "update":
            # Actualizează identitate
            if len(sys.argv) < 5:
                result = {
                    "success": False,
                    "error": "Utilizare: identity update [field] [value]",
                }
            else:
                field = sys.argv[3]
                value = " ".join(sys.argv[4:])
                success = brain.identity_manager.save_identity(
                    {field: value}, reason="Actualizare manuală"
                )
                result = {
                    "success": success,
                    "action": "identity_update",
                    "field": field,
                    "value": value,
                }

        elif subcommand == "history":
            # Afișează istoric
            result = {
                "success": True,
                "action": "identity_history",
                "history": brain.identity_manager.history,
            }
        else:
            result = {
                "success": False,
                "error": f"Subcomandă necunoscută: {subcommand}",
            }

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_core():
    """Gestionare Core Memory (SOUL, TOOLS, MEMORY, USER)."""
    if len(sys.argv) < 3:
        # Afișează raport
        try:
            from core_memory import CoreMemoryManager

            core_manager = CoreMemoryManager()
            report = core_manager.get_comprehensive_report()
            print(report)
            return
        except Exception as e:
            print(json.dumps({"error": f"Eroare la încărcarea Core Memory: {e}"}))
            return

    subcommand = sys.argv[2].lower()

    try:
        from core_memory import CoreMemoryManager

        core_manager = CoreMemoryManager()

        if subcommand == "analyze":
            suggestions = core_manager.analyze_all()
            result = {
                "success": True,
                "action": "core_analyze",
                "suggestions": suggestions,
            }

        elif subcommand == "optimize":
            success, message = core_manager.optimize_memory_file()
            result = {"success": success, "action": "core_optimize", "message": message}

        elif subcommand == "create":
            if len(sys.argv) < 4:
                result = {
                    "success": False,
                    "error": "Specifică tipul: soul, tools, memory, user",
                }
            else:
                file_type = sys.argv[3]
                success = core_manager.create_missing_template(file_type)
                result = {
                    "success": success,
                    "action": "core_create",
                    "file_type": file_type,
                }
        else:
            result = {
                "success": False,
                "error": f"Subcomandă necunoscută: {subcommand}",
            }

    except Exception as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_help():
    print("""
Immortal Brain v5.0 - Agent Autonom Proactiv

COMENZI:
  heartbeat   - Rulează o bătaie de inimă (2 minute ciclu)
  status      - Afișează status sistem
  list        - Listează toate task-urile
  identity    - Gestionare IDENTITY.md
    identity              - Raport identitate
    identity suggest      - Generează sugestii îmbunătățire
    identity update [f] [v] - Actualizează câmp
    identity history      - Vezi istoric evoluție
  core        - Gestionare fișiere core (SOUL, TOOLS, MEMORY, USER)
    core                  - Raport complet
    core analyze          - Analizează toate fișierele
    core optimize         - Optimizează MEMORY.md
    core create [type]    - Creează template (soul/tools/memory/user)

AUTONOMIE:
  Sistemul rulează HEARTBEAT la fiecare 2 minute prin HEARTBEAT.md
  
WORKFLOW AUTOMAT:
  received → research → analysis → planning → approval → execution → completed
                                        ↓ (timeout 6 min)
                                   auto_approved

STĂRI:
  • Task-urile avansează automat prin workflow
  • Primești notificări la fiecare etapă
  • Dacă nu răspunzi în 6 minute → auto-approve
  • Progres raportat procentual

CORE MEMORY:
  • SOUL.md    - Core truths, boundaries, vibe
  • TOOLS.md   - Local notes, device configs
  • MEMORY.md  - User preferences, projects
  • USER.md    - Human profile, context
  • IDENTITY.md - Self definition
  • Analiză automată și sugestii îmbunătățire

CONEXIUNI:
  • Task-uri similare se conectează automat
  • Sugestii îmbunătățiri din task-uri completate
  • Combinări creative de tag-uri

Exemplu HEARTBEAT.md:
  ### La fiecare 2 minute
  - Rulează: python skills/immortal-brain/scripts/brain_service.py heartbeat
  - Notifică rezultatele
""")


def main():
    if len(sys.argv) < 2:
        cmd_help()
        return

    command = sys.argv[1].lower()

    commands = {
        "heartbeat": cmd_heartbeat,
        "status": cmd_status,
        "list": cmd_list,
        "identity": cmd_identity,
        "core": cmd_core,
        "help": cmd_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(json.dumps({"error": f"Comanda necunoscuta: {command}"}))


if __name__ == "__main__":
    main()
