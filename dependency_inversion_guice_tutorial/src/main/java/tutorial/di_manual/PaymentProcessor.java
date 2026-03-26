package tutorial.di_manual;

/**
 * ✅ GOOD: Interface (abstraction) for payment processing.
 * This follows the Dependency Inversion Principle.
 */
public interface PaymentProcessor {
    void charge(double amount);
}





