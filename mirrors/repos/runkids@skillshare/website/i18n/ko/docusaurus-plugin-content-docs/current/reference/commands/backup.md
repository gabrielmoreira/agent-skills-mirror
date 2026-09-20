---
sidebar_position: 2
---

# backup

target 디렉터리의 백업을 생성, 목록 조회, 관리합니다.

```bash
skillshare backup              # Backup all skill targets
skillshare backup claude       # Backup specific target
skillshare backup agents       # Backup all agent targets
skillshare backup --all        # Backup skills + agents
skillshare backup --list       # List all backups
skillshare backup --cleanup    # Remove old backups
```

## 언제 사용하나요

- 위험한 변경 전에 수동 백업을 생성할 때
- 복구 옵션을 확인하기 위해 기존 백업 목록을 조회할 때
- 디스크 공간을 확보하기 위해 오래된 백업을 정리할 때

## 자동 백업

다음 작업 전에 백업이 **자동으로** 생성됩니다.
- `skillshare sync` (skill target과 agent target)
- `skillshare sync agents` (agent target만)
- `skillshare target remove`

위치: `~/.local/share/skillshare/backups/<timestamp>/` (global), `.skillshare/backups/` (project mode, agent 전용)

각 자동 백업 이후 `--cleanup`과 동일한 정책으로 보존 정책이 자동 적용됩니다. 스냅샷을 직접 정리할 필요는 없습니다.

## 명령

### 백업 생성

```bash
skillshare backup              # All targets
skillshare backup claude       # Specific target
skillshare backup --dry-run    # Preview
```

### 백업 목록 조회

```bash
skillshare backup --list
```

```
All backups (15.3 MB total)
  2026-01-20_15-30-00  claude, cursor     4.2 MB  ~/.local/share/.../2026-01-20_15-30-00
  2026-01-19_10-00-00  claude             2.1 MB  ~/.local/share/.../2026-01-19_10-00-00
  2026-01-18_09-00-00  claude, cursor     4.0 MB  ~/.local/share/.../2026-01-18_09-00-00
```

### 오래된 백업 정리

```bash
skillshare backup --cleanup           # Remove old backups
skillshare backup --cleanup --dry-run # Preview cleanup
```

기본 정리 정책:
- 최근 10개 백업 유지
- 30일보다 오래된 백업 제거
- 총 크기를 500 MB로 제한

가장 최신 스냅샷은 그 자체만으로 크기 제한을 초과하더라도 항상 유지됩니다 — 복원 지점 없이 남겨지는 일은 없습니다.

이 정책은 모든 `sync` 이후 자동으로 실행되므로, `--cleanup`은 필요할 때 수동으로 정리하는 용도로만 사용하면 됩니다.

## 옵션

| Flag | Description |
|------|-------------|
| `--all` | skill과 agent 모두 백업 |
| `--project, -p` | project mode 사용(`.skillshare/backups/`); **agent 전용** |
| `--global, -g` | global mode 사용(skill의 기본값) |
| `--list, -l` | 모든 백업 목록 조회 |
| `--cleanup, -c` | 오래된 백업 제거 |
| `--target, -t <name>` | 특정 백업 대상 지정(위치 인자의 대안) |
| `--dry-run, -n` | 변경 없이 미리보기 |

`backup`은 위치 인자로 kind도 받습니다: `skillshare backup agents`는 백업 범위를 agent target으로 한정합니다.

## 백업 구조

```
~/.local/share/skillshare/backups/
├── 2026-01-20_15-30-00/
│   ├── claude/
│   │   ├── skill-a/
│   │   └── skill-b/
│   └── cursor/
│       ├── skill-a/
│       └── skill-b/
└── 2026-01-19_10-00-00/
    └── claude/
        └── ...
```

존재하는 skill 디렉터리는 target의 mode에 따라 다릅니다. [What Gets Backed Up](#what-gets-backed-up)을 참고하세요.

## 백업 대상 {#what-gets-backed-up}

백업은 `sync`가 파괴할 수 있는 것, 즉 **target에는 존재하지만 source에는 없는 로컬 콘텐츠**만 보호합니다.

- target 안의 일반 파일과 디렉터리는 백업됩니다
- merge-mode target의 skill별 symlink는 백업에서 **제외**됩니다 — source를 가리키는 symlink는 이미 안전한 단일 source of truth이기 때문입니다. `skillshare sync`가 이를 다시 생성합니다

이는 다음을 의미합니다.
- merge mode: 로컬(symlink되지 않은) skill만 백업됩니다. 동기화된 skill은 source에 존재합니다
- copy mode: 관리되는 모든 skill 디렉터리가 백업됩니다(실제 파일이므로)
- symlink mode: 아무것도 백업되지 않습니다(전체 디렉터리가 하나의 symlink이므로)

target에 symlink만 존재하는 경우 백업이 생성되지 않으며, `backup`은 할 일이 없다고 보고합니다 — 비어 있는 복원 지점은 쓸모가 없기 때문입니다.

## 백업과 디스크 공간 {#backups--disk-space}

백업은 source를 복사하지 않으므로 크기가 작게 유지됩니다. 다음 세 가지 메커니즘은 혼동하기 쉬우니 구분해서 이해하세요.

| Mechanism | Scope | What it controls |
|-----------|-------|------------------|
| `.gitignore` in your source | Git 전용 | Git이 추적하는 항목. 무시된 파일도 디스크에는 그대로 존재함 |
| `ignore:` in `config.yaml` | `sync` | `sync`가 target에 복사하는 파일(주로 copy mode). [sync](/docs/reference/commands/sync) 참고 |
| Backup | Snapshot | 로컬 target 콘텐츠만 해당 — symlink 및 그에 따른 source artifact는 제외됨 |

symlink된 skill은 따라가지 않으므로, source skill 안에 있는 무거운 아티팩트(모델 가중치, `.venv`, 브라우저 프로필, 미디어)는 `.gitignore`나 `ignore:`에 언급되었는지 여부와 관계없이 스냅샷에 **절대** 복사되지 않습니다.

보존 정책은 아래 기본 정책으로 모든 `sync` 이후 자동 실행됩니다. 사용량을 직접 확인하려면:

```bash
du -sh ~/.local/share/skillshare/backups   # Total size on disk
skillshare backup --list                   # Per-snapshot sizes
skillshare backup --cleanup --dry-run      # Preview what retention would remove
```

copy-mode target은 스냅샷이 여전히 커질 수 있는 유일한 경우입니다: 실제 파일이므로 skill 디렉터리 아래의 모든 것이 복사됩니다. 런타임 캐시와 대용량 아티팩트를 skill 트리 밖에 두거나, `ignore:`로 제외하여 애초에 target에 도달하지 않도록 하세요.

## Agent 백업 {#agent-backup}

Agent는 skill 백업과 함께 실행되는 자체 백업 흐름을 가지며, 알아둘 만한 두 가지 차이점이 있습니다.

**항목 이름.** Agent 백업은 각 timestamp 디렉터리 안에서 skill 백업과 나란히 `<target>-agents/`에 저장됩니다. 예를 들어 `skillshare backup --all` 실행 후 레이아웃은 다음과 같습니다.

```
~/.local/share/skillshare/backups/2026-01-20_15-30-00/
├── claude/          # Skills backup for claude
├── claude-agents/   # Agents backup for claude
└── cursor/
```

**project mode는 skill과 반대입니다.** project mode(`-p`)에서 `backup`은 skill target 백업을 거부하지만 agent target은 백업**합니다**. `agents` 필터를 잊으면 다음과 같은 오류가 표시됩니다.

```
backup is not supported in project mode (except for agents)
```

따라서 project mode에서는 `skillshare backup -p agents` 또는 `skillshare backup -p --all` 중 하나를 명시해야 합니다.

```bash
skillshare backup agents                  # All agent targets (global)
skillshare backup agents claude           # Only claude's agents
skillshare backup agents -p               # Project agent targets
skillshare backup --all                   # Skills + agents in one shot
```

agent 리소스 모델은 [Agents](/docs/understand/agents)를, 복구는 [restore](/docs/reference/commands/restore)를 참고하세요.

## 참고 항목

- [restore](/docs/reference/commands/restore) — 백업에서 복원
- [sync](/docs/reference/commands/sync) — 자동으로 백업 생성
- [target remove](/docs/reference/commands/target) — 자동으로 백업 생성
