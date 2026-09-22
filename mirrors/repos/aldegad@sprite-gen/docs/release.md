# 릴리즈 — 태그를 push 하면 릴리즈 페이지가 생긴다

> Owns: How a vX.Y.Z tag becomes a release page, what the workflow attaches, and what stays manual · Index: [docs/README.md](README.md)

릴리즈 페이지는 손으로 만들지 않는다. `vX.Y.Z` 태그가 push 되면 `.github/workflows/release.yml`
이 그 태그의 `CHANGELOG.md` 절을 본문으로 페이지를 만든다. 사람이 `gh release create` 를 기억할
필요가 없게 하는 것이 목적이다 — v2.5.3 이 태그·CHANGELOG·README 까지 올라간 채 릴리즈 페이지만
빠져서, 릴리즈 목록에는 v2.5.2 가 Latest 로 남아 있었던 적이 있다.

## 한 묶음

1. **릴리즈 커밋** — `CHANGELOG.md` 의 `## Unreleased (vX.Y.Z)` 절을 `## vX.Y.Z - <제목>` 으로
   바꾸고, `pyproject.toml` 의 `version` 과 `SKILL.md` 의 `version:` 을 그 버전으로 맞춘다
   (둘의 일치는 `tests/packaging/test_version_ssot.py` 가 강제한다).
2. **PR 로 `main` 머지** — `main` 은 보호 브랜치라 직접 push 가 거부된다. CI 가 초록이어야 한다.
3. **태그 push** — 코드네임 접두사 없는 `vX.Y.Z` 로.

   ```bash
   git tag vX.Y.Z && git push origin vX.Y.Z
   ```

4. **워크플로가 릴리즈를 만든다** — 태그가 가리키는 커밋에서 wheel·sdist·`SHA256SUMS` 를 빌드하고,
   그 버전의 CHANGELOG 절을 본문으로, 절이 이름 댄 GIF 를 자산으로 붙여 릴리즈를 생성한다.
5. **확인은 `gh release view`** — 태그를 push 한 것으로 끝이 아니다. 이게 성공해야 릴리즈가 끝난 것이다.

   ```bash
   gh release view vX.Y.Z --repo aldegad/sprite-gen
   ```

## 이미 있는 릴리즈는 건드리지 않는다

이미 페이지가 있는 태그로 워크플로가 다시 돌면 **아무것도 만들지 않고 아무것도 고치지 않고** 통과한다
(`… already has a release page …; body and assets left untouched.`). 실패한 잡을 다시 돌려도 공개된
페이지를 덮어쓰지 않는다는 뜻이고, 반대로 **이미 공개된 페이지의 본문·자산을 워크플로로 고칠 수는 없다**
— 고칠 일이 생기면 `gh release edit` / `gh release upload` 로 직접 한다.

## 쇼케이스 GIF 는 레포에 커밋된 것만 붙는다

워크플로가 자산으로 첨부하는 GIF 는 **두 조건을 모두 만족한 것뿐**이다:

- 그 버전의 CHANGELOG 절이 `docs/assets/<이름>.gif` 로 이름을 댄다 (본문의 맨 `<이름>.gif` 도
  `docs/assets/` 안에 그 파일이 있으면 같은 것으로 본다), **그리고**
- 그 파일이 레포에 커밋돼 있다.

즉 **레포 밖에서 만든 GIF 는 게이트가 붙이지 못한다.** v2.5.4 처럼 쇼케이스 클립을 레포에 커밋하지
않고 릴리즈 자산으로만 올리는 경우, 그 GIF 는 릴리즈가 생성된 뒤 손으로 올린다:

```bash
gh release upload vX.Y.Z <clip>.gif --repo aldegad/sprite-gen
```

본문에서 그 클립을 보여주려면 릴리즈 다운로드 URL
(`https://github.com/aldegad/sprite-gen/releases/download/vX.Y.Z/<clip>.gif`)로 임베드하고,
공개 후 그 URL 이 200 인지 확인한다. 반대로 CHANGELOG 절이 `docs/assets/…` 경로를 이름 댔는데 그
파일이 체크아웃에 없으면, 죽은 이미지가 달린 페이지를 내보내는 대신 **잡이 실패한다.**

## 태그 없이 미리 돌려보기

`workflow_dispatch` 로 같은 스크립트를 `--dry-run` 으로 돌릴 수 있다. 태그도, 릴리즈도, 업로드도
없이 제목·본문·첨부 목록만 잡 요약에 찍는다. 이 경로는 **dispatch 한 ref 의 CHANGELOG** 를 읽는다
(입력한 태그의 것이 아니라) — 릴리즈 커밋을 준비하는 브랜치에서 본문을 미리 읽어보라는 뜻이다.
GitHub 은 기본 브랜치에 있는 워크플로만 dispatch 하므로, 이 파일이 `main` 에 들어간 뒤부터 쓸 수 있다.

## 잡이 빨갛게 죽는 경우

전부 "조용히 이상한 페이지" 대신 실패를 고른 지점이다.

- 태그에 해당하는 `## vX.Y.Z` 절이 `CHANGELOG.md` 에 없다 (있는 절 목록을 같이 찍는다).
- 그 절이 비어 있다.
- 절이 이름 댄 `docs/assets/…gif` 가 체크아웃에 없다.
- 빌드 디렉터리가 비어 있지 않다 — 낡은 아카이브가 이번 릴리즈 자산으로 섞여 올라가는 것을 막는다.
- `gh` 가 "릴리즈가 있다/없다" 를 답하지 못했다 (토큰 없음, 네트워크 끊김, 5xx). **모르는 답은
  '없음' 으로 읽지 않는다** — 그대로 멈춘다.

## `release not found` 는 "레포 없음" 이기도 하다

`gh release view` 는 **없는 레포·권한 없는 레포**에 대고 물어도 똑같이 `release not found` 로 답한다.
"릴리즈가 아직 없다" 와 "레포 이름을 잘못 썼다" 가 같은 문장인 셈이다. 워크플로에서는 `--repo` 가
`aldegad/sprite-gen` 으로 고정이고 잡 자신의 토큰을 쓰므로 이 모호함에 도달하지 않고, 도달하더라도
뒤따르는 생성이 크게 실패한다. 손으로 확인할 때만 주의하면 된다 — `--repo` 오타가 "아직 릴리즈가
없네" 로 읽힌다. `gh` 의 입자도 한계이지 스크립트가 고칠 수 있는 것이 아니다.

## Related

- [docs/README.md](README.md) — documentation index
