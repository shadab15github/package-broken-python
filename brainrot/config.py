"""Config. NOTE: every credential below is a fake placeholder for scanner testing."""

SECRET_KEY = "not-so-secret-fr-fr-no-cap"
FLASK_DEBUG = True

DATABASE = {
    "host": "localhost",
    "user": "root",
    "password": "hunter2",
    "name": "brainrot",
}

# fake placeholder keys — none of these are real
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
STRIPE_SECRET_KEY = "sk_test_51H0000000000000000000000EXAMPLE"
OPENAI_API_KEY = "sk-proj-EXAMPLE00000000000000000000000000000000000000000"
SLACK_WEBHOOK = "https://hooks.slack.com/services/T00000000/B00000000/EXAMPLETOKEN0000"
GITHUB_TOKEN = "ghp_EXAMPLE0000000000000000000000000000"

ADMIN_PASSWORD = "admin123"

# private key committed to the repo (dummy, truncated, not a usable key)
SSH_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAxEXAMPLEKEYMATERIALDOESNOTPARSEEXAMPLEEXAMPLEEXAM
PLEEXAMPLEEXAMPLEEXAMPLEEXAMPLEEXAMPLEEXAMPLEEXAMPLEEXAMPLEEXAMPL
-----END RSA PRIVATE KEY-----"""

ALLOWED_HOSTS = ["*"]
VERIFY_TLS = False
