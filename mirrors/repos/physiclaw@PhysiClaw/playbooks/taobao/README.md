# taobao

Five doors, one folder each, chosen by description at the boot. The
marketplace, by courier: `buy` buys one item off the 立即购买 sheet;
`buy-together` buys several in one order. The three delivery
storefronts inside the app, each with its own cart and order page:
`hema-buy` for 盒马 groceries (fresh food, ~30 min), `tmall-buy` for
天猫超市 staples (packaged food, household goods, ~4 h), `shangou-buy`
for 淘宝闪购 takeout from one restaurant or shop (~30 min). An entry that
buys several items runs the two playbooks beside its PLAYBOOK.yml:
`add.yml` once per item, then `checkout.yml` (`taobao/buy-together.add`
to rehearse one); `shangou-buy` adds every dish inside one store visit
instead and runs none.

## Which entry

The boot reads the request and picks by description: a store named
(盒马, 天猫超市 / 猫超, 外卖 / 闪购, a café or restaurant) decides; fresh
ingredients or 买菜 mean 盒马; something to eat or drink now means 闪购;
everyday staples wanted today mean 天猫超市; anything else — a product
with no store named — is the marketplace by courier (`buy`,
`buy-together`).

## Entries are searches, never the grid

The home feed's icon grid reorders, so no route taps it. 盒马 is reached
by searching 盒马 on the home feed (the main search jumps into its
storefront); 天猫超市 and every 闪购 store by the 闪购外卖 tab (a text
tab) and the 闪购 search, where the store's card comes first.

## Device

Recorded on an iPhone with the system in English and Taobao in
Chinese. The pack's pages (`home`, `results`, `buysheet`, `paid`) are
declared by anchors only; run `physiclaw playbooks pages calibrate
taobao` on your phone so one OCR miss does not read a page unknown.

## Rehearsal

`macros/` holds the hands more than one entry shares — `launch` (which
runs `foreground` and `cold-launch`), `search`, `cashier` (the
marketplace and storefront pay hands run it), the `store-*` and
`shangou-*` hands two storefronts share, and `hema-recover`, which a
manifest page's `recover:` names. A hand only one entry uses lives in
that entry's own `macros/` and is written bare there:
`hema-buy/macros/{back,open-cart,settle}.yml`,
`buy-together/macros/nudge.yml`, `tmall-buy/macros/open-tmall.yml`
(`hema-buy`'s `settle` is 盒马's, the pack's is the other storefronts').
Each ships disabled and needs `physiclaw macros run taobao/<name>` —
an entry's is `taobao/<entry>.<name>` — on your device before a playbook
that uses it is live.

## Traps

- `force_quit` kills the foreground app, so `launch` raises Taobao
  before quitting it. A Taobao that resumes on its feed (the tab row
  settled with 推荐, scrolled or not: the search bar stays sticky) is
  used as it is; anything else it kept is mid-state and is quit and
  launched cold.
- Two-character anchors (综合, 销量) match feed text unless pinned
  `within: top`.
- The detail footer's third icon is 收藏, not the cart; `buy` never
  touches the cart, it buys off the 领券购买 / 立即购买 sheet. The cart
  flow reaches the cart by the home footer's 购物车 tab (`buy-together.checkout`'s `open-cart`).
- The 加入购物车 toast is transient, so `buy-together.add` verifies the detail page
  and the cart itself is the check: a line `tick` cannot find escalates.
- Promo popups (天降红包, coupons) cover a page right after it opens;
  `app.landmarks.close` is their ✕, never their buttons.
- A storefront's search field sits at the very top of its search page,
  so iOS draws the Paste bubble BELOW it; the home feed's field sits
  lower and its bubble comes up above (`search` vs `store-search` /
  `shangou-search` — the 闪购 page's bubble sits further right).
- The three storefronts' carts are separate from the marketplace cart,
  and their order pages print 合计, never 实付 — each route's README
  records its own.
- The buy sheet shows `￥…起` until a spec is chosen, and an option row
  tap sometimes needs a second tap.
- A storefront cart's footer button is not the page's identity: 盒马
  prints 去结算, 领券结算 when an unclaimed coupon applies to the ticked
  set (the tap claims it on the way), and 差¥N起送 below the store's
  minimum (¥18 at 盒马, ¥20 at 瑞幸) — `hema-cart` reads its 购物车
  title and `tmall-cart` its 全选 row over any of those three (清空 is
  too small for OCR to hold); `hema-buy.settle` and the pack's `settle`
  each accept both labels.
- Leaving a storefront cart and coming back re-ticks every line and
  keeps the list's scroll (全选, 清空 and the newest lines can sit above
  the header — `hema-buy.open-cart` snaps it to the top when 全选 is
  off the screen, `store-nudge` then moves the 全选 row clear of this phone's
  floating button);
  `go_back` from the cart
  page pops the whole storefront (to the marketplace search-entry
  page), from the order page it pops to the cart with the ticks kept.
- 盒马 splits an order whose lines have different delivery slots: 去结算
  opens a 请分开结算 sheet with one parcel per slot, each with its own
  minimum, instead of the order page — the walk stops there, and
  nothing declares which parcel to buy.
- 天猫超市's store opens under a welcome card (恭喜获得 ¥26, 开心收下)
  whose ✕ sits at y 0.75–0.80, lower than the other stores'; the page
  reads through it, so no covered hand ever fires — `open-tmall` closes
  it while its texts show.
- A 盒马 item page swallows the edge swipe (its gallery): `hema-buy.back`
  pops by each page's own top-left arrow instead.
- 盒马's home opens under a promo card on entry (天天特惠 / 秋风起,
  its ✕ at y 0.69–0.75) that dims 权益中心 past OCR, so the reading is
  unknown rather than covered — `hema-recover` closes it while its
  texts show; and 加入购物车 may raise 购物车内部分商品无法购买 (售罄 /
  即将上架 lines already in the cart) over the 推荐搭配 sheet — 知道了.
