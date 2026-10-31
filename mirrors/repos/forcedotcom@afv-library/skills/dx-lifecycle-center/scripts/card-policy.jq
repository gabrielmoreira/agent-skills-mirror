# Check a filled widget tree against the chat-card v1 rules before widget.sh prints it.
# Prints nothing when the card may be shown, otherwise one line, "<reason>: <detail>".
#   root   a bare tile/widget with one tile/container child, id "<skill>--<card>--v<N>"
#   tiles  only the tiles in allowed; a node has only definition, attributes and children
#   action only a button has actions: one click, either action/openLink (an allowed URL,
#          target _blank) or action/sendMessage (literal text, 1-2000 characters)
#   url    https, a host that is or ends in salesforce.com, force.com or salesforce.mil, no spaces,
#          no "&amp;" left in it
#   table  1-6 plain columns (no link or typed columns), at most 25 rows of text cells
#   secret no session id, access or refresh token, OAuth code or bearer token anywhere
#   expr   no "{!" anywhere: a card is literal, nothing is left for a renderer to evaluate
#   limits at most 80 nodes and depth 8 (widget.sh checks the size)
# Usage: jq -r -f card-policy.jq <filled tree>   (add --arg all 1 to list every problem)
def allowed: ["tile/container", "tile/column", "tile/row", "tile/text", "tile/badge", "tile/icon",
  "tile/separator", "tile/spacer", "tile/table", "tile/list", "tile/listItem", "tile/callout",
  "tile/progress", "tile/code", "tile/button"];
def allowed_url: type == "string" and length <= 2000 and (test("\\s") | not) and (contains("&amp;") | not)
  and test("^https://([A-Za-z0-9-]+\\.)*(salesforce\\.com|force\\.com|salesforce\\.mil)(:[0-9]+)?([/?#]|$)");
def secret: test("[?&#](sid|access_token|refresh_token|code)=|00D[A-Za-z0-9]{12,15}![A-Za-z0-9._-]{16,}|Bearer\\s+[A-Za-z0-9._~+/-]{16,}"; "i");
def nodes: .children[]? | recurse(.children[]?);
def depth: if ((.children // []) | length) == 0 then 0 else 1 + ([.children[] | depth] | max) end;
def action_problems:
  if .attributes.actions == null then
    if .definition == "tile/button" then "action: a button needs attributes.actions.click" else empty end
  elif .definition != "tile/button" then "action: only tile/button may have actions"
  elif (.attributes.actions | type) != "object" or (.attributes.actions | keys) != ["click"]
    or (.attributes.actions.click | type) != "array" or (.attributes.actions.click | length) != 1
  then "action: a button needs exactly one click action"
  else .attributes.actions.click[0] as $a
    | if $a.definition == "action/openLink" then
        if ($a.attributes.url | allowed_url) | not then "url: an openLink URL is not https on a Salesforce host, or still has &amp;"
        elif $a.attributes.target != "_blank" then "action: openLink must open a new tab (_blank)"
        else empty end
      elif $a.definition == "action/sendMessage" then
        if ($a.attributes.content | type) != "string" or ($a.attributes.content | length) < 1
          or ($a.attributes.content | length) > 2000
        then "action: sendMessage needs 1-2000 characters of text" else empty end
      else "action: \($a.definition) is not allowed" end
  end;
def table_problems:
  if .definition != "tile/table" then empty else .attributes as $t
    | (if ($t.columns | type) != "array" or ($t.columns | length) < 1 or ($t.columns | length) > 6
       then "table: 1-6 columns" else empty end),
      (if [$t.columns[]? | select(type != "object" or .columnType != null)] != []
       then "table: no link or typed columns" else empty end),
      (if ($t.rows | type) != "array" or ($t.rows | length) > 25 then "table: at most 25 rows" else empty end),
      (if [$t.rows[]? | select(type != "object" or ([.[] | select(type != "string")] != []))] != []
       then "table: every row is an object of text cells" else empty end)
  end;
def node_problems:
  if type != "object" then "tiles: a child is not a tile"
  else
    (keys - ["definition", "attributes", "children"]) as $extra
    | (if $extra != [] then "tiles: \(.definition) has \($extra | join(", "))" else empty end),
      (.definition as $d | if any(allowed[]; . == $d) then empty else "tiles: \($d // "a node with no definition") is not allowed" end),
      action_problems, table_problems
  end;

[ (if .definition != "tile/widget" or (keys - ["definition", "children"]) != []
     or (.children | length) != 1 or .children[0].definition != "tile/container"
     or ((.children[0].attributes.id // "") | test("^[a-z0-9-]+--[a-z0-9-]+--v[0-9]+$") | not)
   then "root: a bare tile/widget with one tile/container, id <skill>--<card>--v<N>" else empty end),
  (nodes | node_problems),
  ([nodes] | length | if . > 80 then "limits: \(.) nodes, more than 80" else empty end),
  (depth | if . > 8 then "limits: depth \(.), more than 8" else empty end),
  ([.. | strings | select(secret)] | length | if . > 0 then "secret: \(.) value(s) look like a session id or token" else empty end),
  ([.. | strings | select(test("\\{!"))] | length | if . > 0 then "expr: \(.) value(s) contain {!" else empty end)
]
| if length == 0 then empty
  elif $ARGS.named.all != null then join("; ")
  else .[0] + (if length > 1 then " (and \(length - 1) more)" else "" end) end
