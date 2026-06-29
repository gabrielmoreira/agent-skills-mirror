# Roblox DataStores: sessions, limits & metadata (current engine)

Depth behind the DataStores skill: session locking, versioning/metadata, ordered-
store pagination, request limits, and compliance.

## Session locking (preventing duplicate / clobbered data)

Players can occasionally be in two servers briefly (teleports, rejoin races). Two
servers loading and later saving the same key can lose writes. A *session lock*
makes a key owned by one server at a time:

1. On load, `UpdateAsync` the key to stamp it with this server's `JobId` and a
   timestamp, but only if it's unlocked or the lock is stale (older than, say, the
   `BindToClose` budget).
2. If it's locked by a live server, retry a few times, then either kick the player
   or load read-only.
3. On save/leave, clear the lock as part of the same `UpdateAsync`.

`UpdateAsync` is the right primitive because its callback sees the current value, so
the check-and-set is atomic per request. (Production code often uses a vetted
open-source profile/session library that implements this correctly; if you roll your
own, test the teleport and rapid-rejoin cases.)

## Versioning & metadata

Regular `DataStore` keys support versioning and metadata; `OrderedDataStore` does
not (`DataStoreKeyInfo` is always `nil` there).

```lua
local DataStoreService = game:GetService("DataStoreService")
local store = DataStoreService:GetDataStore("PlayerData")

-- Attach UserIds (for content tracking) and custom metadata on write.
local options = Instance.new("DataStoreSetOptions")
options:SetMetadata({ schema = 2, region = "eu" })
pcall(function()
    store:SetAsync(key, data, { player.UserId }, options)
end)

-- Read returns a second value, the DataStoreKeyInfo.
local ok, value, keyInfo = pcall(function() return store:GetAsync(key) end)
if ok and keyInfo then
    print(keyInfo.Version, keyInfo.CreatedTime, keyInfo.UpdatedTime)
    print(keyInfo:GetUserIds(), keyInfo:GetMetadata())
end
```

Important: when you set metadata or UserIds, you must re-supply them on every write
or they're cleared. List past versions with `ListVersionsAsync` and fetch one with
`GetVersionAsync` to recover from a bad write.

A `schema`/version number stored alongside the data lets you **migrate** old saves:
on load, if `data.schema < CURRENT`, transform the table forward before use.

## Ordered stores: full pagination

```lua
local boards = DataStoreService:GetOrderedDataStore("Coins")
local ok, pages = pcall(function()
    return boards:GetSortedAsync(false, 50)   -- descending, page size 50
end)
if ok then
    while true do
        for rank, entry in ipairs(pages:GetCurrentPage()) do
            -- entry.key (the data key), entry.value (the number)
        end
        if pages.IsFinished then break end
        pages:AdvanceToNextPageAsync()        -- yields; wrap loops in pcall in production
    end
end
```

`GetSortedAsync(ascending, pageSize, minValue?, maxValue?)` — page size caps how
many entries `AdvanceToNextPageAsync` fetches per request.

## Request limits & throttling

- Requests are subject to per-minute budgets that scale with the number of players;
  exceeding them queues requests and eventually drops them.
- `GetAsync` results are cached for a short window — an immediate re-read returns the
  cached value, not necessarily the freshest. Disable caching only if you truly need
  to (it costs extra requests).
- Practical rules: save on leave / `BindToClose` and on a periodic timer (e.g. every
  60–120s), **not** on every value change. Coalesce many small changes into one
  write. Use `UpdateAsync` so concurrent writers don't clobber.
- Treat every Async call as fallible: `pcall` + bounded retry with backoff. See the
  official *Error codes and limits* page for the exact numeric limits, which change
  over time.

## Right to be forgotten (RTBF)

You're responsible for deleting a user's data on request. Implement a removal path
(e.g. `RemoveAsync` on every store keyed by that `UserId`, plus any ordered-store
entries) and the Open Cloud DataStore API can perform deletions from outside the
game. Keep the list of stores/keys a player touches so deletion is complete.

## Open Cloud (out-of-game access)

The Open Cloud DataStore API lets trusted external tools read/write the same stores
with scoped API keys — useful for admin dashboards, moderation, and bulk migration.
Treat the API key as a secret; never embed it in client or game code.
