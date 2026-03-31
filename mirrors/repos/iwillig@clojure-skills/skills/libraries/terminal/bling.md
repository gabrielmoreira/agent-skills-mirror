---
name: bling_terminal_styling
description: Terminal styling and formatting library for Clojure.
---

# Bling

A Clojure library for creating colorful and styled terminal output.

## Overview

Bling provides utilities for adding colors, formatting, and ASCII art to terminal output, making CLI applications more user-friendly and visually appealing.

## Core Concepts

**Colors and Styles**: Add visual formatting to output.

```clojure
(require '[bling.core :as bling])

; Colored text
(bling/bling [:red "Error occurred"])
(bling/bling [:green "Success"])
(bling/bling [:bold "Important message"])

; Output to terminal
(println (bling/bling [:yellow "Warning: " :reset "Check logs"]))

; Combining styles
(bling/bling [:bold :cyan "Bold cyan text"])
```

**Callouts**: Formatted message boxes.

```clojure
(require '[bling.core :as bling])

(bling/callout {:type :info} (bling/bling [:bold "Information"]))
(bling/callout {:type :warn} (bling/bling [:bold "Warning message"]))
(bling/callout {:type :error} (bling/bling [:bold "Error occurred"]))
```

## Key Features

- Color support (ANSI)
- Text styling (bold, italic, underline)
- Message formatting
- ASCII art fonts
- Box drawing
- Progress indicators
- Terminal width detection

## When to Use

- CLI applications and tools
- User-friendly terminal output
- Status messages and progress
- Error reporting
- Interactive terminal apps

## When NOT to Use

- Non-interactive output (logs should be plain text)
- Production server output (keep simple)

## Common Patterns

```clojure
(require '[bling.core :as bling])

; Status messages
(defn status-message [status message]
  (let [color (case status
                :success :green
                :error :red
                :warn :yellow
                :info :cyan)]
    (println (bling/bling [color (str status ": " message)]))))

; Progress indication
(defn show-progress [step total]
  (let [percent (* 100 (/ step total))]
    (println (format "Progress: [%-50s] %d%%" 
                     (apply str (repeat (int (/ percent 2)) "="))
                     (int percent)))))

; Formatted output in bb.edn tasks
; (bling/callout
;   {:type :info}
;   (bling/bling [:bold "Running tests..."]))

; Error handling with visual feedback
(defn safe-operation [f]
  (try
    (f)
    (catch Exception e
      (bling/callout {:type :error} 
        (bling/bling [:bold "Operation failed: " :reset (.getMessage e)]))
      (throw e))))
```

## Related Libraries

- io.github.paintparty/bling - Extended styling features
- cli-matic/cli-matic - CLI building

## Resources

- Official Documentation: https://github.com/paintparty/bling
- API Documentation: https://cljdoc.org/d/io.github.paintparty/bling

## Notes

This project uses Bling for colorful terminal output in Babashka tasks and CLI applications.
