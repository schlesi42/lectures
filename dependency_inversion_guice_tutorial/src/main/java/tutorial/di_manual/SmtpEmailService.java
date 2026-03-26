package tutorial.di_manual;

/**
 * SMTP implementation of EmailService.
 */
public class SmtpEmailService implements EmailService {
    @Override
    public void sendEmail(String to, String subject, String body) {
        System.out.println("Sending email via SMTP:");
        System.out.println("  To: " + to);
        System.out.println("  Subject: " + subject);
        System.out.println("  Body: " + body);
    }
}





