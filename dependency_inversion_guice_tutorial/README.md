# Dependency Inversion Principle and Guice Tutorial

## Table of Contents
1. [Introduction](#introduction)
2. [The Problem](#the-problem)
3. [Dependency Inversion Principle](#dependency-inversion-principle)
4. [Manual Dependency Injection](#manual-dependency-injection)
5. [Google Guice Framework](#google-guice-framework)
6. [Advanced Guice Features](#advanced-guice-features)
7. [Best Practices](#best-practices)
8. [Summary](#summary)

## Introduction

This tutorial demonstrates the **Dependency Inversion Principle** (DIP) and how to implement it using **Google Guice**, a dependency injection framework for Java.

### What is Dependency Inversion?

The Dependency Inversion Principle states:
- **High-level modules** should not depend on **low-level modules**. Both should depend on **abstractions**.
- **Abstractions** should not depend on details. **Details** should depend on abstractions.

### Why Use Guice?

Guice simplifies dependency injection by:
- Eliminating boilerplate code
- Providing compile-time type safety
- Making dependencies explicit and testable
- Enabling modular design

## The Problem

Let's start with a common anti-pattern: tight coupling between components.

### Example: E-Commerce Payment System

Consider an e-commerce application that processes payments. Without dependency inversion:

```java
// ❌ BAD: Tight coupling
public class PaymentService {
    private CreditCardProcessor processor;
    
    public PaymentService() {
        this.processor = new StripeProcessor();  // Hard-coded dependency!
    }
    
    public void processPayment(double amount) {
        processor.charge(amount);
    }
}
```

**Problems:**
- Hard to test (can't easily mock the processor)
- Hard to change (must modify code to switch processors)
- Violates Open/Closed Principle
- Creates tight coupling

See `src/main/java/tutorial/problem/` for complete examples.

## Dependency Inversion Principle

DIP requires that we:
1. Define **interfaces** (abstractions) for dependencies
2. High-level modules depend on interfaces, not implementations
3. Inject dependencies rather than creating them

### Refactored Example

```java
// ✅ GOOD: Dependency on abstraction
public interface PaymentProcessor {
    void charge(double amount);
}

public class PaymentService {
    private PaymentProcessor processor;
    
    // Constructor injection
    public PaymentService(PaymentProcessor processor) {
        this.processor = processor;
    }
    
    public void processPayment(double amount) {
        processor.charge(amount);
    }
}
```

Now:
- ✅ Easy to test (can inject mock processor)
- ✅ Easy to change implementations
- ✅ Follows SOLID principles
- ✅ Loose coupling

See `src/main/java/tutorial/di_manual/` for manual dependency injection examples.

## Manual Dependency Injection

While dependency inversion improves design, manually wiring dependencies can become tedious:

```java
// Manual wiring
PaymentProcessor processor = new StripeProcessor();
PaymentService service = new PaymentService(processor);
EmailService emailService = new EmailService();
OrderService orderService = new OrderService(service, emailService);
// ... and so on
```

**Problems with manual DI:**
- Verbose setup code
- Easy to make mistakes
- Hard to manage lifecycle
- Difficult to handle circular dependencies

## Google Guice Framework

Guice automates dependency injection, making your code cleaner and more maintainable.

### Basic Setup

1. **Add Guice dependency** (Maven):
```xml
<dependency>
    <groupId>com.google.inject</groupId>
    <artifactId>guice</artifactId>
    <version>7.0.0</version>
</dependency>
```

2. **Create a Module** to configure bindings:
```java
public class PaymentModule extends AbstractModule {
    @Override
    protected void configure() {
        bind(PaymentProcessor.class).to(StripeProcessor.class);
    }
}
```

3. **Create an Injector** and use it:
```java
Injector injector = Guice.createInjector(new PaymentModule());
PaymentService service = injector.getInstance(PaymentService.class);
```

### Key Concepts

#### 1. Bindings

Bindings tell Guice how to create instances:

```java
// Simple binding
bind(PaymentProcessor.class).to(StripeProcessor.class);

// Binding with annotation
bind(PaymentProcessor.class)
    .annotatedWith(Names.named("Stripe"))
    .to(StripeProcessor.class);

// Binding to instance
bind(PaymentProcessor.class).toInstance(new StripeProcessor());

// Binding to provider
bind(PaymentProcessor.class).toProvider(StripeProcessorProvider.class);
```

#### 2. Constructor Injection

Guice automatically injects dependencies through constructors:

```java
public class PaymentService {
    private final PaymentProcessor processor;
    private final EmailService emailService;
    
    @Inject
    public PaymentService(PaymentProcessor processor, 
                         EmailService emailService) {
        this.processor = processor;
        this.emailService = emailService;
    }
}
```

#### 3. Field and Method Injection

```java
public class PaymentService {
    @Inject
    private PaymentProcessor processor;
    
    @Inject
    public void setEmailService(EmailService emailService) {
        this.emailService = emailService;
    }
}
```

#### 4. Provider Pattern

For complex object creation:

```java
public class PaymentProcessorProvider implements Provider<PaymentProcessor> {
    @Override
    public PaymentProcessor get() {
        // Complex initialization logic
        return new StripeProcessor(apiKey, timeout);
    }
}
```

#### 5. Scopes

Control object lifecycle:

```java
// Singleton (one instance per application)
bind(PaymentProcessor.class).to(StripeProcessor.class).in(Singleton.class);

// Request scope (per HTTP request)
bind(PaymentProcessor.class).to(StripeProcessor.class).in(RequestScoped.class);
```

### Complete Example

See `src/main/java/tutorial/guice/` for complete working examples.

## Advanced Guice Features

### 1. Named Bindings

Distinguish between multiple implementations:

```java
// In module
bind(PaymentProcessor.class)
    .annotatedWith(Names.named("Stripe"))
    .to(StripeProcessor.class);
    
bind(PaymentProcessor.class)
    .annotatedWith(Names.named("PayPal"))
    .to(PayPalProcessor.class);

// In usage
@Inject
public PaymentService(@Named("Stripe") PaymentProcessor processor) {
    this.processor = processor;
}
```

### 2. Custom Annotations

Create type-safe annotations:

```java
@BindingAnnotation
@Target({ElementType.FIELD, ElementType.PARAMETER, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface Stripe {}

// Usage
bind(PaymentProcessor.class)
    .annotatedWith(Stripe.class)
    .to(StripeProcessor.class);
```

### 3. Optional Dependencies

```java
@Inject(optional = true)
private Optional<EmailService> emailService;
```

### 4. Multi-binding

Bind multiple implementations:

```java
Multibinder<PaymentProcessor> processorBinder = 
    Multibinder.newSetBinder(binder(), PaymentProcessor.class);
processorBinder.addBinding().to(StripeProcessor.class);
processorBinder.addBinding().to(PayPalProcessor.class);

// Inject as Set
@Inject
private Set<PaymentProcessor> processors;
```

### 5. Assisted Injection

For dependencies that need constructor parameters:

```java
public interface PaymentServiceFactory {
    PaymentService create(String currency);
}

// In module
install(new FactoryModuleBuilder()
    .build(PaymentServiceFactory.class));
```

## Best Practices

1. **Prefer Constructor Injection**
   - Makes dependencies explicit
   - Enables immutability
   - Easier to test

2. **Use Interfaces for Dependencies**
   - Enables flexibility
   - Improves testability

3. **Organize Modules by Feature**
   - Keep modules focused
   - Makes configuration manageable

4. **Use Scopes Appropriately**
   - Singleton for stateless services
   - Request scope for request-specific data

5. **Avoid Service Locator Pattern**
   - Use injection, not lookup

6. **Keep Modules Simple**
   - One module per feature or layer

## Summary

### Benefits of Dependency Inversion + Guice

✅ **Testability**: Easy to inject mocks  
✅ **Flexibility**: Change implementations without modifying code  
✅ **Maintainability**: Clear dependencies and responsibilities  
✅ **Modularity**: Loose coupling between components  
✅ **Type Safety**: Compile-time checking of dependencies  

### Key Takeaways

1. Depend on abstractions, not implementations
2. Inject dependencies, don't create them
3. Use Guice to automate dependency wiring
4. Keep modules focused and organized
5. Leverage Guice features for complex scenarios

## Running the Examples

### Prerequisites
- Java 8 or higher
- Maven 3.6 or higher

### Build and Run

```bash
cd dependency_inversion_guice_tutorial
mvn clean compile
mvn exec:java -Dexec.mainClass="tutorial.guice.Main"
```

### Run Tests

```bash
mvn test
```

## Further Reading

- [Guice User's Guide](https://github.com/google/guice/wiki)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)





