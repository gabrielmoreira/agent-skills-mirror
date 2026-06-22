# /solid-check

Audits target modules or code changes for SOLID and Clean Code principles, specifically evaluating SRP (Single Responsibility) and DIP (Dependency Inversion).

## Protocol
1. **Single Responsibility (SRP) Audit:**
   - Scan modules or classes. Look for functions longer than 40 lines.
   - Detect files containing multiple domains (e.g. database logic intermingled with HTML component rendering, or API routing mixed with complex business calculations).
2. **Dependency Inversion (DIP) Audit:**
   - Check if the code relies directly on external third-party classes, utilities (e.g. standard network fetches, payment clients), or globally-accessed configurations without dependency injection or interface abstraction boundaries.
3. **Report & Abstractions:**
   - Output a checklist of SOLID violations.
   - For each violation, specify:
     - Target file/symbol link
     - The rule violated
     - A concrete refactoring proposal showing how to split the code or abstract the coupling behind an interface.
