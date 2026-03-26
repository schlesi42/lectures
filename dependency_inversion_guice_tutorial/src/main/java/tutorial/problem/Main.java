package tutorial.problem;

/**
 * Main class demonstrating the problem without dependency inversion.
 */
public class Main {
    public static void main(String[] args) {
        System.out.println("=== Problem: Without Dependency Inversion ===");
        System.out.println();
        
        // Problem: PaymentService is tightly coupled to CreditCardProcessor
        PaymentService paymentService = new PaymentService();
        paymentService.processPayment(100.0);
        
        System.out.println();
        System.out.println("Issues:");
        System.out.println("1. Cannot easily swap CreditCardProcessor with another implementation");
        System.out.println("2. Cannot easily test with a mock processor");
        System.out.println("3. Violates Dependency Inversion Principle");
    }
}





