package tutorial.problem;

/**
 * ❌ BAD EXAMPLE: PaymentService with tight coupling
 * 
 * Problems:
 * - Hard-coded dependency on CreditCardProcessor
 * - Cannot be easily tested (can't inject mock)
 * - Cannot be easily changed (must modify code)
 * - Violates Dependency Inversion Principle
 */
public class PaymentService {
    private CreditCardProcessor processor;
    
    public PaymentService() {
        // ❌ BAD: Creating dependency directly
        this.processor = new CreditCardProcessor();
    }
    
    public void processPayment(double amount) {
        System.out.println("Processing payment of $" + amount);
        processor.charge(amount);
    }
}





