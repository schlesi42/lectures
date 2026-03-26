package tutorial.guice;

import com.google.inject.AbstractModule;
import com.google.inject.Singleton;

/**
 * Guice module that configures dependency bindings.
 * 
 * This tells Guice:
 * - Which implementation to use for each interface
 * - What scope to use (Singleton, etc.)
 * - How to create complex objects
 */
public class PaymentModule extends AbstractModule {
    
    @Override
    protected void configure() {
        // Bind PaymentProcessor interface to StripeProcessor implementation
        bind(PaymentProcessor.class).to(StripeProcessor.class);
        
        // EmailService is already annotated with @Singleton,
        // but we can also bind it explicitly here if needed
        // bind(EmailService.class).to(SmtpEmailService.class).in(Singleton.class);
    }
}





