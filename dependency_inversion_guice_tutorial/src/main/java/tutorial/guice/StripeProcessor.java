package tutorial.guice;

/**
 * Stripe implementation of PaymentProcessor.
 */
public class StripeProcessor implements PaymentProcessor {
    @Override
    public void charge(double amount) {
        System.out.println("  → Charging $" + amount + " using Stripe API");
        // Simulated Stripe API call
    }
    
    @Override
    public String getName() {
        return "Stripe";
    }
}





