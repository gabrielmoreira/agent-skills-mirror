@tool
extends RefCounted

## Helper utilities for TEMP agent vision bridge (optional import).
## Prefer plugin.gd handshake; this file documents Control crop patterns.


static func crop_control(full: Image, control: Control) -> Image:
	if full == null or control == null:
		return null
	var r: Rect2 = control.get_global_rect()
	var region := Rect2i(int(r.position.x), int(r.position.y), int(r.size.x), int(r.size.y))
	region = region.intersection(Rect2i(0, 0, full.get_width(), full.get_height()))
	if region.size.x <= 0 or region.size.y <= 0:
		return null
	return full.get_region(region)
