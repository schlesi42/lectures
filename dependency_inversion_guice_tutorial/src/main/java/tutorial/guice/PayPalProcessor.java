package tutorial.guice;

/**
 * PayPal implementation of PaymentProcessor.
 */
public class PayPalProcessor implements PaymentProcessor {
    @Override
    public void charge(double amount) {
        System.out.println("  → Charging $" + amount + " using PayPal API");
        // Simulated PayPal API call
    }
    
    @Override
    public String getName() {
        return "PayPal";
    }
}





