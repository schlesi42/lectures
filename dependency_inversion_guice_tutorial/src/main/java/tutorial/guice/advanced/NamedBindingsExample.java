package tutorial.guice.advanced;

import com.google.inject.AbstractModule;
import com.google.inject.Guice;
import com.google.inject.Injector;
import com.google.inject.name.Named;
import com.google.inject.name.Names;
import jakarta.inject.Inject;
import tutorial.guice.PaymentProcessor;
import tutorial.guice.PayPalProcessor;
import tutorial.guice.StripeProcessor;

/**
 * Example demonstrating named bindings in Guice.
 * 
 * This allows multiple implementations of the same interface
 * to be distinguished using annotations.
 */
public class NamedBindingsExample {
    
    // Service that needs specific processor implementations
    public static class PaymentController {
        private final PaymentProcessor stripeProcessor;
        private final PaymentProcessor paypalProcessor;
        
        @Inject
        public PaymentController(
                @Named("Stripe") PaymentProcessor stripeProcessor,
                @Named("PayPal") PaymentProcessor paypalProcessor) {
            this.stripeProcessor = stripeProcessor;
            this.paypalProcessor = paypalProcessor;
        }
        
        public void processWithStripe(double amount) {
            System.out.println("Processing with Stripe:");
            stripeProcessor.charge(amount);
        }
        
        public void processWithPayPal(double amount) {
            System.out.println("Processing with PayPal:");
            paypalProcessor.charge(amount);
        }
    }
    
    // Module with named bindings
    public static class NamedPaymentModule extends AbstractModule {
        @Override
        protected void configure() {
            bind(PaymentProcessor.class)
                .annotatedWith(Names.named("Stripe"))
                .to(StripeProcessor.class);
                
            bind(PaymentProcessor.class)
                .annotatedWith(Names.named("PayPal"))
                .to(PayPalProcessor.class);
        }
    }
    
    public static void main(String[] args) {
        System.out.println("=== Named Bindings Example ===");
        System.out.println();
        
        Injector injector = Guice.createInjector(new NamedPaymentModule());
        PaymentController controller = injector.getInstance(PaymentController.class);
        
        controller.processWithStripe(100.0);
        System.out.println();
        controller.processWithPayPal(200.0);
    }
}

