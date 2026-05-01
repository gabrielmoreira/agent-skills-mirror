# SequenceDiagram.org Complete Syntax Reference

## Table of Contents

1. Participants
2. Messages
3. Notes and Boxes
4. Control Structures (Fragments)
5. Lifelines and Activation
6. Create and Destroy
7. Styling and Formatting
8. Global Options
9. Special Elements

## 1. Participants

### Basic Participant Types

```
participant Name          # Standard rectangle box
rparticipant Name        # Rounded rectangle
actor Name               # Stick figure actor
boundary Name            # Boundary circle
control Name             # Control circle with arrow
database Name            # Database cylinder
entity Name              # Entity rectangle
```

### Styled Participants

```
actor "<color:#green>User</color>" as U
participant "**System**" as Sys
database "//OrderDB//" as DB
```

### Participant Groups

```
participantgroup #lightblue Backend Services
  control AuthService
  control PaymentService
end

participantgroup #lightyellow Data Layer
  database UserDB
  database OrderDB
end
```

Groups can be nested and styled with colors.

### Participant Spacing

```
participantspacing equal        # Equal spacing
participantspacing 50           # Custom spacing value
```

## 2. Messages

### Basic Message Syntax

```
A->B: message text
```

### Message Types

```
A->B: Synchronous call           # Solid arrow
A-->B: Synchronous return        # Dashed arrow
A->>B: Asynchronous message      # Open arrow
A-->>B: Asynchronous return      # Dashed open arrow
A-xB: Failure/error              # X arrow
[->A: Incoming message           # From outside
A->]: Outgoing message           # To outside
```

### Message Delays

```
A->(1)B: Delayed message         # Non-instantaneous (1-9)
```

### Styled Messages

```
A-[#red;3]>B: Error message      # Color and line weight
A-[#blue]>B: Info message        # Color only
```

### Message Numbering

```
autonumber                       # Start numbering from 1
autonumber 10                    # Start from custom number
```

## 3. Notes and Boxes

### Notes

```
note over A: Single participant note
note over A,B: Multi-participant note
note left of A: Left side note
note right of A: Right side note
```

### Boxes

```
box over A: Standard box
abox over A: Angular box
rbox over A: Rounded box
aboxright over A: Angular right-aligned
aboxleft over A: Angular left-aligned
```

### References

```
ref over A,B: Reference to another diagram
```

## 4. Control Structures (Fragments)

### Alternative Paths

```
alt success case
  System->User: Success message
else error case
  System->User: Error message
else timeout case
  System->User: Timeout message
end
```

### Optional Blocks

```
opt condition met
  System->Cache: Update cache
end
```

### Loops

```
loop for each item
  System->Database: Process item
  Database-->System: Result
end
```

### Parallel Execution

```
par thread 1
  Service->Database: Query 1
else thread 2
  Service->Cache: Query 2
end
```

### Other Fragment Types

```
break on error               # Break from normal flow
  System->User: Critical error
end

critical transaction         # Critical section
  System->Database: Update
end

group Custom Label          # Generic grouping
  System->Service: Call
end

expandable- Collapsed Section  # Collapsible section
  System->Database: Query
  Database-->System: Result
end
```

Additional fragment types: `seq`, `strict`, `neg`, `ignore`, `consider`, `assert`, `region`

## 5. Lifelines and Activation

### Manual Activation

```
activate ParticipantName
ParticipantName->Other: Do something
deactivate ParticipantName
```

### Deactivate After

```
deactivateafter ParticipantName  # Deactivate below previous entry
```

### Auto-Activation

```
autoactivation on               # Enable automatic activation
User->System: Request
System->Database: Query         # Auto-activated
Database-->System: Result       # Auto-deactivated
autoactivation off              # Disable
```

### Activation Styling

```
activecolor #lightblue          # Set activation bar color
```

## 6. Create and Destroy

### Creating Participants

```
User->*NewService: Create via message
create NewService               # Create without message
```

### Destroying Participants

```
destroy ParticipantName         # Destroy at previous position
destroyafter ParticipantName    # Destroy with dedicated space
destroysilent ParticipantName   # Destroy without X symbol
```

## 7. Styling and Formatting

### Text Formatting

```
**bold text**
//italic text//
--small text--
++large text++
""monospaced""
~~strikethrough~~
<color:#red>colored text</color>
<size:20>sized text</size>
<align:center>centered</align>
<background:#yellow>highlighted</background>
<sub>subscript</sub>
<sup>superscript</sup>
```

### Element Styling

Format: `element #fillcolor #bordercolor;width;style`

```
participant User #lightblue #blue;2;dashed
note over User #yellow #red;1;solid: Styled note
```

Colors can be hex (#ff0000) or names (red, lightblue)

Border width: 0-9.9
Border style: solid or dashed

### Named Styles

```
style myStyle #white #red;2;dashed,**<color:#red>
participant User [style=myStyle]
```

### Type-Based Styles

```
participantstyle #lightgray #black;1;solid
notestyle #lightyellow
messagestyle #blue
dividerstyle #gray
boxstyle #lightgreen
lifelinestyle #gray;1;dashed
```

## 8. Global Options

### Title and Spacing

```
title My Sequence Diagram
entryspacing 0.5               # Spacing between entries
space                          # Add vertical space
space 20                       # Add custom space
```

### Message Alignment

```
linear                         # Linear message alignment
parallel                       # Parallel entry positioning
```

### Font Settings

```
fontfamily sans-serif
fontfamily mono
fontfamily Arial
```

### Bottom Participants

```
bottomparticipants             # Display participants at bottom too
```

## 9. Special Elements

### Dividers

```
==Phase 1: Initialization==
User->System: Start
==Phase 2: Processing==
System->Database: Query
==Phase 3: Completion==
System->User: Done
```

### Frames

```
frame #lightblue My Diagram Frame
  participant User
  participant System
  User->System: Message
end
```

### Links

```
note over User: <link:https://example.com>Click here</link>
```

### Comments

```
// This is a comment
# This is also a comment
```

### Line Breaks

```
User->System: First line\nSecond line\nThird line
```

### Escape Characters

```
User->System: Special chars: \\n \\t \\[
```

## Complete Example

```
title E-commerce Checkout Flow

participantgroup #lightblue Frontend
  actor User
  participant WebApp
end

participantgroup #lightgreen Backend
  control OrderService
  control PaymentGateway
end

database OrderDB

autoactivation on

User->WebApp: Click "Checkout"
WebApp->OrderService: Create order

activate OrderDB
OrderService->OrderDB: Save order
OrderDB-->OrderService: Order ID
deactivate OrderDB

alt Payment success
  OrderService->PaymentGateway: Process payment
  PaymentGateway-->OrderService: Payment confirmed

  note over OrderService: Update order status
  OrderService->OrderDB: Mark as paid

  OrderService-->WebApp: Order complete
  WebApp-->User: Show confirmation
else Payment failed
  OrderService->PaymentGateway: Process payment
  PaymentGateway-->OrderService: Payment declined

  OrderService-->WebApp: Payment error
  WebApp-->User: Show error
end
```
