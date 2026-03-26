package tutorial.guice;

import jakarta.inject.Singleton;

/**
 * SMTP implementation of EmailService.
 * Annotated as Singleton to ensure only one instance is created.
 */
@Singleton
public class SmtpEmailService implements EmailService {
    private int emailCount = 0;
    
    @Override
    public void sendEmail(String to, String subject, String body) {
        emailCount++;
        System.out.println("  → [Email #" + emailCount + "] Sending email via SMTP:");
        System.out.println("     To: " + to);
        System.out.println("     Subject: " + subject);
    }
    
    public int getEmailCount() {
        return emailCount;
    }
}

