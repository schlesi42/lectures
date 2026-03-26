package tutorial.guice;

import com.google.inject.AbstractModule;
import com.google.inject.Guice;
import com.google.inject.Injector;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests demonstrating how easy it is to test with Guice.
 * 
 * We can create test modules with mock implementations
 * without modifying the production code.
 */
class PaymentServiceTest {
    
    // Mock implementations for testing
    static class MockPaymentProcessor implements PaymentProcessor {
        private double lastAmount = 0;
        private int chargeCount = 0;
        
        @Override
        public void charge(double amount) {
            this.lastAmount = amount;
            this.chargeCount++;
        }
        
        @Override
        public String getName() {
            return "MockProcessor";
        }
        
        public double getLastAmount() {
            return lastAmount;
        }
        
        public int getChargeCount() {
            return chargeCount;
        }
    }
    
    static class MockEmailService implements EmailService {
        private int emailCount = 0;
        private String lastRecipient;
        
        @Override
        public void sendEmail(String to, String subject, String body) {
            this.emailCount++;
            this.lastRecipient = to;
        }
        
        public int getEmailCount() {
            return emailCount;
        }
        
        public String getLastRecipient() {
            return lastRecipient;
        }
    }
    
    // Test module
    static class TestModule extends AbstractModule {
        @Override
        protected void configure() {
            bind(PaymentProcessor.class).to(MockPaymentProcessor.class);
            bind(EmailService.class).to(MockEmailService.class);
        }
    }
    
    private Injector injector;
    private PaymentService paymentService;
    private MockPaymentProcessor mockProcessor;
    private MockEmailService mockEmail;
    
    @BeforeEach
    void setUp() {
        injector = Guice.createInjector(new TestModule());
        paymentService = injector.getInstance(PaymentService.class);
        mockProcessor = injector.getInstance(MockPaymentProcessor.class);
        mockEmail = injector.getInstance(MockEmailService.class);
    }
    
    @Test
    void testProcessPayment() {
        // When
        paymentService.processPayment(100.0, "test@example.com");
        
        // Then
        assertEquals(100.0, mockProcessor.getLastAmount(), 0.01);
        assertEquals(1, mockProcessor.getChargeCount());
        assertEquals(1, mockEmail.getEmailCount());
        assertEquals("test@example.com", mockEmail.getLastRecipient());
    }
    
    @Test
    void testMultiplePayments() {
        // When
        paymentService.processPayment(50.0, "customer1@example.com");
        paymentService.processPayment(75.0, "customer2@example.com");
        
        // Then
        assertEquals(75.0, mockProcessor.getLastAmount(), 0.01);
        assertEquals(2, mockProcessor.getChargeCount());
        assertEquals(2, mockEmail.getEmailCount());
    }
    
    @Test
    void testEmailServiceIsSingleton() {
        // Get another instance
        EmailService emailService2 = injector.getInstance(EmailService.class);
        
        // Should be the same instance (singleton)
        assertSame(mockEmail, emailService2);
    }
}





