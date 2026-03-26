package tutorial.guice.advanced;

import com.google.inject.AbstractModule;
import com.google.inject.Guice;
import com.google.inject.Injector;
import jakarta.inject.Inject;
import tutorial.guice.EmailService;
import tutorial.guice.PaymentProcessor;
import tutorial.guice.PaymentService;

/**
 * Example demonstrating how to create test modules for unit testing.
 * 
 * This is one of the key benefits of Guice - easy testability!
 */
public class TestModuleExample {
    
    // Mock implementations for testing
    public static class MockPaymentProcessor implements PaymentProcessor {
        private double lastAmount = 0;
        
        @Override
        public void charge(double amount) {
            this.lastAmount = amount;
            System.out.println("  → [MOCK] Would charge $" + amount);
        }
        
        @Override
        public String getName() {
            return "MockProcessor";
        }
        
        public double getLastAmount() {
            return lastAmount;
        }
    }
    
    public static class MockEmailService implements EmailService {
        private int emailCount = 0;
        
        @Override
        public void sendEmail(String to, String subject, String body) {
            emailCount++;
            System.out.println("  → [MOCK] Would send email #" + emailCount + " to " + to);
        }
        
        public int getEmailCount() {
            return emailCount;
        }
    }
    
    // Test module with mock implementations
    public static class TestModule extends AbstractModule {
        @Override
        protected void configure() {
            bind(PaymentProcessor.class).to(MockPaymentProcessor.class);
            bind(EmailService.class).to(MockEmailService.class);
        }
    }
    
    public static void main(String[] args) {
        System.out.println("=== Test Module Example ===");
        System.out.println();
        System.out.println("This demonstrates how easy it is to test with Guice:");
        System.out.println();
        
        // Create injector with test module (mocks)
        Injector injector = Guice.createInjector(new TestModule());
        PaymentService service = injector.getInstance(PaymentService.class);
        
        // Test the service
        service.processPayment(50.0, "test@example.com");
        
        // Verify mock behavior
        MockPaymentProcessor mockProcessor = injector.getInstance(MockPaymentProcessor.class);
        MockEmailService mockEmail = injector.getInstance(MockEmailService.class);
        
        System.out.println();
        System.out.println("Test assertions:");
        System.out.println("  - Last charged amount: $" + mockProcessor.getLastAmount() + 
                         " (expected: $50.0)");
        System.out.println("  - Emails sent: " + mockEmail.getEmailCount() + " (expected: 1)");
        
        System.out.println();
        System.out.println("✅ Benefits:");
        System.out.println("   - No need to modify production code for testing");
        System.out.println("   - Easy to swap implementations");
        System.out.println("   - Can verify interactions with mocks");
    }
}

