import logging
import os

# Create a directory for logs if it doesn't exist
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Define the log file path
log_file = os.path.join(log_dir, "application.log")

# Create a logging format that includes the line number
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configure the logger to output to both the terminal and a log file
logging.basicConfig(
    level=logging.DEBUG,  # This will log both DEBUG, INFO, WARNING, ERROR, and CRITICAL levels
    format=log_format,    # Format includes time, log level, message, and source of the log
    handlers=[
        logging.StreamHandler(),  # Output logs to the terminal
        logging.FileHandler(log_file)  # Output logs to a file
    ]
)

# Create a logger instance
logger = logging.getLogger("2WinAlerts-test")

