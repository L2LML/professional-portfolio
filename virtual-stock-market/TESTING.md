# Testing Documentation - Virtual Stock Market

**Project**: Virtual Stock Market - Team Capstone  
**Tested By**: Lisa Marie Lewandowski  
**Last Updated**: February 17, 2026  
**Test Coverage**: 82% (Backend), 75% (Frontend)

## 📋 Table of Contents
- [Testing Strategy](#testing-strategy)
- [Test Environment](#test-environment)
- [Manual Test Cases](#manual-test-cases)
- [API Testing](#api-testing)
- [Automated Tests](#automated-tests)
- [Bug Tracking](#bug-tracking)
- [Quality Metrics](#quality-metrics)
- [User Acceptance Testing](#user-acceptance-testing)

---

## 🎯 Testing Strategy

### Testing Objectives
1. Validate stock trading logic and calculations
2. Ensure API integration with Market Stack works reliably
3. Verify database transaction integrity (ACID properties)
4. Test authentication and authorization security
5. Confirm portfolio calculations are accurate
6. Validate edge cases (insufficient funds, invalid symbols, etc.)

### Testing Scope

**In Scope:**
- User registration and authentication
- Stock search and price retrieval
- Buy/sell transaction processing
- Portfolio balance calculations
- Competition creation and management
- Leaderboard rankings
- Transaction history
- API error handling

**Out of Scope:**
- Market Stack API reliability (third-party)
- Browser compatibility (tested Chrome, Firefox only)
- Performance/load testing (planned for future)

### Testing Types Performed
- ✅ **Unit Testing** - Individual methods and components
- ✅ **Integration Testing** - API endpoints and database
- ✅ **Functional Testing** - End-to-end workflows
- ✅ **Regression Testing** - Post-bug-fix verification
- ✅ **User Acceptance Testing** - Stakeholder validation
- ✅ **Security Testing** - Authentication and authorization
- ✅ **API Testing** - REST endpoint validation
- ⚠️ **Performance Testing** - Planned for future sprints

### Testing Tools
- **Backend**: JUnit 5, Mockito, Spring Boot Test
- **Frontend**: Jest, Vue Test Utils
- **API Testing**: Postman, REST Assured
- **Database**: PostgreSQL with test database
- **Version Control**: Git for test case management
- **Bug Tracking**: GitHub Issues

---

## 🖥️ Test Environment

### Development Environment
- **OS**: Windows 11, macOS
- **Backend**: Java 11, Spring Boot 2.7, PostgreSQL 14
- **Frontend**: Node.js 16, Vue.js 3
- **IDE**: IntelliJ IDEA, VS Code

### Test Database
- **Name**: `virtual_stock_market_test`
- **Purpose**: Isolated environment for testing
- **Refresh**: Reset before each test suite

### Test Data
- **Test Users**: 
  - `test_user_1` (ID: 100, Starting balance: $10,000)
  - `test_user_2` (ID: 101, Starting balance: $10,000)
- **Test Stocks**: AAPL, MSFT, TSLA, GOOGL
- **Mock API Responses**: Stored in `src/test/resources/mock-data/`

---

## 🧪 Manual Test Cases

### TC-001: User Registration

**Priority**: High  
**Type**: Functional  
**Prerequisites**: None

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to /register | Registration form displays | ✅ Pass |
| 2 | Enter username "testuser123" | Input accepted | ✅ Pass |
| 3 | Enter valid email "test@example.com" | Input accepted | ✅ Pass |
| 4 | Enter password "SecurePass123!" | Password masked | ✅ Pass |
| 5 | Confirm password matches | Confirmation field validates | ✅ Pass |
| 6 | Click "Register" button | User created, redirect to login | ✅ Pass |
| 7 | Verify database entry | User exists in `users` table | ✅ Pass |
| 8 | Verify password hash | Password stored as bcrypt hash | ✅ Pass |

**Result**: PASS  
**Notes**: Registration workflow functions correctly

---

### TC-002: Duplicate Username Registration

**Priority**: High  
**Type**: Negative Testing  
**Prerequisites**: User "testuser123" already exists

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to /register | Registration form displays | ✅ Pass |
| 2 | Enter existing username "testuser123" | Input accepted | ✅ Pass |
| 3 | Fill in other required fields | Form completed | ✅ Pass |
| 4 | Click "Register" button | Error: "Username already exists" | ✅ Pass |
| 5 | Verify user not duplicated | Only one entry in database | ✅ Pass |
| 6 | Verify error message styling | Red error message displayed | ✅ Pass |

**Result**: PASS  
**Notes**: Duplicate prevention works correctly

---

### TC-003: Buy Stock - Sufficient Funds

**Priority**: Critical  
**Type**: Functional  
**Prerequisites**: User logged in with $10,000 balance, AAPL trading at $150.00

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Search for stock "AAPL" | Stock info displayed | ✅ Pass |
| 2 | View current price | Price: $150.00 shown | ✅ Pass |
| 3 | Enter quantity: 50 shares | Input accepted | ✅ Pass |
| 4 | Review total cost | Total: $7,500.00 calculated | ✅ Pass |
| 5 | Click "Buy" button | Transaction initiated | ✅ Pass |
| 6 | Verify success message | "Purchase successful" displayed | ✅ Pass |
| 7 | Check updated cash balance | Balance: $2,500.00 ($10,000 - $7,500) | ✅ Pass |
| 8 | Verify portfolio holdings | 50 shares AAPL in portfolio | ✅ Pass |
| 9 | Check transaction history | Buy transaction logged with timestamp | ✅ Pass |

**Result**: PASS  
**Database Verification**:
```sql
-- Verified portfolio balance
SELECT cash_balance FROM portfolios WHERE user_id = 100;
-- Expected: 2500.00

-- Verified holdings
SELECT symbol, quantity FROM holdings WHERE portfolio_id = 1;
-- Expected: AAPL, 50
```

---

### TC-004: Buy Stock - Insufficient Funds

**Priority**: Critical  
**Type**: Negative Testing  
**Prerequisites**: User has $2,500 balance, AAPL at $150.00

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Search for stock "AAPL" | Stock displayed | ✅ Pass |
| 2 | Enter quantity: 20 shares | Input accepted (requires $3,000) | ✅ Pass |
| 3 | Click "Buy" button | Transaction rejected | ✅ Pass |
| 4 | Verify error message | "Insufficient funds" displayed | ✅ Pass |
| 5 | Check cash balance unchanged | Balance still $2,500 | ✅ Pass |
| 6 | Verify no holdings added | Portfolio unchanged | ✅ Pass |
| 7 | Check transaction history | No new transaction logged | ✅ Pass |

**Result**: PASS  
**Notes**: Validation prevents overdraft correctly

---

### TC-005: Sell Stock - Sufficient Shares

**Priority**: Critical  
**Type**: Functional  
**Prerequisites**: User owns 50 shares of AAPL, current price $155.00

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Portfolio | Holdings displayed | ✅ Pass |
| 2 | Select AAPL holding (50 shares) | Stock selected | ✅ Pass |
| 3 | Click "Sell" | Sell dialog opens | ✅ Pass |
| 4 | Enter quantity: 30 shares | Input accepted | ✅ Pass |
| 5 | Review sell value | $4,650.00 ($155 × 30) calculated | ✅ Pass |
| 6 | Click "Confirm Sell" | Transaction processed | ✅ Pass |
| 7 | Verify success message | "Sale successful" displayed | ✅ Pass |
| 8 | Check updated cash balance | Increased by $4,650.00 | ✅ Pass |
| 9 | Verify remaining holdings | 20 shares AAPL remaining | ✅ Pass |
| 10 | Check transaction history | Sell transaction logged | ✅ Pass |

**Result**: PASS  
**Profit Calculation Verified**: Bought at $150, sold at $155 = $5 profit/share × 30 = $150 profit

---

### TC-006: Sell Stock - Insufficient Shares

**Priority**: High  
**Type**: Negative Testing  
**Prerequisites**: User owns 20 shares of AAPL

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Portfolio | Holdings show 20 AAPL shares | ✅ Pass |
| 2 | Attempt to sell 30 shares | Quantity exceeds holdings | ✅ Pass |
| 3 | Click "Confirm Sell" | Transaction rejected | ✅ Pass |
| 4 | Verify error message | "Insufficient shares to sell" | ✅ Pass |
| 5 | Check holdings unchanged | Still owns 20 shares | ✅ Pass |
| 6 | Check cash balance unchanged | No cash added | ✅ Pass |

**Result**: PASS

---

### TC-007: Invalid Stock Symbol

**Priority**: Medium  
**Type**: Negative Testing  
**Prerequisites**: None

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to stock search | Search form displayed | ✅ Pass |
| 2 | Enter invalid symbol "ZZZZZ" | Input accepted | ✅ Pass |
| 3 | Click "Search" | API called | ✅ Pass |
| 4 | Verify error handling | "Stock not found" message | ✅ Pass |
| 5 | Confirm no data displayed | Empty result set | ✅ Pass |

**Result**: PASS  
**Notes**: Graceful error handling for invalid symbols

---

### TC-008: Competition Leaderboard Calculation

**Priority**: High  
**Type**: Functional  
**Prerequisites**: Multiple users in same competition

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create test competition | Competition ID: 5 | ✅ Pass |
| 2 | Add User A (portfolio value: $12,000) | User added | ✅ Pass |
| 3 | Add User B (portfolio value: $15,000) | User added | ✅ Pass |
| 4 | Add User C (portfolio value: $9,500) | User added | ✅ Pass |
| 5 | Navigate to leaderboard | Leaderboard displays | ✅ Pass |
| 6 | Verify ranking order | 1. User B, 2. User A, 3. User C | ✅ Pass |
| 7 | Check portfolio values | Values match database | ✅ Pass |
| 8 | Verify profit/loss calculation | User B: +50%, User C: -5% | ✅ Pass |

**Result**: PASS  
**Calculation Formula Verified**:
```
Portfolio Value = Cash Balance + (Shares × Current Price)
Profit % = ((Current Value - Starting Value) / Starting Value) × 100
```

---

### TC-009: Transaction History Display

**Priority**: Medium  
**Type**: Functional  
**Prerequisites**: User has made multiple transactions

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Transaction History | Page loads | ✅ Pass |
| 2 | Verify transaction list | All transactions displayed | ✅ Pass |
| 3 | Check sorting order | Most recent first (DESC) | ✅ Pass |
| 4 | Verify transaction details | Symbol, type, qty, price shown | ✅ Pass |
| 5 | Check timestamp format | "MM/DD/YYYY HH:MM AM/PM" | ✅ Pass |
| 6 | Verify buy/sell indicators | Color-coded (green=buy, red=sell) | ✅ Pass |
| 7 | Test pagination (if >20 records) | Pagination works | ⚠️ N/A (< 20 records) |

**Result**: PASS

---

### TC-010: Session Timeout

**Priority**: High  
**Type**: Security  
**Prerequisites**: User logged in

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Login successfully | JWT token received | ✅ Pass |
| 2 | Wait 25 hours (token expiry: 24hrs) | Session expires | ✅ Pass |
| 3 | Attempt API call | 401 Unauthorized error | ✅ Pass |
| 4 | Verify redirect to login | Redirected to /login | ✅ Pass |
| 5 | Verify error message | "Session expired, please login" | ✅ Pass |

**Result**: PASS  
**Notes**: JWT expiration correctly enforced

---

## 📡 API Testing

### Postman Collection

All API endpoints tested using Postman with automated test scripts.

**Collection**: `Virtual-Stock-Market-API-Tests.postman_collection.json`

### Authentication Endpoints

#### POST /api/auth/register

**Test Case**: Successful Registration
```javascript
// Postman Test Script
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Response contains user data", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('username');
});
```

**Result**: ✅ PASS

---

#### POST /api/auth/login

**Test Case**: Valid Credentials
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("JWT token returned", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('token');
    pm.environment.set("jwt_token", jsonData.token);
});
```

**Result**: ✅ PASS

---

### Stock Endpoints

#### GET /api/stocks/search?symbol=AAPL

**Test Case**: Valid Stock Symbol
```javascript
pm.test("Returns stock data", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.symbol).to.eql("AAPL");
    pm.expect(jsonData.price).to.be.a('number');
});
```

**Result**: ✅ PASS

---

#### GET /api/stocks/search?symbol=INVALID

**Test Case**: Invalid Stock Symbol
```javascript
pm.test("Returns 404 for invalid symbol", function () {
    pm.response.to.have.status(404);
});
```

**Result**: ✅ PASS

---

### Transaction Endpoints

#### POST /api/transactions/buy

**Test Case**: Buy with Sufficient Funds

**Request Body**:
```json
{
  "userId": 100,
  "symbol": "AAPL",
  "quantity": 10,
  "price": 150.00
}
```

**Postman Test**:
```javascript
pm.test("Purchase successful", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    pm.expect(jsonData.message).to.include("success");
});

pm.test("Transaction ID returned", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.transactionId).to.be.a('number');
});
```

**Result**: ✅ PASS

---

#### POST /api/transactions/buy

**Test Case**: Buy with Insufficient Funds

**Request Body**:
```json
{
  "userId": 100,
  "symbol": "AAPL",
  "quantity": 1000,
  "price": 150.00
}
```

**Postman Test**:
```javascript
pm.test("Returns 400 for insufficient funds", function () {
    pm.response.to.have.status(400);
});

pm.test("Error message indicates insufficient funds", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.error).to.include("Insufficient funds");
});
```

**Result**: ✅ PASS

---

## 🤖 Automated Tests

### Backend Unit Tests

**Test Class**: `StockServiceTest.java`

```java
@Test
public void testCalculatePortfolioValue() {
    // Arrange
    Portfolio portfolio = new Portfolio();
    portfolio.setCashBalance(new BigDecimal("2500.00"));
    
    List<Holding> holdings = new ArrayList<>();
    holdings.add(new Holding("AAPL", 50, new BigDecimal("150.00")));
    holdings.add(new Holding("MSFT", 25, new BigDecimal("300.00")));
    
    when(mockStockService.getCurrentPrice("AAPL")).thenReturn(new BigDecimal("155.00"));
    when(mockStockService.getCurrentPrice("MSFT")).thenReturn(new BigDecimal("310.00"));
    
    // Act
    BigDecimal totalValue = portfolioService.calculateTotalValue(portfolio, holdings);
    
    // Assert
    // Cash: 2500 + (50 × 155) + (25 × 310) = 2500 + 7750 + 7750 = 18000
    assertEquals(new BigDecimal("18000.00"), totalValue);
}
```

**Result**: ✅ PASS

---

**Test Class**: `TransactionServiceTest.java`

```java
@Test
public void testBuyStock_SufficientFunds_Success() {
    // Arrange
    User user = createTestUser(1L, new BigDecimal("10000.00"));
    TransactionRequest request = new TransactionRequest("AAPL", 50, new BigDecimal("150.00"));
    
    // Act
    TransactionResult result = transactionService.buyStock(user.getId(), request);
    
    // Assert
    assertTrue(result.isSuccess());
    assertEquals(new BigDecimal("2500.00"), user.getPortfolio().getCashBalance());
    verify(mockHoldingDao).addHolding(any(Holding.class));
}

@Test(expected = InsufficientFundsException.class)
public void testBuyStock_InsufficientFunds_ThrowsException() {
    // Arrange
    User user = createTestUser(1L, new BigDecimal("1000.00"));
    TransactionRequest request = new TransactionRequest("AAPL", 50, new BigDecimal("150.00"));
    
    // Act
    transactionService.buyStock(user.getId(), request);
    
    // Assert - Exception thrown
}
```

**Results**: ✅ Both PASS

---

### Test Coverage Report

```
Package                  Class Coverage    Method Coverage    Line Coverage
---------------------------------------------------------------------------
com.stockmarket.service      95%               88%               82%
com.stockmarket.dao          90%               85%               78%
com.stockmarket.model        100%              100%              100%
com.stockmarket.controller   75%               70%               65%
---------------------------------------------------------------------------
TOTAL                        90%               86%               82%
```

---

## 🐛 Bug Tracking

### Bugs Found & Resolved

#### BUG-001: Portfolio Value Calculation Error
- **Severity**: Critical
- **Status**: ✅ Resolved
- **Description**: Portfolio value not updating after selling stock
- **Root Cause**: Cache not invalidated after sell transaction
- **Fix**: Added cache clear in `sellStock()` method
- **Tested By**: Lisa Lewandowski
- **Test Case**: TC-005 (Sell Stock)

#### BUG-002: Negative Quantity Allowed
- **Severity**: High  
- **Status**: ✅ Resolved
- **Description**: System allowed buying negative quantity of stocks
- **Root Cause**: Missing input validation
- **Fix**: Added server-side validation `quantity > 0`
- **Tested By**: Lisa Lewandowski
- **Test Case**: Added TC-011 (Negative Quantity Test)

#### BUG-003: Decimal Precision Error
- **Severity**: Medium
- **Status**: ✅ Resolved
- **Description**: Cash balance showing $2500.0000001 instead of $2500.00
- **Root Cause**: Floating point arithmetic
- **Fix**: Changed to `BigDecimal` with `.setScale(2, RoundingMode.HALF_UP)`
- **Tested By**: Lisa Lewandowski

#### BUG-004: Concurrent Transaction Race Condition
- **Severity**: Critical
- **Status**: ✅ Resolved
- **Description**: Two simultaneous buy requests could overdraw account
- **Root Cause**: No database-level locking
- **Fix**: Implemented optimistic locking with `@Version` annotation
- **Tested By**: Lisa Lewandowski
- **Test Case**: Added TC-012 (Concurrent Transaction Test)

---

## 📊 Quality Metrics

### Defect Density
- **Total Bugs Found**: 12
- **Critical**: 3
- **High**: 4
- **Medium**: 4
- **Low**: 1
- **Bugs Resolved**: 12 (100%)

### Test Execution Summary
- **Total Test Cases**: 45
- **Passed**: 43
- **Failed**: 0
- **Blocked**: 2 (pending features)
- **Pass Rate**: 95.6%

### Test Effort
- **Total Testing Hours**: 60 hours
- **Manual Testing**: 35 hours
- **Automated Test Development**: 20 hours
- **Regression Testing**: 5 hours

---

## 👥 User Acceptance Testing (UAT)

### UAT Session 1 - Stakeholder Feedback

**Date**: Sprint 2 Review  
**Participants**: Product Owner, 3 end users, development team

**Test Scenarios**:
1. Complete buy/sell workflow
2. View leaderboard and rankings
3. Check transaction history

**Feedback Summary**:
- ✅ Trading interface intuitive
- ✅ Portfolio calculations accurate
- ⚠️ Request: Add price alerts (added to backlog)
- ⚠️ Request: Historical charts (added to backlog)

**Acceptance Criteria Met**: Yes - All critical features accepted

---

## 🎯 Conclusion

The Virtual Stock Market application has undergone rigorous testing across multiple dimensions:

- **Functional Testing**: All core trading, portfolio, and competition features validated
- **API Testing**: Comprehensive Postman test suite with 100% endpoint coverage
- **Security Testing**: Authentication and authorization mechanisms verified
- **Edge Case Testing**: Insufficient funds, invalid symbols, and boundary conditions tested
- **Bug Resolution**: 100% of discovered defects resolved

**Overall Quality Assessment**: Production-ready with 82% code coverage and 95.6% test pass rate.

---

**Tested By**: Lisa Marie Lewandowski  
**Role**: QA Engineer / Full-Stack Developer  
**Contact**: lewandowski.lisa@gmail.com  
**GitHub**: github.com/L2LML
