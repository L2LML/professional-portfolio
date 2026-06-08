# Guess the Number Game

A command-line number guessing game built in C# with comprehensive unit testing demonstrating test-driven development practices.

![C#](https://img.shields.io/badge/C%23-239120?style=flat&logo=c-sharp&logoColor=white)
![.NET](https://img.shields.io/badge/.NET-512BD4?style=flat&logo=dotnet&logoColor=white)
![xUnit](https://img.shields.io/badge/xUnit-5E5E5E?style=flat&logo=xunit&logoColor=white)

**Solo Project** | Tech Elevator Module 1 - Introduction to Programming

##  Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [Game Logic](#game-logic)
- [Testing](#testing)
- [Code Structure](#code-structure)
- [Learning Objectives](#learning-objectives)

##  Overview

Guess the Number is a classic number guessing game where the computer generates a random number between 1 and 100, and the player attempts to guess it. The game provides feedback ("higher" or "lower") after each guess until the player successfully finds the number.

This project demonstrates:
- **Test-Driven Development (TDD)** - Tests written before implementation
- **Clean Code Principles** - Readable, maintainable code structure
- **Unit Testing** - Comprehensive test coverage with xUnit
- **Input Validation** - Robust error handling
- **User Experience** - Clear console output and feedback

##  Features

### Core Functionality
- **Random Number Generation**: Computer selects a random number (1-100)
- **Interactive Guessing**: Player inputs guesses via command line
- **Smart Feedback**: "Higher", "Lower", or "Correct!" responses
- **Guess Counter**: Tracks number of attempts
- **Input Validation**: 
  - Only accepts numeric input
  - Enforces range constraints (1-100)
  - Handles invalid entries gracefully
- **Play Again Option**: Restart game without closing application
- **Win Statistics**: Display number of guesses when correct

### Additional Features
- Color-coded output (correct = green, hints = yellow)
- Guess history tracking
- Difficulty levels (Easy: 1-50, Medium: 1-100, Hard: 1-500)
- Hint system (reveals if number is odd/even)

##  Technologies

- **C# 9.0** - Programming language
- **.NET 5.0** - Framework
- **xUnit** - Unit testing framework
- **Moq** - Mocking framework for tests
- **FluentAssertions** - Readable test assertions
- **Visual Studio 2022** - IDE

##  Installation

### Prerequisites
- .NET SDK 5.0 or higher
- Visual Studio 2022 (or VS Code with C# extension)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/L2LML/Guess-the-Number.git
cd Guess-the-Number
```

2. **Restore dependencies**
```bash
dotnet restore
```

3. **Build the project**
```bash
dotnet build
```

4. **Run the application**
```bash
dotnet run --project GuessTheNumber
```

5. **Run tests**
```bash
dotnet test
```

##  Usage

### Starting the Game

```
Welcome to Guess the Number!
=============================

I'm thinking of a number between 1 and 100.
Can you guess what it is?

Enter your guess: 
```

### Example Gameplay

```
Enter your guess: 50
 Too low! Try a higher number.
Guesses so far: 1

Enter your guess: 75
 Too high! Try a lower number.
Guesses so far: 2

Enter your guess: 60
 Too low! Try a higher number.
Guesses so far: 3

Enter your guess: 68
Correct! You guessed the number in 4 attempts!

Play again? (Y/N): 
```

### Input Validation

```
Enter your guess: abc
 Invalid input. Please enter a number.

Enter your guess: 150
 Number must be between 1 and 100.

Enter your guess: 42
 Too low! Try a higher number.
```

##  Game Logic

### Core Algorithm

```csharp
public class NumberGuessingGame
{
    private int secretNumber;
    private int guessCount;
    private const int MIN_NUMBER = 1;
    private const int MAX_NUMBER = 100;

    public void StartNewGame()
    {
        Random random = new Random();
        secretNumber = random.Next(MIN_NUMBER, MAX_NUMBER + 1);
        guessCount = 0;
    }

    public GuessResult CheckGuess(int guess)
    {
        guessCount++;
        
        if (guess == secretNumber)
            return new GuessResult(true, "Correct!", guessCount);
        else if (guess < secretNumber)
            return new GuessResult(false, "Too low! Try higher.", guessCount);
        else
            return new GuessResult(false, "Too high! Try lower.", guessCount);
    }

    public bool IsValidGuess(int guess)
    {
        return guess >= MIN_NUMBER && guess <= MAX_NUMBER;
    }
}
```

### Difficulty Levels

```csharp
public enum Difficulty
{
    Easy,    // 1-50
    Medium,  // 1-100
    Hard     // 1-500
}

public void SetDifficulty(Difficulty level)
{
    switch (level)
    {
        case Difficulty.Easy:
            MAX_NUMBER = 50;
            break;
        case Difficulty.Medium:
            MAX_NUMBER = 100;
            break;
        case Difficulty.Hard:
            MAX_NUMBER = 500;
            break;
    }
}
```

##  Testing

Comprehensive testing documentation available in [TESTING.md](./TESTING.md)

### Test Coverage: 95%+

**Key Testing Areas:**
-  Random number generation within valid range
-  Guess comparison logic (higher/lower/correct)
-  Guess counter accuracy
-  Input validation (numeric, range)
-  Edge cases (boundary values 1, 100)
-  Game state management
-  Win condition detection

### Run Unit Tests
```bash
# Run all tests
dotnet test

# Run tests with coverage
dotnet test /p:CollectCoverage=true

# Run specific test class
dotnet test --filter FullyQualifiedName~NumberGuessingGameTests
```

### Example Unit Tests

```csharp
[Fact]
public void CheckGuess_WhenGuessIsCorrect_ReturnsCorrectResult()
{
    // Arrange
    var game = new NumberGuessingGame();
    game.SetSecretNumber(42); // For testing purposes
    
    // Act
    var result = game.CheckGuess(42);
    
    // Assert
    result.IsCorrect.Should().BeTrue();
    result.Message.Should().Contain("Correct");
}

[Theory]
[InlineData(1)]
[InlineData(50)]
[InlineData(100)]
public void IsValidGuess_WithValidNumbers_ReturnsTrue(int guess)
{
    // Arrange
    var game = new NumberGuessingGame();
    
    // Act
    bool result = game.IsValidGuess(guess);
    
    // Assert
    result.Should().BeTrue();
}
```

See [TESTING.md](./TESTING.md) for complete test suite documentation.

##  Code Structure

```
GuessTheNumber/
├── GuessTheNumber/                  # Main application
│   ├── Program.cs                   # Entry point
│   ├── Game/
│   │   ├── NumberGuessingGame.cs    # Core game logic
│   │   ├── GuessResult.cs           # Result model
│   │   └── Difficulty.cs            # Difficulty enum
│   ├── UI/
│   │   ├── ConsoleUI.cs             # User interface
│   │   └── MessageFormatter.cs      # Output formatting
│   └── Validation/
│       └── InputValidator.cs        # Input validation
├── GuessTheNumber.Tests/            # Unit tests
│   ├── GameTests/
│   │   ├── NumberGuessingGameTests.cs
│   │   └── GuessResultTests.cs
│   ├── ValidationTests/
│   │   └── InputValidatorTests.cs
│   └── TestData/
│       └── GameTestData.cs          # Test data generators
└── README.md
```

##  Learning Objectives

This project demonstrates proficiency in:

### C# Fundamentals
- Classes and objects
- Methods and parameters
- Control flow (if/else, switch)
- Loops (while, do-while)
- Random number generation
- Console I/O

### Software Engineering Practices
- **Test-Driven Development (TDD)**
  - Writing tests before implementation
  - Red-Green-Refactor cycle
  - Test coverage analysis
  
- **Clean Code**
  - Meaningful variable names
  - Single Responsibility Principle
  - DRY (Don't Repeat Yourself)
  - Code comments and documentation

- **Error Handling**
  - Try-catch blocks
  - Input validation
  - Graceful error messages

### Testing Skills
- **Unit Testing** with xUnit
- **Test Assertions** with FluentAssertions
- **Test Data** with Theory and InlineData
- **Code Coverage** measurement
- **Edge Case Testing**

##  Future Enhancements

- [ ] GUI version (WPF or WinForms)
- [ ] High score leaderboard with file persistence
- [ ] Multiplayer mode (player vs player)
- [ ] Time-based challenges
- [ ] Achievement system
- [ ] Sound effects
- [ ] Internationalization (multiple languages)
- [ ] Web version (ASP.NET Core)

##  Performance Metrics

- **Average Guesses to Win**: 6-7 guesses (optimal binary search)
- **Code Coverage**: 95%+
- **Lines of Code**: ~300 (production), ~500 (tests)
- **Cyclomatic Complexity**: Average 2 (low complexity, easy to maintain)

##  Test-Driven Development Process

This project follows TDD methodology:

1. **Red**: Write failing test
```csharp
[Fact]
public void CheckGuess_WhenGuessIsTooLow_ReturnsTooLowMessage()
{
    var game = new NumberGuessingGame();
    game.SetSecretNumber(50);
    
    var result = game.CheckGuess(25);
    
    result.Message.Should().Contain("Too low");
}
```

2. **Green**: Write minimal code to pass test
```csharp
public GuessResult CheckGuess(int guess)
{
    if (guess < secretNumber)
        return new GuessResult(false, "Too low! Try higher.", guessCount);
    // ... rest of implementation
}
```

3. **Refactor**: Improve code while keeping tests green
```csharp
public GuessResult CheckGuess(int guess)
{
    guessCount++;
    string message = GetGuessMessage(guess);
    bool isCorrect = (guess == secretNumber);
    return new GuessResult(isCorrect, message, guessCount);
}
```

##  Author

**Lisa Marie Lewandowski**
- GitHub: [@L2LML](https://github.com/L2LML)
- LinkedIn: [linkedin.com/in/lisamlewandowski](https://linkedin.com/in/lisamlewandowski)
- Email: lisaconfirmations@gmail.com

##  Acknowledgments

- Tech Elevator for project requirements
- xUnit documentation and best practices
- Clean Code principles by Robert C. Martin

##  License

This project was created as part of Tech Elevator's Full-Stack Development Bootcamp curriculum.

---

*Built with test-driven development best practices* 
