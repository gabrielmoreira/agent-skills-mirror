---
name: non-wsq-lms-push
description: Write a NON-WSQ course's Google Drive courseware links into its course record on the tertiarycourses.com.sg storefront admin — Trainer Slides (PPT), Learner Slides (PPT PDF), Lesson Plan, Learner Guide and the Lab/Activities folder. Reads the links from Drive, writes them over the storefront's courseware API.
---

# non-wsq-lms-push — publish courseware links to tertiarycourses.com.sg

The non-WSQ counterpart of `lms-push`. Where the WSQ version writes to
LMS-TMS, this writes to the **storefront admin** on tertiarycourses.com.sg,
which is where non-WSQ (C-prefix) courses live.

Run it **after** `$non-wsq-gdrive-push` — that publishes the files, this
publishes the links to them.

## Required input and hard rules

1. Require the non-WSQ course SKU. If none is supplied, derive it from
   `course_data.py`'s `COURSE_CODE` and confirm it. If it cannot be resolved,
   ask and stop; never guess.
2. Push courseware to Drive first with `$non-wsq-gdrive-push`.
3. Always run a dry run and show all resolved links before writing.
4. Never overwrite a good link with a blank. Report and skip missing Drive
   files while leaving the current storefront field unchanged.
5. Use this endpoint only for C-prefix non-WSQ courses. Send `TGS-` WSQ courses
   through their LMS-TMS workflow instead.

## What it writes

| Storefront field | Source on Drive |
|---|---|
| Trainer Slides URL | the `.pptx` in **Trainer Slides** |
| Learner Slides URL | the `.pdf` in **Learner Slides** |
| Lesson Plan URL | the `LP-*.pdf` in **Lesson Plan** |
| Learner Guide URL | the `LG-*.pdf` in **Learner Guide** |
| Lab URL | the **Activities** folder itself |

**Lab URL is a folder link, not a file link** — a lab set is many worksheets plus
the trainer's datasets and templates, so there is no single file to point at.

Each file is set to *anyone with the link can view* as it is linked, so a learner
opening it from the course page isn't blocked by permissions.

## Transport

`POST /courses/api_courseware` on the storefront, authed with an `X-API-Key`
header — the same shared secret as the other `/courses/api_*` endpoints
(Magento config `courses/general/wsq_schedule_api_key`).

The endpoint is a **partial update**: it writes only the keys present in the body.
That is the important difference from the WSQ LMS-TMS endpoint, which nulls every
column it doesn't receive and therefore forces a read-modify-write. Here, fields
this skill doesn't manage (`courseware_link`, `brochure_link`) are simply left alone.

The endpoint, plus the `learner_guide_url` form field and the new `lab_url` column
(migration 611), live in the **ai-mms** repo:

```
app/code/local/MMD/Courses/controllers/Api/CoursewareController.php
migrations/611-course-courseware-lab-url.sql
app/design/adminhtml/.../dashboard/index.phtml
```

If the endpoint returns 404, the relevant ai-mms change has not been deployed.

## Credentials

```bash
export TC_API_KEY='<the storefront X-API-Key>'    # required
export TC_API='https://www.tertiarycourses.com.sg' # optional, this is the default
```

Keep `TC_API_KEY` in your shell profile, never in a course repo — courseware repos
are pushed to public GitHub.

Read the live value from the storefront container with:

```bash
docker exec ai-mms-web-1 php -r 'require_once "/var/www/html/app/Mage.php"; Mage::app();
  echo Mage::getStoreConfig("courses/general/wsq_schedule_api_key");'
```

If the local ai-mms container is not running, read the seeded value straight from the
ai-mms repo — migration 183 seeds `core_config_data` with it (the production value
matches unless rotated in System → Configuration):

```bash
export TC_API_KEY=$(sed -n "s/.*wsq_schedule_api_key', '\([^']*\)'.*/\1/p" \
  ~/projects/tertiary/ai-mms/migrations/183-wsq-schedule-api-key.sql)
```

**Do not ask the user for this key** — resolve it yourself via the container or
the migration file above, then continue the push. Never print, log, or persist
the value in a course repository.

## Usage

```bash
python "<skill-dir>/lms_push_nonwsq.py" --sku C524 --dry-run
python "<skill-dir>/lms_push_nonwsq.py" --sku C524
```

Resolve `<skill-dir>` from this `SKILL.md`. Show one line per resolved
storefront field, including the Drive source, before the real write. Report
fields written, fields already current, and fields that could not be resolved.

The Drive folder is read from the course's existing **Courseware Link** on the
storefront, so the SKU alone is enough after `$non-wsq-gdrive-push`. Override
with `--drive-folder <link>` when the course has no Courseware Link set yet.

Only fields whose value actually differs are written, so a re-run on unchanged
courseware reports "nothing to write" instead of churning the record.

## Notes

- The storefront's bot filter **403s the default `Python-urllib` User-Agent**
  before the request reaches the controller, so the script sends its own UA.
  Keep that header if you adapt the script.
- A missing Drive folder or file is reported per-field and skipped; the other
  links are still written. It never writes a blank over a good link.
- Non-WSQ courses have no assessment, so — unlike the WSQ flow — there is no
  question-paper attachment step and no answer key to keep off the site.
