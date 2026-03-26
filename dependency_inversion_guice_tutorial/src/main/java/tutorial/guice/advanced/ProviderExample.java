package tutorial.guice.advanced;

import com.google.inject.AbstractModule;
import com.google.inject.Guice;
import com.google.inject.Injector;
import com.google.inject.Provider;
import jakarta.inject.Inject;
import tutorial.guice.PaymentProcessor;
import tutorial.guice.StripeProcessor;

/**
 * Example demonstrating Provider pattern in Guice.
 * 
 * Providers are useful when:
 * - Object creation is complex
 * - You need runtime configuration
 * - You want lazy initialization
 */
public class ProviderExample {
    
    // Configuration object
    public static class StripeConfig {
        private final String apiKey;
        private final int timeout;
        
        public StripeConfig(String apiKey, int timeout) {
            this.apiKey = apiKey;
            this.timeout = timeout;
        }
        
        public String getApiKey() { return apiKey; }
        public int getTimeout() { return timeout; }
    }
    
    // Enhanced processor that needs configuration
    public static class ConfigurableStripeProcessor implements PaymentProcessor {
        private final StripeConfig config;
        
        public ConfigurableStripeProcessor(StripeConfig config) {
            this.config = config;
            System.out.println("ConfigurableStripeProcessor created with API key: " + 
                             config.getApiKey().substring(0, 8) + "...");
        }
        
        @Override
        public void charge(double amount) {
            System.out.println("  → Charging $" + amount + " using Stripe (timeout: " + 
                             config.getTimeout() + "ms)");
        }
        
        @Override
        public String getName() {
            return "ConfigurableStripe";
        }
    }
    
    // Provider that creates the processor with configuration
    public static class StripeProcessorProvider implements Provider<PaymentProcessor> {
        @Override
        public PaymentProcessor get() {
            // In real application, this might read from config file, environment, etc.
            StripeConfig config = new StripeConfig("sk_test_12345678", 5000);
            return new ConfigurableStripeProcessor(config);
        }
    }
    
    // Service using the processor
    public static class PaymentService {
        private final PaymentProcessor processor;
        
        @Inject
        public PaymentService(PaymentProcessor processor) {
            this.processor = processor;
        }
        
        public void processPayment(double amount) {
            processor.charge(amount);
        }
    }
    
    // Module using provider
    public static class ProviderModule extends AbstractModule {
        @Override
        protected void configure() {
            bind(PaymentProcessor.class).toProvider(StripeProcessorProvider.class);
        }
    }
    
    public static void main(String[] args) {
        System.out.println("=== Provider Pattern Example ===");
        System.out.println();
        
        Injector injector = Guice.createInjector(new ProviderModule());
        PaymentService service = injector.getInstance(PaymentService.class);
        
        service.processPayment(100.0);
        
        System.out.println();
        System.out.println("Note: Provider allows complex initialization logic");
        System.out.println("and can access configuration at runtime.");
    }
}

