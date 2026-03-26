package tutorial.di_manual;

/**
 * Main class demonstrating manual dependency injection.
 * 
 * This works, but can become tedious with many dependencies.
 */
public class Main {
    public static void main(String[] args) {
        System.out.println("=== Manual Dependency Injection ===");
        System.out.println();
        
        // Manual wiring of dependencies
        PaymentProcessor processor = new StripeProcessor();
        EmailService emailService = new SmtpEmailService();
        PaymentService paymentService = new PaymentService(processor, emailService);
        
        System.out.println("Using Stripe:");
        paymentService.processPayment(100.0, "customer@example.com");
        
        System.out.println();
        System.out.println("Switching to PayPal:");
        PaymentProcessor paypalProcessor = new PayPalProcessor();
        PaymentService paypalPaymentService = new PaymentService(paypalProcessor, emailService);
        paypalPaymentService.processPayment(150.0, "customer@example.com");
        
        System.out.println();
        System.out.println("Benefits:");
        System.out.println("✅ Flexible - can swap implementations easily");
        System.out.println("✅ Testable - can inject mocks");
        System.out.println("✅ Follows DIP");
        System.out.println();
        System.out.println("But manual wiring can become tedious with many dependencies...");
        System.out.println("That's where Guice comes in!");
    }
}





