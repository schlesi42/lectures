package tutorial.problem;

/**
 * Tightly coupled payment processor implementation.
 * This is a concrete class, not an interface.
 */
public class CreditCardProcessor {
    public void charge(double amount) {
        System.out.println("Charging " + amount + " using CreditCardProcessor");
        // Simulated payment processing
    }
}





