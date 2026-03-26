package tutorial.guice;

import jakarta.inject.Inject;

/**
 * PaymentService using Guice dependency injection.
 * 
 * Guice automatically injects dependencies through:
 * - Constructor injection (preferred)
 * - Field injection
 * - Method injection
 */
public class PaymentService {
    private final PaymentProcessor processor;
    private final EmailService emailService;
    
    /**
     * Constructor injection with @Inject annotation.
     * Guice will automatically provide the dependencies.
     */
    @Inject
    public PaymentService(PaymentProcessor processor, EmailService emailService) {
        this.processor = processor;
        this.emailService = emailService;
        System.out.println("PaymentService created with processor: " + processor.getName());
    }
    
    public void processPayment(double amount, String customerEmail) {
        System.out.println("\nProcessing payment of $" + amount);
        
        // Process payment
        processor.charge(amount);
        
        // Send confirmation email
        emailService.sendEmail(
            customerEmail,
            "Payment Confirmation",
            "Your payment of $" + amount + " has been processed successfully."
        );
    }
    
    public PaymentProcessor getProcessor() {
        return processor;
    }
}

