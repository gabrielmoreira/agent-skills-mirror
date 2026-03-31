---
name: etaoin_browser_automation
description: |
  Automate web browsers with Etaoin, a pure Clojure WebDriver implementation.
  Use when writing browser automation tests, UI testing, web scraping, screenshot
  capture, or when the user mentions WebDriver, Selenium, browser automation,
  headless browsers, UI tests, integration tests, end-to-end tests, or web testing.
---

# Etaoin

A pure Clojure implementation of the WebDriver protocol for browser automation and testing. Etaoin is lightweight, fast, and Selenium-free.

## Quick Start

Etaoin provides instant browser automation directly from the REPL:

```clojure
(require '[etaoin.api :as e]
         '[etaoin.keys :as k])

;; Start a browser
(def driver (e/chrome))
;; or use Firefox:
(def driver (e/firefox))

;; Navigate and interact
(e/go driver "https://en.wikipedia.org/")
(e/wait-visible driver [{:tag :input :name :search}])
(e/fill driver {:tag :input :name :search} "Clojure programming language")
(e/fill driver {:tag :input :name :search} k/enter)

;; Query results
(e/get-title driver)
;; => "Clojure - Wikipedia"

;; Take a screenshot
(e/screenshot driver "wiki-clojure.png")

;; Clean up
(e/quit driver)
```

**Key benefits:**
- Selenium-free: no large Java dependencies
- Pure Clojure: simple, composable API
- REPL-driven: test interactively
- Multi-browser: Chrome, Firefox, Safari, Edge
- Babashka compatible: fast startup for scripts

## Core Concepts

### WebDriver Lifecycle

Etaoin manages WebDriver processes for you:

```clojure
;; Manual lifecycle
(def driver (e/chrome))
;; ... do work
(e/quit driver)

;; Automatic lifecycle (recommended)
(e/with-chrome driver
  (e/go driver "https://clojure.org")
  ;; driver automatically closed on exit
  )
```

The `with-<browser>` macros ensure cleanup even if exceptions occur.

### Element Queries

Queries locate elements on the page. Multiple syntax options:

```clojure
;; By ID (keyword)
(e/click driver :submit-button)

;; By attribute map
(e/click driver {:tag :button :class :primary})

;; By XPath string
(e/click driver "//button[@class='primary']")

;; By CSS (when driver uses CSS mode)
(e/use-css driver)
(e/click driver "button.primary")

;; Vector queries chain from element to element
(e/click driver [{:tag :form} {:tag :button :type :submit}])
```

### Headless Browsers

Run browsers without UI for CI/CD:

```clojure
(e/with-chrome-headless driver
  (e/go driver "https://example.com")
  ;; no browser window appears
  )

;; Or explicitly
(e/chrome {:headless true})
```

### Wait Functions

Wait for page state before interacting:

```clojure
;; Wait for element to be visible
(e/wait-visible driver :search-results)

;; Wait for text to appear
(e/wait-has-text driver :message "Success")

;; Wait with custom timeout
(e/with-wait-timeout 30
  (e/wait-visible driver :slow-element))

;; Simple time-based wait
(e/wait driver 2) ;; wait 2 seconds
```

## Common Workflows

### Workflow 1: Basic Form Interaction

```clojure
(e/with-chrome driver
  ;; Navigate to page
  (e/go driver "https://example.com/login")
  
  ;; Fill form fields
  (e/fill driver :username "test@example.com")
  (e/fill driver :password "secret123")
  
  ;; Submit form
  (e/click driver {:tag :button :type :submit})
  
  ;; Wait for redirect
  (e/wait-visible driver :dashboard)
  
  ;; Verify success
  (e/has-text? driver "Welcome back"))
;; => true
```

### Workflow 2: Testing File Downloads

```clojure
(require '[clojure.java.io :as io])

(def download-dir "target/downloads")

(e/with-chrome {:download-dir download-dir} driver
  (e/go driver "https://example.com/reports")
  
  ;; Click download link
  (e/click driver :download-report)
  
  ;; Wait for download to complete
  (e/wait 5)
  
  ;; Verify file exists
  (let [files (file-seq (io/file download-dir))
        pdf-files (filter #(.endsWith (.getName %) ".pdf") files)]
    (is (seq pdf-files) "PDF report should be downloaded")))
```

### Workflow 3: Screenshot Capture

```clojure
(e/with-firefox driver
  (e/go driver "https://clojure.org")
  
  ;; Full page screenshot
  (e/screenshot driver "clojure-homepage.png")
  
  ;; Screenshot specific element (Chrome/Firefox only)
  (e/screenshot-element driver 
                        {:id :main-content}
                        "content-only.png")
  
  ;; Screenshot after each action
  (e/with-screenshots driver "screenshots/"
    (e/click driver :menu)
    (e/click driver :submenu)
    ;; creates chrome-<timestamp>.png after each action
    ))
```

### Workflow 4: Multi-Element Selection

```clojure
(e/with-chrome driver
  (e/go driver "https://example.com/products")
  
  ;; Get all product elements
  (def products (e/query-all driver {:class :product-card}))
  
  ;; Interact with each
  (doseq [product products]
    (let [name (e/get-element-text-el driver product)
          price (e/get-element-text-el 
                  driver 
                  (e/query-from driver product {:class :price}))]
      (println name "-" price)))
  
  ;; Click the nth element
  (e/click-el driver (nth products 2)))
```

### Workflow 5: Handling JavaScript

```clojure
(e/with-chrome driver
  (e/go driver "https://example.com")
  
  ;; Execute JavaScript
  (e/js-execute driver "alert('Hello from Etaoin!')")
  (e/dismiss-alert driver)
  
  ;; Return data from JavaScript
  (def window-size 
    (e/js-execute driver 
                  "return {width: window.innerWidth, height: window.innerHeight}"))
  ;; => {:width 1024, :height 768}
  
  ;; Async JavaScript with callbacks
  (e/js-async driver 
    "var callback = arguments[arguments.length-1];
     setTimeout(function() { callback(42); }, 1000);"
    {})
  ;; => 42
  )
```

### Workflow 6: Frame/iFrame Navigation

```clojure
(e/with-chrome driver
  (e/go driver "https://example.com/page-with-frames")
  
  ;; Cannot see inside frames initially
  (e/exists? driver :element-in-frame)
  ;; => false
  
  ;; Switch to frame
  (e/switch-frame driver :my-frame)
  
  ;; Now can interact with elements in frame
  (e/click driver :element-in-frame)
  
  ;; Switch back to main page
  (e/switch-frame-top driver)
  
  ;; Or use with-frame for automatic cleanup
  (e/with-frame driver {:id :my-frame}
    (e/click driver :element-in-frame)
    ;; automatically returns to previous frame
    ))
```

### Workflow 7: Writing Tests with Postmortem

```clojure
(require '[clojure.test :refer [deftest is use-fixtures]])

(def ^:dynamic *driver*)

(defn fixture-driver [f]
  (e/with-chrome driver
    (binding [*driver* driver]
      (f))))

(use-fixtures :each fixture-driver)

(deftest test-login-flow
  (e/with-postmortem *driver* {:dir "target/postmortem"}
    (e/go *driver* "https://example.com/login")
    (e/fill *driver* :username "test@example.com")
    (e/fill *driver* :password "wrong-password")
    (e/click *driver* :submit)
    
    ;; If this fails, saves screenshot + HTML + console logs
    (is (e/wait-has-text *driver* :error "Invalid credentials"))))
```

## When to Use Each Approach

### Use Etaoin when:
- Writing browser UI integration tests
- Automating web interactions
- Testing JavaScript-heavy applications
- Capturing screenshots for documentation
- Scraping data from dynamic sites
- Running tests in CI/CD pipelines

### Use headless mode when:
- Running in CI/CD without displays
- Need faster test execution
- Testing backend-rendered content
- Saving system resources

### Use explicit waits when:
- Working with dynamic content
- AJAX requests load data
- Animations or transitions occur
- Page loads are unpredictable

## Best Practices

**DO:**
- Use `with-<browser>` macros for automatic cleanup
- Wait for elements before interacting (`wait-visible`, `wait-has-text`)
- Use headless mode in CI/CD environments
- Take screenshots on test failures for debugging
- Set explicit download directories when testing downloads
- Use vector queries to navigate element hierarchies
- Test with multiple browsers (Chrome, Firefox)
- Set `load-strategy` to `:eager` or `:none` for faster page loads

**DON'T:**
- Forget to call `quit` when not using `with-` macros
- Interact with elements before they're visible
- Use `wait` with fixed times except for debugging
- Skip cleanup in test fixtures
- Assume all browsers behave identically
- Use emojis in Chrome/Edge (limited UNICODE support)
- Query for active element using `:active` keyword (deprecated, use `get-active-element`)

## Common Issues

### Issue: "Element not interactable"

**Problem:** Clicking on element throws error

```clojure
(e/click driver :hidden-button)
;; Error: element not interactable
```

**Solution:** Ensure element is visible first

```clojure
(e/wait-visible driver :hidden-button)
(e/click driver :hidden-button)
```

### Issue: "Stale element reference"

**Problem:** Element reference becomes invalid after page change

```clojure
(def elem (e/query driver :button))
(e/click driver :refresh) ;; page refreshes
(e/click-el driver elem)  ;; fails - element is stale
```

**Solution:** Re-query after page changes

```clojure
(e/click driver :refresh)
(e/wait-visible driver :button)
(def elem (e/query driver :button)) ;; re-query
(e/click-el driver elem)
```

### Issue: Tests pass locally but fail in CI

**Problem:** Tests work on developer machine but fail in CI

**Cause:** CI often has no display, different screen size, or timing issues

**Solution:** Use headless mode and explicit waits

```clojure
;; In CI environment
(e/with-chrome-headless {:size [1920 1080]} driver
  (e/with-wait-timeout 30
    ;; tests with longer timeouts for CI
    ))
```

### Issue: Downloads not working in headless Chrome

**Problem:** Files don't download in headless mode

**Solution:** Explicitly enable downloads for headless Chrome

```clojure
(e/chrome-headless 
  {:download-dir "target/downloads"
   :prefs {:download.default_directory (str (.getAbsolutePath 
                                              (io/file "target/downloads")))
           :download.prompt_for_download false}})
```

### Issue: Safari automation not working

**Problem:** Safari driver fails to start

**Solution:** Enable remote automation in Safari

1. Enable Developer menu: Safari → Preferences → Advanced → "Show Develop menu"
2. Enable Remote Automation: Develop → "Allow Remote Automation"
3. Run `safaridriver --enable` from terminal

## Advanced Topics

### WebDriver Actions API

Low-level input device simulation:

```clojure
;; Create virtual input devices
(def mouse (e/make-mouse-input))
(def keyboard (e/make-key-input))

;; Build action sequences
(-> keyboard
    (e/add-key-down k/shift-left)
    (e/add-key-press "h")
    (e/add-key-press "e")
    (e/add-key-press "l")
    (e/add-key-press "l")
    (e/add-key-press "o")
    (e/add-key-up k/shift-left))

;; Perform actions
(e/perform-actions driver keyboard mouse)
(e/release-actions driver)
```

### DevTools Integration (Chrome only)

Track network requests and AJAX:

```clojure
(require '[etaoin.dev :as dev])

(e/with-chrome {:dev {}} driver
  (e/go driver "https://example.com")
  
  ;; Get all HTTP requests
  (def reqs (dev/get-requests driver))
  
  ;; Filter AJAX requests
  (def ajax (dev/get-ajax driver))
  
  ;; Check request status
  (dev/request-done? (first ajax))
  (dev/request-success? (first ajax)))
```

### Shadow DOM Queries

Query elements inside shadow DOM:

```clojure
;; Check if element has shadow root
(e/has-shadow-root? driver {:id "shadow-host"})
;; => true

;; Get shadow root
(def shadow-root (e/get-element-shadow-root driver {:id "shadow-host"}))

;; Query inside shadow DOM (use CSS, not XPath)
(e/query-from-shadow-root driver {:id "shadow-host"} {:css "#inner-element"})
```

### Running Selenium IDE Scripts

Play back recorded browser sessions:

```clojure
(require '[etaoin.ide.flow :as flow])

(e/with-chrome driver
  (flow/run-ide-script driver "test.side" 
                       {:base-url "https://example.com"}))
```

## Testing Configuration

### Multi-Driver Test Fixture

Test against multiple browsers:

```clojure
(def driver-types [:chrome :firefox])

(defn fixture-drivers [f]
  (doseq [type driver-types]
    (e/with-driver type {:headless true} driver
      (binding [*driver* driver]
        (testing (format "Testing in %s" (name type))
          (f))))))

(use-fixtures :each fixture-drivers)
```

### Connecting to Remote WebDriver

Connect to existing WebDriver (e.g., in Docker):

```clojure
;; WebDriver running on localhost:9515
(def driver (e/chrome {:host "localhost" :port 9515}))

;; Or specify full URL
(def driver (e/chrome {:webdriver-url "http://selenium-hub:4444/wd/hub"}))
```

## Resources

- GitHub: https://github.com/clj-commons/etaoin
- API Documentation: https://cljdoc.org/d/etaoin/etaoin
- User Guide: https://github.com/clj-commons/etaoin/blob/master/doc/01-user-guide.adoc
- Slack: #etaoin on Clojurians Slack

## Summary

Etaoin provides pure Clojure browser automation:

1. **Simple API** - Query elements, click, fill, navigate
2. **Multi-browser** - Chrome, Firefox, Safari, Edge
3. **REPL-friendly** - Interactive development and debugging
4. **Testing-focused** - Fixtures, postmortem, screenshots
5. **Headless support** - Run without UI for CI/CD
6. **Selenium-free** - Lightweight, no Java dependencies

**Core workflow:**
- Start driver with `with-<browser>`
- Navigate with `go`
- Query elements with maps, keywords, or strings
- Wait for state with `wait-visible`, `wait-has-text`
- Interact with `click`, `fill`, `select`
- Capture artifacts with `screenshot` and `with-postmortem`

Etaoin makes browser automation feel like natural Clojure code.
