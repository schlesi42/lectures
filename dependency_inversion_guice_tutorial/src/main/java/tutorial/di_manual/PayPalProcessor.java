package tutorial.di_manual;

/**
 * PayPal implementation of PaymentProcessor.
 */
public class PayPalProcessor implements PaymentProcessor {
    @Override
    public void charge(double amount) {
        System.out.println("Charging " + amount + " using PayPal");
        // Simulated PayPal API call
    }
}





