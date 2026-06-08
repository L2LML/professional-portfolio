# Virtual Stock Market - Technical Documentation

A real-time stock trading simulation game (Market 25) where users can buy and sell stocks using current market data within customized time intervals.

![Java](https://img.shields.io/badge/Java-ED8B00?style=flat&logo=java&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-35495E?style=flat&logo=vue.js&logoColor=4FC08D)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)
![Agile](https://img.shields.io/badge/Agile-Scrum-blue)

**Team Capstone Project** | Tech Elevator Full-Stack Development Bootcamp

>  For user walkthrough and demo flow, see [README.md](./README.md)  
>  For comprehensive testing documentation, see [TESTING.md](./TESTING.md)

##  Table of Contents
- [Overview](#overview)
- [Technologies](#technologies)
- [Architecture](#architecture)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Team & Development Process](#team--development-process)
- [Future Enhancements](#future-enhancements)

##  Overview

Market 25 is a full-stack web application that simulates competitive stock trading using live market data from the Market Stack API. Users can create custom time-limited trading games, invite other players via email, and compete to achieve the highest portfolio value before the game ends.

### Key Highlights
- **25 Real Stocks**: Live price data for 25 different stocks
- **Multi-Game Support**: Users can participate in multiple concurrent games
- **Game Creation**: Create custom games with unique names and end dates
- **Email Invitations**: Invite other users to join your games
- **Multiple Portfolios**: Separate portfolio for each game you join
- **Starting Balance**: $100,000 virtual cash per game
- **Auto-Liquidation**: All positions automatically close when game ends
- **Real-Time Leaderboard**: Track your ranking against competitors
- **Team Development**: Built using Agile/Scrum methodologies

##  Technologies

### Backend
- **Java 11** - Core application logic
- **Spring Boot 2.7** - RESTful API framework
- **Spring Security** - Authentication and authorization
- **PostgreSQL** - Relational database
- **JDBC & DAO Pattern** - Data access layer
- **Maven** - Dependency management

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Axios** - HTTP client for API calls
- **Vue Router** - Client-side routing
- **Vuex** - State management
- **Bootstrap/CSS3** - Responsive styling

### External APIs
- **Market Stack API** - Real-time stock market data for 25 stocks

### Development Tools
- **Git/GitHub** - Version control
- **Postman** - API testing
- **pgAdmin** - Database management
- **IntelliJ IDEA** - Java IDE
- **VS Code** - Frontend development

##  Architecture

```
virtual-stock-market/
├── backend/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/stockmarket/
│   │   │   │   ├── controller/          # REST controllers
│   │   │   │   ├── dao/                 # Data Access Objects
│   │   │   │   ├── model/               # Entity classes
│   │   │   │   │   ├── User.java
│   │   │   │   │   ├── Game.java
│   │   │   │   │   ├── Portfolio.java
│   │   │   │   │   ├── Stock.java
│   │   │   │   │   ├── Transaction.java
│   │   │   │   │   └── Invitation.java
│   │   │   │   ├── service/             # Business logic
│   │   │   │   ├── security/            # JWT & authentication
│   │   │   │   └── exception/           # Custom exceptions
│   │   │   └── resources/
│   │   │       ├── application.properties
│   │   │       └── schema.sql
│   │   └── test/                        # Unit & integration tests
│   └── pom.xml
├── frontend/
│   ├── src/
│   │   ├── components/                  # Vue components
│   │   │   ├── GameList.vue
│   │   │   ├── Leaderboard.vue
│   │   │   ├── Portfolio.vue
│   │   │   ├── InvitationManager.vue
│   │   │   └── StockTable.vue
│   │   ├── views/                       # Page views
│   │   │   ├── Home.vue
│   │   │   ├── GameDetails.vue
│   │   │   └── PortfolioView.vue
│   │   ├── services/                    # API service layer
│   │   ├── store/                       # Vuex state management
│   │   └── router/                      # Vue Router config
│   └── package.json
└── database/
    ├── schema.sql                       # Database schema
    └── data.sql                         # Seed data
```

##  Installation

### Prerequisites
- Java JDK 11+
- Node.js 14+
- PostgreSQL 12+
- Market Stack API Key ([Get one here](https://marketstack.com/))

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/L2LML/Virtual-Stock-Market.git
cd Virtual-Stock-Market/backend
```

2. **Create PostgreSQL database**
```bash
psql -U postgres
CREATE DATABASE virtual_stock_market;
\q

# Run schema
psql -U postgres -d virtual_stock_market -f database/schema.sql
psql -U postgres -d virtual_stock_market -f database/data.sql
```

3. **Configure application properties**
```properties
# src/main/resources/application.properties
spring.datasource.url=jdbc:postgresql://localhost:5432/virtual_stock_market
spring.datasource.username=postgres
spring.datasource.password=your_password

# Market Stack API
market.api.key=YOUR_MARKET_STACK_API_KEY
market.api.url=http://api.marketstack.com/v1

# JWT Secret
jwt.secret=your_jwt_secret_key
jwt.expiration=86400000
```

4. **Build and run**
```bash
mvn clean install
mvn spring-boot:run
```

Backend runs on: `http://localhost:8080`

### Frontend Setup

1. **Navigate to frontend**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure API endpoint**
```javascript
// src/services/config.js
export const API_BASE_URL = 'http://localhost:8080/api';
```

4. **Run development server**
```bash
npm run serve
```

Frontend runs on: `http://localhost:8081`

##  API Endpoints

### Authentication
```http
POST /api/auth/register          # Register new user
POST /api/auth/login             # User login (returns JWT)
```

### Users
```http
GET  /api/users/{id}             # Get user profile
GET  /api/users/{id}/games       # Get user's games
```

### Games
```http
GET  /api/games                  # List all active games
POST /api/games                  # Create new game
GET  /api/games/{id}             # Get game details
GET  /api/games/{id}/leaderboard # Get game leaderboard
DELETE /api/games/{id}           # Delete game (organizer only)
```

**Example Create Game Request:**
```json
{
  "name": "Spring Championship 2026",
  "organizerId": 1,
  "startDate": "2026-03-01T00:00:00",
  "endDate": "2026-03-31T23:59:59",
  "startingBalance": 100000.00
}
```

### Invitations
```http
POST /api/invitations            # Send game invitation
GET  /api/invitations/user/{id}  # Get user's pending invitations
PUT  /api/invitations/{id}/accept # Accept invitation
PUT  /api/invitations/{id}/decline # Decline invitation
```

**Example Invitation Request:**
```json
{
  "gameId": 5,
  "inviterEmail": "user@example.com",
  "inviteeEmail": "friend@example.com"
}
```

### Portfolios
```http
GET  /api/portfolios/user/{userId}/game/{gameId}  # Get portfolio for specific game
GET  /api/portfolios/{id}/holdings                # Get portfolio holdings
```

### Stocks
```http
GET  /api/stocks                      # Get all 25 stocks
GET  /api/stocks/search?symbol={ticker} # Search stock by symbol
GET  /api/stocks/{symbol}/quote       # Get real-time quote
GET  /api/stocks/refresh              # Refresh all stock prices
```

**Stock Response Example:**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "price": 150.25,
  "change": 2.15,
  "changePercent": 1.45,
  "lastUpdated": "2026-02-17T10:30:00"
}
```

### Transactions
```http
POST /api/transactions/buy       # Buy stock
POST /api/transactions/sell      # Sell stock
GET  /api/transactions/portfolio/{id}/history # Get transaction history
```

**Example Buy Request:**
```json
{
  "portfolioId": 1,
  "symbol": "AAPL",
  "quantity": 10,
  "price": 150.25
}
```

##  Database Schema

### Core Tables

**users**
```sql
id SERIAL PRIMARY KEY
username VARCHAR(50) UNIQUE NOT NULL
email VARCHAR(100) UNIQUE NOT NULL
password_hash VARCHAR(255) NOT NULL
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**games**
```sql
id SERIAL PRIMARY KEY
name VARCHAR(100) UNIQUE NOT NULL
organizer_id INTEGER REFERENCES users(id)
start_date TIMESTAMP NOT NULL
end_date TIMESTAMP NOT NULL
starting_balance DECIMAL(12,2) DEFAULT 100000.00
is_active BOOLEAN DEFAULT true
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**portfolios**
```sql
id SERIAL PRIMARY KEY
user_id INTEGER REFERENCES users(id)
game_id INTEGER REFERENCES games(id)
cash_balance DECIMAL(12,2) DEFAULT 100000.00
total_value DECIMAL(12,2) DEFAULT 100000.00
UNIQUE(user_id, game_id)
```

**holdings**
```sql
id SERIAL PRIMARY KEY
portfolio_id INTEGER REFERENCES portfolios(id)
symbol VARCHAR(10) NOT NULL
quantity INTEGER NOT NULL
average_cost DECIMAL(10,2) NOT NULL
```

**transactions**
```sql
id SERIAL PRIMARY KEY
portfolio_id INTEGER REFERENCES portfolios(id)
symbol VARCHAR(10) NOT NULL
transaction_type VARCHAR(4) NOT NULL  -- 'BUY' or 'SELL'
quantity INTEGER NOT NULL
price DECIMAL(10,2) NOT NULL
timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**invitations**
```sql
id SERIAL PRIMARY KEY
game_id INTEGER REFERENCES games(id)
inviter_id INTEGER REFERENCES users(id)
invitee_email VARCHAR(100) NOT NULL
status VARCHAR(20) DEFAULT 'PENDING'  -- 'PENDING', 'ACCEPTED', 'DECLINED'
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**stocks** (25 stocks tracked)
```sql
id SERIAL PRIMARY KEY
symbol VARCHAR(10) UNIQUE NOT NULL
name VARCHAR(100) NOT NULL
current_price DECIMAL(10,2)
last_updated TIMESTAMP
```

### Key Relationships
- One user can create many games (organizer)
- One user can have many portfolios (one per game joined)
- One game has many portfolios (multiple players)
- One portfolio has many holdings (different stocks)
- One portfolio has many transactions (buy/sell history)
- One game can have many invitations

##  Testing

Comprehensive testing documentation available in [TESTING.md](./TESTING.md)

### Test Coverage
-  Unit Tests: 80%+ coverage
-  Integration Tests: API endpoints
-  Manual Test Cases: User workflows
-  API Testing: Postman collection available

### Run Tests
```bash
# Backend unit tests
cd backend
mvn test

# Frontend tests
cd frontend
npm run test:unit

# Integration tests
mvn verify -P integration-tests
```

**Key Testing Areas:**
- User authentication and authorization
- Game creation and management
- Invitation system (send, accept, decline)
- Stock trading logic (buy/sell validation)
- Portfolio calculation accuracy (per-game isolation)
- API integration with Market Stack
- Database transaction integrity
- Auto-liquidation at game end
- Leaderboard ranking algorithm
- Edge cases (insufficient funds, invalid symbols, game ended)

See [TESTING.md](./TESTING.md) for detailed test cases and QA procedures.

##  Team & Development Process

### Agile/Scrum Methodology
- **Sprint Length**: 2-week sprints
- **Daily Standups**: Team synchronization
- **Sprint Planning**: User story prioritization
- **Sprint Retrospectives**: Continuous improvement
- **Team Size**: 4 developers working collaboratively

### My Contributions
- **API Integration**: Implemented Market Stack API service layer
- **Database Design**: Created schema with multi-game support
- **Testing**: Developed comprehensive test suite
- **Invitation System**: Built email-based invitation workflow
- **Stakeholder Collaboration**: Gathered requirements and feedback
- **Process Documentation**: Created user stories and process flows
- **Issue Tracking**: Documented and resolved bugs

### User Stories Implemented

**User Story 1: New User Registration & Game Creation**
```
As a new user, I want to register for Market 25
  so that I can create and organize stock trading games

Acceptance Criteria:
- User can register with unique email
- User can log in with credentials
- User can create uniquely named games
- User can set custom start and end dates
- User can invite other users via email
- User starts with $100,000 per game
```

**User Story 2: Existing User Game Participation**
```
As an existing user, I want to manage my game invitations
  so that I can join games and compete with other players

Acceptance Criteria:
- User can view pending invitations
- User can accept or decline invitations
- User can see leaderboard for each game
- User can view separate portfolio per game
- User can buy and sell stocks within active games
- User sees updated leaderboard after trades
```

##  Future Enhancements

- [ ] Historical stock price charts (Chart.js integration)
- [ ] Advanced portfolio analytics and metrics
- [ ] Real-time notifications for game updates
- [ ] Social features (follow other traders, share strategies)
- [ ] Mobile app (React Native)
- [ ] Cryptocurrency trading support
- [ ] Paper trading mode for practice
- [ ] Email notifications for invitations and game endings
- [ ] AI-powered trading suggestions
- [ ] Multi-currency support
- [ ] Dark mode theme
- [ ] Export portfolio reports (PDF)
- [ ] Tournament mode with brackets
- [ ] Stock watchlists and alerts

##  Screenshots

*Coming soon - screenshots of game creation, invitation system, leaderboard, and portfolio*

##  Author

**Lisa Marie Lewandowski**
- GitHub: [@L2LML](https://github.com/L2LML)
- LinkedIn: [linkedin.com/in/lisamlewandowski](https://linkedin.com/in/lisamlewandowski)
- Email: lisaconfirmations@gmail.com

##  Acknowledgments

- Tech Elevator for project framework and mentorship
- Market Stack for providing stock market API
- Team members for collaboration and support
- Stakeholders for requirements and feedback

##  License

This project was created as part of Tech Elevator's Full-Stack Development Bootcamp curriculum.

---

*Built with ☕ and teamwork in Detroit Metro*
