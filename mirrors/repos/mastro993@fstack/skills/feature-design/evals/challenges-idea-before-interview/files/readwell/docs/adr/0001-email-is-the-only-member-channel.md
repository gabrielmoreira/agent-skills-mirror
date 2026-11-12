# Email is the only way Readwell contacts members

The library has no budget and one volunteer maintainer. SMS costs money per message, and push
notifications need either a native app or a web-push service plus a worker that is always on,
which the single VPS and its nightly cron job don't give us. Every member registers with an email
address at the desk, so email reaches everyone. Readwell sends email only, from the nightly job.

Considered: SMS through a paid gateway (recurring cost, numbers go stale); web push (most members
never install the site to their home screen, and iOS only delivers web push to installed sites).
