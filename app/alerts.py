"""Alert service for threshold monitoring and notifications."""
from flask import current_app
from flask_mail import Message
from app import mail
from app.models import db, AlertRule, AlertHistory, SystemMetric, NetworkMetric, Server
from datetime import datetime, timedelta, timezone
from twilio.rest import Client


def check_and_notify_alerts():
    """Check all active alert rules and send notifications if thresholds are breached."""
    # Get all active alert rules
    alert_rules = AlertRule.query.filter_by(is_active=True).all()
    
    for rule in alert_rules:
        try:
            check_alert_rule(rule)
        except Exception as e:
            current_app.logger.error(f"Error checking alert rule {rule.id}: {e}")


def check_alert_rule(rule):
    """Check a single alert rule and trigger notification if needed."""
    # Determine which servers to check
    if rule.server_id:
        servers = [Server.query.get(rule.server_id)]
    else:
        servers = Server.query.filter_by(is_active=True).all()
    
    for server in servers:
        if not server:
            continue
        
        # Get the latest metric value
        metric_value = get_latest_metric_value(server.id, rule.metric_type)
        
        if metric_value is None:
            continue
        
        # Check if threshold is breached
        if evaluate_threshold(metric_value, rule.threshold, rule.comparison):
            # Check if alert was already triggered recently (within duration)
            recent_alert = AlertHistory.query.filter_by(
                rule_id=rule.id,
                server_id=server.id
            ).filter(
                AlertHistory.triggered_at >= datetime.now(timezone.utc) - timedelta(seconds=rule.duration)
            ).first()
            
            # Only trigger if no recent alert exists
            if not recent_alert:
                trigger_alert(rule, server, metric_value)


def get_latest_metric_value(server_id, metric_type):
    """Get the latest metric value for a specific metric type."""
    if metric_type == 'cpu':
        metric = SystemMetric.query.filter_by(server_id=server_id).order_by(
            SystemMetric.timestamp.desc()
        ).first()
        return metric.cpu_percent if metric else None
    
    elif metric_type == 'memory':
        metric = SystemMetric.query.filter_by(server_id=server_id).order_by(
            SystemMetric.timestamp.desc()
        ).first()
        return metric.memory_percent if metric else None
    
    elif metric_type == 'disk':
        metric = SystemMetric.query.filter_by(server_id=server_id).order_by(
            SystemMetric.timestamp.desc()
        ).first()
        return metric.disk_percent if metric else None
    
    elif metric_type == 'cpu_temp':
        metric = SystemMetric.query.filter_by(server_id=server_id).order_by(
            SystemMetric.timestamp.desc()
        ).first()
        return metric.cpu_temp_c if metric else None
    
    elif metric_type == 'network_sent':
        metric = NetworkMetric.query.filter_by(server_id=server_id).order_by(
            NetworkMetric.timestamp.desc()
        ).first()
        return metric.bytes_sent if metric else None
    
    elif metric_type == 'network_recv':
        metric = NetworkMetric.query.filter_by(server_id=server_id).order_by(
            NetworkMetric.timestamp.desc()
        ).first()
        return metric.bytes_recv if metric else None
    
    return None


def evaluate_threshold(value, threshold, comparison):
    """Evaluate if a value meets the threshold condition."""
    if comparison == '>':
        return value > threshold
    elif comparison == '>=':
        return value >= threshold
    elif comparison == '<':
        return value < threshold
    elif comparison == '<=':
        return value <= threshold
    elif comparison == '==':
        return value == threshold
    return False


def trigger_alert(rule, server, metric_value):
    """Trigger an alert and send notifications."""
    # Create alert history record
    message = f"Alert: {rule.name} - {rule.metric_type} is {metric_value:.2f} (threshold: {rule.comparison} {rule.threshold})"
    
    alert_history = AlertHistory(
        rule_id=rule.id,
        server_id=server.id,
        metric_value=metric_value,
        message=message
    )
    
    # Send email notification
    if rule.notify_email:
        email_sent = send_email_alert(rule, server, metric_value, message)
        alert_history.email_sent = email_sent
    
    # Send SMS notification
    if rule.notify_sms:
        sms_sent = send_sms_alert(rule, server, metric_value, message)
        alert_history.sms_sent = sms_sent
    
    # Send Slack notification
    if rule.notify_slack:
        slack_sent = send_slack_alert(rule, server, metric_value, message)
        alert_history.slack_sent = slack_sent
    
    db.session.add(alert_history)
    db.session.commit()
    
    current_app.logger.info(f"Alert triggered: {message}")


def send_email_alert(rule, server, metric_value, message):
    """Send email alert notification."""
    try:
        # Use rule-specific email or user's email
        recipient = rule.email_address or rule.user.email
        
        msg = Message(
            subject=f"System Monitor Alert: {rule.name}",
            recipients=[recipient],
            body=f"""
System Monitor Alert

Server: {server.name}
Alert Rule: {rule.name}
Metric: {rule.metric_type}
Current Value: {metric_value:.2f}
Threshold: {rule.comparison} {rule.threshold}

Message: {message}

Triggered at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

---
This is an automated alert from System Monitor.
            """.strip()
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending email alert: {e}")
        return False


def send_sms_alert(rule, server, metric_value, message):
    """Send SMS alert notification via Twilio."""
    try:
        # Check if Twilio is configured
        account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        from_number = current_app.config.get('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, from_number]):
            current_app.logger.warning("Twilio not configured, skipping SMS alert")
            return False
        
        # Use rule-specific phone or skip
        to_number = rule.phone_number
        if not to_number:
            current_app.logger.warning("No phone number configured for alert rule")
            return False
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send SMS
        sms_message = f"System Monitor Alert: {rule.name} on {server.name}. {rule.metric_type}={metric_value:.2f} (threshold: {rule.comparison}{rule.threshold})"
        
        client.messages.create(
            body=sms_message,
            from_=from_number,
            to=to_number
        )
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending SMS alert: {e}")
        return False


def test_alert_notification(rule_id, notification_type='email'):
    """Test an alert notification without triggering the actual alert."""
    rule = AlertRule.query.get(rule_id)
    if not rule:
        return False, "Alert rule not found"
    
    server = Server.query.filter_by(is_local=True).first()
    if not server:
        return False, "No server found"
    
    test_message = f"Test alert for rule: {rule.name}"
    
    if notification_type == 'email':
        success = send_email_alert(rule, server, rule.threshold, test_message)
        return success, "Email sent successfully" if success else "Failed to send email"
    elif notification_type == 'sms':
        success = send_sms_alert(rule, server, rule.threshold, test_message)
        return success, "SMS sent successfully" if success else "Failed to send SMS"
    
    return False, "Invalid notification type"


def send_slack_alert(rule, server, metric_value, message):
    """Send alert notification to Slack via webhook."""
    import requests
    import json
    
    try:
        webhook_url = current_app.config.get('SLACK_WEBHOOK_URL')
        
        if not webhook_url:
            current_app.logger.warning("Slack webhook URL not configured")
            return False
        
        # Format Slack message with rich formatting
        slack_message = {
            "text": f"🚨 System Monitor Alert: {rule.name}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 {rule.name}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Server:*\n{server.name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Metric:*\n{rule.metric_type}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Current Value:*\n{metric_value:.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Threshold:*\n{rule.comparison} {rule.threshold}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Message:* {message}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Triggered at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(
            webhook_url,
            data=json.dumps(slack_message),
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            return True
        else:
            current_app.logger.error(f"Slack webhook failed with status {response.status_code}")
            return False
            
    except Exception as e:
        current_app.logger.error(f"Error sending Slack alert: {e}")
        return False
