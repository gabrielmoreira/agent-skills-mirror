# Fill an HXL widget template (<name>.json) with the values in $attrs, the way
# mosaic-json-core evaluates the same bindings, so the result has no expressions left:
#   "{!$attrs.k}" as the whole string     -> the value itself, any JSON type
#   "... {!$attrs.k} ..." inside a string -> the value as text
#   "meta": {"if": "{!$attrs.k}"}         -> the node stays only when k is true
# Any other expression or meta key, a missing attr, or a "{!" in a value is an error.
# A v68.0 envelope ({"type": "lightning__agentforceWidget", "contentBody": {"widgetBody": ...}})
# is unwrapped first, so the result is always the bare tile/widget tree.
# Usage: jq -c --argjson attrs '<json object>' -f fill-widget.jq <name>.json
def binding: "\\{!\\$attrs\\.(?<k>[A-Za-z0-9_]+)\\}";
def attr($k): if $attrs | has($k) then $attrs[$k] else error("missing attr: \($k)") end;
def fill:
  if test("^" + binding + "$") then attr(capture("^" + binding + "$").k)
  else gsub(binding; attr(.k) | tostring) end;
def keep:
  if (.meta | type) != "object" then true
  elif (.meta | keys) != ["if"] then error("unsupported meta: \(.meta | keys | join(","))")
  elif (.meta.if | type) == "string" then (.meta.if | fill) == true
  else .meta.if == true end;
def prune: if (.children | type) == "array" then .children |= map(select(keep) | prune) else . end;

(if .type == "lightning__agentforceWidget" then .contentBody.widgetBody else . end)
| if [.. | strings | select(gsub(binding; "") | test("\\{!"))] != [] then error("unsupported expression in template")
elif .meta != null then error("meta is not allowed on the root")
else . end
| prune
| walk(if type == "object" and has("definition") then del(.meta) else . end)
| walk(if type == "string" then fill else . end)
| if [.. | strings | select(test("\\{!"))] != [] then error("a value contains {!") else . end
