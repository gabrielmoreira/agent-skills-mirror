---
name: salt-wireframes
description: |
  Create GUI mockups and wireframes using PlantUML Salt. Use when designing user
  interfaces, creating UI prototypes, documenting screen layouts, building wireframes,
  mocking up forms and dialogs, or when the user mentions GUI design, interface mockups,
  screen blueprints, UI schematics, wireframe diagrams, form layouts, or visual design
  documentation. Salt provides a text-based DSL for creating professional-looking
  interface mockups without needing graphical tools.
---

# Salt - GUI Wireframes and Mockups

## Quick Start

Salt is a PlantUML subproject for creating GUI wireframes and mockups using a simple text-based DSL. Perfect for designing interfaces, prototyping UIs, and documenting screen layouts.

```clojure
(ns myapp.wireframes
  (:require [clojure.java.shell :refer [sh]]
            [clojure.java.io :as io]))

;; Basic Salt wireframe as string
(def login-wireframe
  "@startsalt
{
  Login    | \"MyName   \"
  Password | \"****     \"
  [Cancel] | [  OK   ]
}
@endsalt")

;; Generate diagram with PlantUML
(defn generate-wireframe [salt-code output-file]
  (spit "temp.salt" salt-code)
  (sh "plantuml" "-tpng" "temp.salt")
  (io/copy (io/file "temp.png") (io/file output-file))
  (io/delete-file "temp.salt")
  (io/delete-file "temp.png"))

;; Usage
(generate-wireframe login-wireframe "login.png")
```

**Key benefits:**
- **Text-based** - Version control friendly, no binary files
- **Fast prototyping** - Quick to create and modify
- **No tools needed** - Just text, generates images via PlantUML
- **Composable** - Build complex UIs from simple components
- **Documentation** - Keep UI specs with code

## Core Concepts

### Basic Syntax

Salt uses special characters to define UI elements:

```clojure
;; Buttons: [text]
"[Submit]"
"[Cancel]"

;; Radio buttons: (text) or (X)
"() Unchecked radio"
"(X) Checked radio"

;; Checkboxes: [] or [X]
"[] Unchecked box"
"[X] Checked box"

;; Text input: "text"
"\"Enter name\""

;; Droplist: ^text^
"^Select option^"
```

### Layout with Grids

Grids organize elements in rows and columns:

```clojure
;; Grid with pipe separators
(def form-layout
  "@startsalt
{
  Name     | \"John Doe\"
  Email    | \"john@example.com\"
  [Cancel] | [Submit]
}
@endsalt")

;; Grid modifiers after opening brace:
;; {#  - Show all lines (grid)
;; {!  - Show vertical lines only
;; {-  - Show horizontal lines only  
;; {+  - Show external border only
```

### Containers

Use brackets to create nested containers:

```clojure
;; Nested layout
(def nested-form
  "@startsalt
{
  Name | {
    First | \"John\"
    Last  | \"Doe\"
  }
  Email | \"john@example.com\"
  [Submit]
}
@endsalt")
```

## Common Workflows

### Workflow 1: Login Form

Create a basic login form:

```clojure
(def login-form
  "@startsalt
{+
  ^\"Login Form\"
  ==
  Username | \"              \"
  Password | \"****          \"
  ==
  [] Remember me
  ==
  [Cancel] | [Login]
}
@endsalt")

;; With Hiccup-style data structure
(defn salt-login []
  (str "@startsalt\n"
       "{\n"
       "  Login    | \"MyName   \"\n"
       "  Password | \"****     \"\n"
       "  [Cancel] | [  OK   ]\n"
       "}\n"
       "@endsalt"))
```

### Workflow 2: Settings Dialog with Tabs

Create tabbed interface:

```clojure
(def settings-dialog
  "@startsalt
{+
  {/ <b>General | Fullscreen | Behavior | Saving }
  {
    {
      Theme: | ^Light Mode^^Dark Mode^High Contrast^
      [X] Enable tooltips
      [X] Show line numbers
      [] Auto-save
    }
  }
  ==
  [Cancel] | [Apply] | [OK]
}
@endsalt")

;; Generate programmatically
(defn salt-tabs [active-tab tabs content]
  (str "@startsalt\n"
       "{+\n"
       "  {/ " (clojure.string/join " | " 
                (map #(if (= % active-tab) 
                        (str "<b>" % "</b>") 
                        %) 
                     tabs)) " }\n"
       "  " content "\n"
       "}\n"
       "@endsalt"))

(salt-tabs "General" 
           ["General" "Fullscreen" "Behavior"]
           "{\n    [X] Enable feature\n  }")
```

### Workflow 3: Data Table

Create table-based layouts:

```clojure
(def user-table
  "@startsalt
{#
  .      | Name     | Email           | Status
  Row 1  | Alice    | alice@email.com | Active
  Row 2  | Bob      | bob@email.com   | Inactive
  Row 3  | Charlie  | charlie@email.com | Active
}
@endsalt")

;; Generate from data
(defn salt-table [headers rows]
  (str "@startsalt\n"
       "{#\n"
       "  . | " (clojure.string/join " | " headers) "\n"
       (clojure.string/join "\n"
         (map-indexed
           (fn [idx row]
             (str "  Row " (inc idx) " | " 
                  (clojure.string/join " | " row)))
           rows))
       "\n}\n"
       "@endsalt"))

(salt-table ["Name" "Email" "Status"]
            [["Alice" "alice@email.com" "Active"]
             ["Bob" "bob@email.com" "Inactive"]])
```

### Workflow 4: Tree Navigation

Create hierarchical navigation:

```clojure
(def file-tree
  "@startsalt
{
  {T
    + Project
    ++ src
    +++ main
    ++++ clojure
    +++++ myapp
    ++++++ core.clj
    ++++++ handlers.clj
    +++ test
    ++++ myapp
    +++++ core_test.clj
    ++ resources
    +++ config.edn
  }
}
@endsalt")

;; Generate tree from data structure
(defn salt-tree
  ([tree] (salt-tree tree 0))
  ([tree depth]
   (let [indent (apply str (repeat (inc depth) "+"))]
     (if (map? tree)
       (clojure.string/join "\n"
         (for [[k v] tree]
           (str indent " " (name k) "\n"
                (salt-tree v (inc depth)))))
       (str indent " " tree)))))

(def project-structure
  {:Project
   {:src {:main {:clojure {:myapp ["core.clj" "handlers.clj"]}}
          :test {:myapp ["core_test.clj"]}}
    :resources ["config.edn"]}})

(str "@startsalt\n{\n{T\n"
     (salt-tree project-structure)
     "\n}\n}\n@endsalt")
```

### Workflow 5: Form with Validation

Create forms with visual validation states:

```clojure
(def registration-form
  "@startsalt
{+
  ^\"Register New Account\"
  ==
  Username   | \"john_doe\" | <color:green>Available
  Email      | \"john@example.com\" | <color:green>Valid
  Password   | \"****\" | <color:red>Too short
  Confirm    | \"****\" | <color:red>Doesn't match
  ==
  [] I agree to terms and conditions
  ==
  [<color:#9a9a9a>Submit]
}
@endsalt")

;; Generate with validation
(defn salt-form-field [label value status]
  (let [color (case status
                :valid "green"
                :invalid "red"
                :warning "orange"
                "black")
        msg (case status
              :valid "Valid"
              :invalid "Invalid"
              :warning "Warning"
              "")]
    (str label " | \"" value "\" | <color:" color ">" msg)))

(defn salt-registration-form [fields]
  (str "@startsalt\n{+\n"
       (clojure.string/join "\n  "
         (map (fn [{:keys [label value status]}]
                (salt-form-field label value status))
              fields))
       "\n}\n@endsalt"))

(salt-registration-form
  [{:label "Username" :value "john_doe" :status :valid}
   {:label "Email" :value "invalid" :status :invalid}])
```

### Workflow 6: Menu Bar

Create application menus:

```clojure
(def app-with-menu
  "@startsalt
{+
  {* File | Edit | View | Help
    File | New | Open | Save | - | Exit
  }
  ==
  {
    Content area here
    .
    .
  }
  ==
  Status: Ready
}
@endsalt")

;; Generate menu structure
(defn salt-menu [items]
  (str "{* " (clojure.string/join " | " (keys items)) "\n"
       (clojure.string/join "\n"
         (for [[menu-name menu-items] items]
           (str "  " menu-name " | " 
                (clojure.string/join " | " menu-items))))
       "\n}"))

(salt-menu
  {"File" ["New" "Open" "Save" "-" "Exit"]
   "Edit" ["Cut" "Copy" "Paste"]
   "View" ["Zoom In" "Zoom Out"]})
```

### Workflow 7: Dashboard Layout

Create complex dashboard layouts:

```clojure
(def dashboard
  "@startsalt
{+
  {* Dashboard | Reports | Settings }
  ==
  {
    {
      ^\"Statistics\"
      {#
        . | Today | This Week | This Month
        Users | 142 | 1,234 | 4,567
        Sales | $1,234 | $12,345 | $45,678
      }
    } | {
      ^\"Quick Actions\"
      [New Order]
      [Generate Report]
      [Export Data]
    }
  }
  ==
  {
    {T
      + Recent Activity
      ++ User john signed in
      ++ Order #1234 completed
      ++ Report generated
    } | {
      ^\"Notifications\"
      () 3 new messages
      () 2 pending approvals
      () 1 system alert
    }
  }
}
@endsalt")
```

### Workflow 8: Mobile App Mockup

Create mobile interface mockups:

```clojure
(def mobile-app
  "@startsalt
{+
  {
    [<&arrow-left>] | <b>Profile</b> | [<&cog>]
  }
  ==
  {SI
    .
    {
      .
      <&person> John Doe
      .
    }
    ==
    Email: john@example.com
    Phone: (555) 123-4567
    ==
    [Edit Profile]
    ==
    ^\"Recent Activity\"
    .
    - Logged in from new device
    - Updated password
    - Changed profile picture
    .
    .
  }
  ==
  {
    [<&home>] | [<&magnifying-glass>] | [<&bell>] | [<&person>]
  }
}
@endsalt")
```

## Advanced Features

### Using OpenIconic Icons

Salt supports OpenIconic icons:

```clojure
(def icon-demo
  "@startsalt
{
  Login<&person> | \"username\"
  Password<&key> | \"****\"
  [<&account-login> Sign In] | [<&circle-x> Cancel]
}
@endsalt")

;; Available icons include:
;; <&person>, <&key>, <&home>, <&cog>, <&check>, <&x>
;; <&arrow-left>, <&arrow-right>, <&magnifying-glass>
;; <&bell>, <&heart>, <&star>, <&file>, <&folder>
;; And many more - see PlantUML OpenIconic documentation
```

### Pseudo Sprites

Define reusable sprite-like elements:

```clojure
(def sprite-demo
  "@startsalt
{
  <<folder
  ............
  .XXXXX......
  .X...X......
  .XXXXXXXXXX.
  .X........X.
  .X........X.
  .XXXXXXXXXX.
  ............
  >>
  |
  This is a folder: <<folder>>
  |
  Another folder: <<folder>>
}
@endsalt")
```

### Scroll Bars

Add scroll bars to containers:

```clojure
;; Vertical and horizontal scrollbars
(def scroll-both
  "@startsalt
{S
  Long content here
  .
  .
  .
}
@endsalt")

;; Vertical only
(def scroll-vertical
  "@startsalt
{SI
  Long content
  .
  .
}
@endsalt")

;; Horizontal only
(def scroll-horizontal
  "@startsalt
{S-
  Wide content here that extends beyond normal width
}
@endsalt")
```

### Text Styling with Creole

Use Creole markup for rich text:

```clojure
(def styled-text
  "@startsalt
{
  **Bold text**
  //Italic text//
  __Underlined text__
  --Strikethrough--
  \"\"Monospaced text\"\"
  ==
  <color:blue>Blue text</color>
  <size:20>Large text</size>
  <back:yellow>Highlighted</back>
}
@endsalt")
```

## Integration with Clojure

### Generating Salt from Data

```clojure
(ns myapp.wireframes
  (:require [clojure.string :as str]))

(defprotocol SaltElement
  (to-salt [this]))

(defrecord Button [text]
  SaltElement
  (to-salt [_] (str "[" text "]")))

(defrecord TextField [value]
  SaltElement
  (to-salt [_] (str "\"" value "\"")))

(defrecord Radio [checked? text]
  SaltElement
  (to-salt [_] (str "(" (if checked? "X" "") ") " text)))

(defrecord Checkbox [checked? text]
  SaltElement
  (to-salt [_] (str "[" (if checked? "X" "") "] " text)))

(defrecord Droplist [options]
  SaltElement
  (to-salt [_] (str "^" (str/join "^" options) "^")))

(defn salt-grid [rows]
  (str "{\n"
       (str/join "\n"
         (map (fn [row]
                (str "  " (str/join " | " 
                                    (map to-salt row))))
              rows))
       "\n}"))

;; Usage
(def login
  [[[:label "Username:"] (->TextField "")]
   [[:label "Password:"] (->TextField "****")]
   [(->Button "Cancel") (->Button "Login")]])

(str "@startsalt\n" (salt-grid login) "\n@endsalt")
```

### Generating Diagrams from Specs

```clojure
(require '[clojure.spec.alpha :as s])

(s/def ::field-type #{:text :password :email :number})
(s/def ::field-name string?)
(s/def ::field-label string?)
(s/def ::field (s/keys :req [::field-type ::field-name ::field-label]))

(s/def ::form (s/keys :req [::title ::fields ::actions]))
(s/def ::fields (s/coll-of ::field))
(s/def ::actions (s/coll-of ::button))
(s/def ::button (s/keys :req [::text]))

(defn spec->salt [form-spec]
  (str "@startsalt\n"
       "{+\n"
       "  ^\"" (::title form-spec) "\"\n"
       "  ==\n"
       (str/join "\n"
         (map (fn [field]
                (str "  " (::field-label field) " | \"\""))
              (::fields form-spec)))
       "\n  ==\n"
       "  " (str/join " | "
               (map #(str "[" (::text %) "]")
                    (::actions form-spec)))
       "\n}\n@endsalt"))

(def contact-form-spec
  {::title "Contact Us"
   ::fields [{::field-type :text
              ::field-name "name"
              ::field-label "Name"}
             {::field-type :email
              ::field-name "email"
              ::field-label "Email"}]
   ::actions [{::text "Cancel"}
              {::text "Submit"}]})

(spec->salt contact-form-spec)
```

### Integration with Web Frameworks

```clojure
;; With Ring/Bidi - serve wireframe images
(require '[bidi.bidi :as bidi])

(defn generate-wireframe-endpoint [salt-code]
  {:status 200
   :headers {"Content-Type" "image/png"}
   :body (generate-png-from-salt salt-code)})

(def routes
  ["/" [["wireframes/login.png" :login-wireframe]
        ["wireframes/dashboard.png" :dashboard-wireframe]]])

(def handlers
  {:login-wireframe (fn [_] (generate-wireframe-endpoint login-form))
   :dashboard-wireframe (fn [_] (generate-wireframe-endpoint dashboard))})

;; With DataStar - display wireframes in UI
(defn wireframe-viewer []
  (html5
    [:head
     [:script {:type "module"
               :src "https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"}]]
    [:body
     [:h1 "UI Mockups"]
     [:button {:data-on:click "@get('/wireframes/login.png')"} 
      "Show Login"]
     [:button {:data-on:click "@get('/wireframes/dashboard.png')"} 
      "Show Dashboard"]
     [:div#wireframe]]))
```

## When to Use Salt

**Use Salt when:**
- Prototyping UI designs quickly
- Documenting screen layouts in text
- Creating wireframes for stakeholder review
- Designing forms and dialogs
- Planning application navigation
- Need version-controllable UI specs
- Working on early-stage design
- Creating technical UI documentation

**Use graphical tools when:**
- Need pixel-perfect designs
- Creating high-fidelity mockups
- Designing complex visual effects
- Working with designers unfamiliar with text syntax
- Branding and marketing materials needed
- Client presentations require polish

**Use Salt vs other tools:**
- **Salt vs Figma/Sketch**: Salt for quick prototypes, Figma for detailed design
- **Salt vs HTML/CSS**: Salt faster for mockups, HTML for actual implementation
- **Salt vs draw.io**: Salt for text-based workflow, draw.io for graphical editing

## Best Practices

**Do:**
- Keep wireframes simple and focused
- Use consistent spacing and alignment
- Version control Salt files with code
- Generate diagrams in CI/CD pipeline
- Use descriptive labels and text
- Leverage grid layouts for structure
- Use colors sparingly for emphasis
- Include OpenIconic icons for clarity

```clojure
;; Good: Clear structure with grid
(def good-form
  "@startsalt
{+
  Username | \"                \"
  Password | \"****            \"
  [Cancel] | [Login]
}
@endsalt")

;; Good: Meaningful labels
(def good-labels
  "@startsalt
{
  <&person> User Profile
  Name: | \"John Doe\"
  Role: | ^Admin^User^Guest^
}
@endsalt")
```

**Don't:**
- Try to make Salt mockups pixel-perfect
- Use Salt for final production designs
- Overcomplicate wireframes with detail
- Forget to generate diagrams from code
- Mix design concerns in wireframes
- Use inconsistent spacing/alignment

```clojure
;; Bad: Too much detail, unclear structure
(def bad-form
  "@startsalt
{
Username with validation and real-time checking|\"john_doe_123_verified_premium_user_since_2020\"
[<color:red><b><i><<CANCEL ALL OPERATIONS>>] | [<color:green><size:20><b>SUBMIT NOW!!!]
}
@endsalt")

;; Good: Simple and clear
(def good-form
  "@startsalt
{
  Username | \"john_doe\"
  [Cancel] | [Submit]
}
@endsalt")
```

## Common Issues

### Issue: Alignment problems

```clojure
;; Problem: Inconsistent spacing
"@startsalt
{
  Short | \"value\"
  Very long label | \"value\"
}
@endsalt"
```

**Solution**: Use padding and consistent length:

```clojure
"@startsalt
{
  Short label      | \"value\"
  Very long label  | \"value\"
}
@endsalt"
```

### Issue: PlantUML not installed

**Problem**: Command `plantuml` not found

**Solution**: Install PlantUML:

```bash
# macOS
brew install plantuml

# Or use Docker
docker run -v $(pwd):/data plantuml/plantuml -tpng /data/diagram.salt
```

### Issue: Complex layouts not working

**Problem**: Nested structures don't render correctly

**Solution**: Simplify nesting, use separate diagrams:

```clojure
;; Instead of deeply nested structure
;; Split into multiple simpler diagrams
(def main-layout "@startsalt {...} @endsalt")
(def detail-view "@startsalt {...} @endsalt")
```

### Issue: Text truncation

**Problem**: Long text gets cut off

**Solution**: Add spacing or break into multiple lines:

```clojure
;; Use padding
"\"Long text here                    \""

;; Or text area
"{+
  This is a long
  text in a textarea
  .
  \"                            \"
}"
```

## Resources

- Official Salt Documentation: https://plantuml.com/salt
- PlantUML: https://plantuml.com
- OpenIconic Icons: https://useiconic.com/open/
- PlantUML Online Server: https://www.plantuml.com/plantuml/uml/
- Creole Syntax: https://plantuml.com/creole

## Related Skills

- **plantuml** - Full PlantUML integration
- **hiccup** - HTML generation (for wireframe viewers)
- **datastar** - Display wireframes in web UI
- **bidi** - Routing for wireframe endpoints

## Summary

Salt enables text-based GUI wireframing and mockups:

1. **Text-based DSL** - Version control friendly
2. **Fast prototyping** - Quick iteration on designs
3. **Composable** - Build complex UIs from simple elements
4. **PlantUML integration** - Generates professional diagrams
5. **Clojure-friendly** - Easy to generate programmatically

**Most common patterns:**

```clojure
;; Simple form
"@startsalt
{+
  Label | \"value\"
  [Cancel] | [OK]
}
@endsalt"

;; Table layout
"@startsalt
{#
  . | Column 1 | Column 2
  Row 1 | Value | Value
}
@endsalt"

;; Tree navigation
"@startsalt
{T
  + Root
  ++ Child
  +++ Grandchild
}
@endsalt"

;; Generate from Clojure
(defn salt-form [fields]
  (str "@startsalt\n{+\n"
       (str/join "\n" 
         (map #(str "  " (:label %) " | \"" (:value %) "\"") 
              fields))
       "\n}\n@endsalt"))
```

Perfect for quickly prototyping UIs, documenting interfaces, and maintaining wireframes alongside code.
