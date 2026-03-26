package tutorial.di_manual;

/**
 * Stripe implementation of PaymentProcessor.
 */
public class StripeProcessor implements PaymentProcessor {
    @Override
    public void charge(double amount) {
        System.out.println("Charging " + amount + " using Stripe");
        // Simulated Stripe API call
    }
}





