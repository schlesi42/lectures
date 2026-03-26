package tutorial.di_manual;

/**
 * ✅ GOOD: PaymentService with dependency inversion.
 * 
 * Benefits:
 * - Depends on PaymentProcessor interface, not concrete class
 * - Dependencies injected via constructor
 * - Easy to test (can inject mock)
 * - Easy to change implementations
 * - Follows Dependency Inversion Principle
 */
public class PaymentService {
    private final PaymentProcessor processor;
    private final EmailService emailService;
    
    // Constructor injection
    public PaymentService(PaymentProcessor processor, EmailService emailService) {
        this.processor = processor;
        this.emailService = emailService;
    }
    
    public void processPayment(double amount, String customerEmail) {
        System.out.println("Processing payment of $" + amount);
        
        // Process payment
        processor.charge(amount);
        
        // Send confirmation email
        emailService.sendEmail(
            customerEmail,
            "Payment Confirmation",
            "Your payment of $" + amount + " has been processed successfully."
        );
    }
}





