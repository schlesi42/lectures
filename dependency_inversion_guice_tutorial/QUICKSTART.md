# Quick Start Guide

## Prerequisites

- Java 11 or higher
- Maven 3.6 or higher

## Setup

1. **Navigate to the tutorial directory:**
   ```bash
   cd dependency_inversion_guice_tutorial
   ```

2. **Download dependencies:**
   ```bash
   mvn clean install
   ```

## Running Examples

### 1. Problem Example (Without Dependency Inversion)
```bash
mvn exec:java -Dexec.mainClass="tutorial.problem.Main"
```

### 2. Manual Dependency Injection Example
```bash
mvn exec:java -Dexec.mainClass="tutorial.di_manual.Main"
```

### 3. Guice Dependency Injection Example
```bash
mvn exec:java -Dexec.mainClass="tutorial.guice.Main"
```

### 4. Advanced Examples

**Named Bindings:**
```bash
mvn exec:java -Dexec.mainClass="tutorial.guice.advanced.NamedBindingsExample"
```

**Provider Pattern:**
```bash
mvn exec:java -Dexec.mainClass="tutorial.guice.advanced.ProviderExample"
```

**Test Module:**
```bash
mvn exec:java -Dexec.mainClass="tutorial.guice.advanced.TestModuleExample"
```

## Running Tests

```bash
mvn test
```

## Project Structure

```
dependency_inversion_guice_tutorial/
├── src/
│   ├── main/
│   │   └── java/
│   │       └── tutorial/
│   │           ├── problem/          # ❌ Bad: Without DI
│   │           ├── di_manual/        # ✅ Good: Manual DI
│   │           └── guice/            # ✅ Best: Guice DI
│   │               └── advanced/     # Advanced Guice features
│   └── test/
│       └── java/
│           └── tutorial/
│               └── guice/            # Unit tests
├── pom.xml                           # Maven configuration
└── README.md                         # Full tutorial
```

## Learning Path

1. **Start with `tutorial.problem`** - See what problems dependency inversion solves
2. **Review `tutorial.di_manual`** - Understand manual dependency injection
3. **Explore `tutorial.guice`** - Learn how Guice automates DI
4. **Check `tutorial.guice.advanced`** - Learn advanced Guice features
5. **Run tests** - See how easy testing becomes with DI

## Troubleshooting

### Import errors in IDE
The IDE may show import errors until dependencies are downloaded. Run:
```bash
mvn clean install
```

### Java version issues
Ensure you have Java 11 or higher:
```bash
java -version
```

### Maven not found
Install Maven or use your IDE's built-in Maven support.





