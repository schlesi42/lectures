package tutorial.guice;

import com.google.inject.Guice;
import com.google.inject.Injector;

/**
 * Main class demonstrating Google Guice dependency injection.
 */
public class Main {
    public static void main(String[] args) {
        System.out.println("=== Google Guice Dependency Injection ===");
        System.out.println();
        
        // Create Guice injector with our module
        Injector injector = Guice.createInjector(new PaymentModule());
        
        System.out.println("Guice injector created with PaymentModule");
        System.out.println();
        
        // Get instance from Guice - dependencies are automatically injected!
        PaymentService paymentService = injector.getInstance(PaymentService.class);
        
        // Process a payment
        paymentService.processPayment(100.0, "customer@example.com");
        
        System.out.println();
        System.out.println("--- Creating another PaymentService instance ---");
        
        // Get another instance
        PaymentService paymentService2 = injector.getInstance(PaymentService.class);
        paymentService2.processPayment(200.0, "another@example.com");
        
        System.out.println();
        System.out.println("Note: EmailService is a singleton, so email count continues from previous instance");
        
        // Verify singleton behavior
        SmtpEmailService emailService = injector.getInstance(SmtpEmailService.class);
        System.out.println("Total emails sent: " + emailService.getEmailCount());
        
        System.out.println();
        System.out.println("✅ Benefits of Guice:");
        System.out.println("   - No manual wiring needed");
        System.out.println("   - Automatic dependency injection");
        System.out.println("   - Type-safe configuration");
        System.out.println("   - Easy to test (can create test modules)");
        System.out.println("   - Supports scopes (Singleton, etc.)");
    }
}





