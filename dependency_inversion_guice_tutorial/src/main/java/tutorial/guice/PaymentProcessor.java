package tutorial.guice;

/**
 * Payment processor interface (abstraction).
 */
public interface PaymentProcessor {
    void charge(double amount);
    String getName();
}





