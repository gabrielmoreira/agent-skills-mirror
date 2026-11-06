# taobao/buy-together

From one message naming several items to one paid order. `parse` lists
the items, `ack` tells the buyer what was understood, `add` runs once
per item (each round cold-starts Taobao, searches, picks, adds to the
cart; a round that cannot find its item is recorded as missed and the
rest go on), `checkout` ticks exactly those lines, confirms 实付款 off
the order page with the buyer, and pays once. A reply to that
confirmation that is neither yes nor no re-runs `parse` with the reply
and the cart lines: new items get a round, an item already in the cart
is not added again, a dropped item is left unticked. Two revisions,
then the reply hands over.

## The parts

`add.yml` — One item into the cart, nothing paid: `parse` derives the keyword,
`launch` cold-starts Taobao, `search` types the keyword, `pick` opens
the listing and adds it through the 加入购物车 sheet with the quantity
the buyer named, and the walk ends on the detail page. Returns `line`,
the cart line as the buyer will read it. Runs once per item, its `start` the reset
between items.

`checkout.yml` — The cart to one paid order: `launch` cold-starts Taobao and `open-cart`
taps the 购物车 tab, `tick` makes the ticked lines match the buyer's list (unticking
everything else, quantities included), `checkout` taps 结算, the
`confirm-pay` ask quotes 实付款 off the order page (shipping and
discounts applied) and waits for 好的 / 不用, `pay` submits the order
and pays. `lines` 全部, the default, keeps whatever is ticked.
