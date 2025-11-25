"""Alert service for threshold monitoring and notifications."""  # """Alert service for threshold monitoring and notifications."""
from flask import current_app  # from flask import current_app
from flask_mail import Message  # from flask_mail import Message
from app import mail  # from app import mail
from app.models import db, AlertRule, AlertHistory, SystemMetric, NetworkMetric, Server  # from app.models import db, AlertRule, AlertHistory, SystemMetric, NetworkMetric, Server
from datetime import datetime, timedelta  # from datetime import datetime, timedelta
from twilio.rest import Client  # from twilio.rest import Client
  # blank line
  # blank line
def check_and_notify_alerts():  # def check_and_notify_alerts():
    """Check all active alert rules and send notifications if thresholds are breached."""  # """Check all active alert rules and send notifications if thresholds are breached."""
    # Get all active alert rules  # # Get all active alert rules
    alert_rules = AlertRule.query.filter_by(is_active=True).all()  # alert_rules = AlertRule.query.filter_by(is_active=True).all()
      # blank line
    for rule in alert_rules:  # for rule in alert_rules:
        try:  # try:
            check_alert_rule(rule)  # check_alert_rule(rule)
        except Exception as e:  # except Exception as e:
            current_app.logger.error(f"Error checking alert rule {rule.id}: {e}")  # current_app.logger.error(f"Error checking alert rule {rule.id}: {e}")
  # blank line
  # blank line
def check_alert_rule(rule):  # def check_alert_rule(rule):
    """Check a single alert rule and trigger notification if needed."""  # """Check a single alert rule and trigger notification if needed."""
    # Determine which servers to check  # # Determine which servers to check
    if rule.server_id:  # if rule.server_id:
        servers = [Server.query.get(rule.server_id)]  # servers = [Server.query.get(rule.server_id)]
    else:  # else:
        servers = Server.query.filter_by(is_active=True).all()  # servers = Server.query.filter_by(is_active=True).all()
      # blank line
    for server in servers:  # for server in servers:
        if not server:  # if not server:
            continue  # continue
          # blank line
        # Get the latest metric value  # # Get the latest metric value
        metric_value = get_latest_metric_value(server.id, rule.metric_type)  # metric_value = get_latest_metric_value(server.id, rule.metric_type)
          # blank line
        if metric_value is None:  # if metric_value is None:
            continue  # continue
          # blank line
        # Check if threshold is breached  # # Check if threshold is breached
        if evaluate_threshold(metric_value, rule.threshold, rule.comparison):  # if evaluate_threshold(metric_value, rule.threshold, rule.comparison):
            # Check if alert was already triggered recently (within duration)  # # Check if alert was already triggered recently (within duration)
            recent_alert = AlertHistory.query.filter_by(  # recent_alert = AlertHistory.query.filter_by(
                rule_id=rule.id,  # rule_id=rule.id,
                server_id=server.id  # server_id=server.id
            ).filter(  # ).filter(
                AlertHistory.triggered_at >= datetime.utcnow() - timedelta(seconds=rule.duration)  # AlertHistory.triggered_at >= datetime.utcnow() - timedelta(seconds=rule.duration)
            ).first()  # ).first()
              # blank line
            # Only trigger if no recent alert exists  # # Only trigger if no recent alert exists
            if not recent_alert:  # if not recent_alert:
                trigger_alert(rule, server, metric_value)  # trigger_alert(rule, server, metric_value)
  # blank line
  # blank line
def get_latest_metric_value(server_id, metric_type):  # def get_latest_metric_value(server_id, metric_type):
    """Get the latest metric value for a specific metric type."""  # """Get the latest metric value for a specific metric type."""
    if metric_type == 'cpu':  # if metric_type == 'cpu':
        metric = SystemMetric.query.filter_by(server_id=server_id).order_by(  # metric = SystemMetric.query.filter_by(server_id=server_id).order_by(
            SystemMetric.timestamp.desc()  # SystemMetric.timestamp.desc()
        ).first()  # ).first()
        return metric.cpu_percent if metric else None  # return metric.cpu_percent if metric else None
      # blank line
    elif metric_type == 'memory':  # elif metric_type == 'memory':
        metric = SystemMetric.query.filter_by(server_id=server_id).order_by(  # metric = SystemMetric.query.filter_by(server_id=server_id).order_by(
            SystemMetric.timestamp.desc()  # SystemMetric.timestamp.desc()
        ).first()  # ).first()
        return metric.memory_percent if metric else None  # return metric.memory_percent if metric else None
      # blank line
    elif metric_type == 'disk':  # elif metric_type == 'disk':
        metric = SystemMetric.query.filter_by(server_id=server_id).order_by(  # metric = SystemMetric.query.filter_by(server_id=server_id).order_by(
            SystemMetric.timestamp.desc()  # SystemMetric.timestamp.desc()
        ).first()  # ).first()
        return metric.disk_percent if metric else None  # return metric.disk_percent if metric else None
      # blank line
    elif metric_type == 'cpu_temp':  # elif metric_type == 'cpu_temp':
        metric = SystemMetric.query.filter_by(server_id=server_id).order_by(  # metric = SystemMetric.query.filter_by(server_id=server_id).order_by(
            SystemMetric.timestamp.desc()  # SystemMetric.timestamp.desc()
        ).first()  # ).first()
        return metric.cpu_temp_c if metric else None  # return metric.cpu_temp_c if metric else None
      # blank line
    elif metric_type == 'network_sent':  # elif metric_type == 'network_sent':
        metric = NetworkMetric.query.filter_by(server_id=server_id).order_by(  # metric = NetworkMetric.query.filter_by(server_id=server_id).order_by(
            NetworkMetric.timestamp.desc()  # NetworkMetric.timestamp.desc()
        ).first()  # ).first()
        return metric.bytes_sent if metric else None  # return metric.bytes_sent if metric else None
      # blank line
    elif metric_type == 'network_recv':  # elif metric_type == 'network_recv':
        metric = NetworkMetric.query.filter_by(server_id=server_id).order_by(  # metric = NetworkMetric.query.filter_by(server_id=server_id).order_by(
            NetworkMetric.timestamp.desc()  # NetworkMetric.timestamp.desc()
        ).first()  # ).first()
        return metric.bytes_recv if metric else None  # return metric.bytes_recv if metric else None
      # blank line
    return None  # return None
  # blank line
  # blank line
def evaluate_threshold(value, threshold, comparison):  # def evaluate_threshold(value, threshold, comparison):
    """Evaluate if a value meets the threshold condition."""  # """Evaluate if a value meets the threshold condition."""
    if comparison == '>':  # if comparison == '>':
        return value > threshold  # return value > threshold
    elif comparison == '>=':  # elif comparison == '>=':
        return value >= threshold  # return value >= threshold
    elif comparison == '<':  # elif comparison == '<':
        return value < threshold  # return value < threshold
    elif comparison == '<=':  # elif comparison == '<=':
        return value <= threshold  # return value <= threshold
    elif comparison == '==':  # elif comparison == '==':
        return value == threshold  # return value == threshold
    return False  # return False
  # blank line
  # blank line
def trigger_alert(rule, server, metric_value):  # def trigger_alert(rule, server, metric_value):
    """Trigger an alert and send notifications."""  # """Trigger an alert and send notifications."""
    # Create alert history record  # # Create alert history record
    message = f"Alert: {rule.name} - {rule.metric_type} is {metric_value:.2f} (threshold: {rule.comparison} {rule.threshold})"  # message = f"Alert: {rule.name} - {rule.metric_type} is {metric_value:.2f} (threshold: {rule.comparison} {rule.threshold})"
      # blank line
    alert_history = AlertHistory(  # alert_history = AlertHistory(
        rule_id=rule.id,  # rule_id=rule.id,
        server_id=server.id,  # server_id=server.id,
        metric_value=metric_value,  # metric_value=metric_value,
        message=message  # message=message
    )  # )
      # blank line
    # Send email notification  # # Send email notification
    if rule.notify_email:  # if rule.notify_email:
        email_sent = send_email_alert(rule, server, metric_value, message)  # email_sent = send_email_alert(rule, server, metric_value, message)
        alert_history.email_sent = email_sent  # alert_history.email_sent = email_sent
      # blank line
    # Send SMS notification  # # Send SMS notification
    if rule.notify_sms:  # if rule.notify_sms:
        sms_sent = send_sms_alert(rule, server, metric_value, message)  # sms_sent = send_sms_alert(rule, server, metric_value, message)
        alert_history.sms_sent = sms_sent  # alert_history.sms_sent = sms_sent
      # blank line
    # Send Slack notification  # # Send Slack notification
    if rule.notify_slack:  # if rule.notify_slack:
        slack_sent = send_slack_alert(rule, server, metric_value, message)  # slack_sent = send_slack_alert(rule, server, metric_value, message)
        alert_history.slack_sent = slack_sent  # alert_history.slack_sent = slack_sent
      # blank line
    db.session.add(alert_history)  # db.session.add(alert_history)
    db.session.commit()  # db.session.commit()
      # blank line
    current_app.logger.info(f"Alert triggered: {message}")  # current_app.logger.info(f"Alert triggered: {message}")
  # blank line
  # blank line
def send_email_alert(rule, server, metric_value, message):  # def send_email_alert(rule, server, metric_value, message):
    """Send email alert notification."""  # """Send email alert notification."""
    try:  # try:
        # Use rule-specific email or user's email  # # Use rule-specific email or user's email
        recipient = rule.email_address or rule.user.email  # recipient = rule.email_address or rule.user.email
          # blank line
        msg = Message(  # msg = Message(
            subject=f"System Monitor Alert: {rule.name}",  # subject=f"System Monitor Alert: {rule.name}",
            recipients=[recipient],  # recipients=[recipient],
            body=f"""  # body=f"""
System Monitor Alert  # System Monitor Alert
  # blank line
Server: {server.name}  # Server: {server.name}
Alert Rule: {rule.name}  # Alert Rule: {rule.name}
Metric: {rule.metric_type}  # Metric: {rule.metric_type}
Current Value: {metric_value:.2f}  # Current Value: {metric_value:.2f}
Threshold: {rule.comparison} {rule.threshold}  # Threshold: {rule.comparison} {rule.threshold}
  # blank line
Message: {message}  # Message: {message}
  # blank line
Triggered at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  # Triggered at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
  # blank line
---  # ---
This is an automated alert from System Monitor.  # This is an automated alert from System Monitor.
            """.strip()  # """.strip()
        )  # )
          # blank line
        mail.send(msg)  # mail.send(msg)
        return True  # return True
    except Exception as e:  # except Exception as e:
        current_app.logger.error(f"Error sending email alert: {e}")  # current_app.logger.error(f"Error sending email alert: {e}")
        return False  # return False
  # blank line
  # blank line
def send_sms_alert(rule, server, metric_value, message):  # def send_sms_alert(rule, server, metric_value, message):
    """Send SMS alert notification via Twilio."""  # """Send SMS alert notification via Twilio."""
    try:  # try:
        # Check if Twilio is configured  # # Check if Twilio is configured
        account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')  # account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')  # auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        from_number = current_app.config.get('TWILIO_PHONE_NUMBER')  # from_number = current_app.config.get('TWILIO_PHONE_NUMBER')
          # blank line
        if not all([account_sid, auth_token, from_number]):  # if not all([account_sid, auth_token, from_number]):
            current_app.logger.warning("Twilio not configured, skipping SMS alert")  # current_app.logger.warning("Twilio not configured, skipping SMS alert")
            return False  # return False
          # blank line
        # Use rule-specific phone or skip  # # Use rule-specific phone or skip
        to_number = rule.phone_number  # to_number = rule.phone_number
        if not to_number:  # if not to_number:
            current_app.logger.warning("No phone number configured for alert rule")  # current_app.logger.warning("No phone number configured for alert rule")
            return False  # return False
          # blank line
        # Initialize Twilio client  # # Initialize Twilio client
        client = Client(account_sid, auth_token)  # client = Client(account_sid, auth_token)
          # blank line
        # Send SMS  # # Send SMS
        sms_message = f"System Monitor Alert: {rule.name} on {server.name}. {rule.metric_type}={metric_value:.2f} (threshold: {rule.comparison}{rule.threshold})"  # sms_message = f"System Monitor Alert: {rule.name} on {server.name}. {rule.metric_type}={metric_value:.2f} (threshold: {rule.comparison}{rule.threshold})"
          # blank line
        client.messages.create(  # client.messages.create(
            body=sms_message,  # body=sms_message,
            from_=from_number,  # from_=from_number,
            to=to_number  # to=to_number
        )  # )
          # blank line
        return True  # return True
    except Exception as e:  # except Exception as e:
        current_app.logger.error(f"Error sending SMS alert: {e}")  # current_app.logger.error(f"Error sending SMS alert: {e}")
        return False  # return False
  # blank line
  # blank line
def test_alert_notification(rule_id, notification_type='email'):  # def test_alert_notification(rule_id, notification_type='email'):
    """Test an alert notification without triggering the actual alert."""  # """Test an alert notification without triggering the actual alert."""
    rule = AlertRule.query.get(rule_id)  # rule = AlertRule.query.get(rule_id)
    if not rule:  # if not rule:
        return False, "Alert rule not found"  # return False, "Alert rule not found"
      # blank line
    server = Server.query.filter_by(is_local=True).first()  # server = Server.query.filter_by(is_local=True).first()
    if not server:  # if not server:
        return False, "No server found"  # return False, "No server found"
      # blank line
    test_message = f"Test alert for rule: {rule.name}"  # test_message = f"Test alert for rule: {rule.name}"
      # blank line
    if notification_type == 'email':  # if notification_type == 'email':
        success = send_email_alert(rule, server, rule.threshold, test_message)  # success = send_email_alert(rule, server, rule.threshold, test_message)
        return success, "Email sent successfully" if success else "Failed to send email"  # return success, "Email sent successfully" if success else "Failed to send email"
    elif notification_type == 'sms':  # elif notification_type == 'sms':
        success = send_sms_alert(rule, server, rule.threshold, test_message)  # success = send_sms_alert(rule, server, rule.threshold, test_message)
        return success, "SMS sent successfully" if success else "Failed to send SMS"  # return success, "SMS sent successfully" if success else "Failed to send SMS"
      # blank line
    return False, "Invalid notification type"  # return False, "Invalid notification type"
  # blank line
  # blank line
def send_slack_alert(rule, server, metric_value, message):  # def send_slack_alert(rule, server, metric_value, message):
    """Send alert notification to Slack via webhook."""  # """Send alert notification to Slack via webhook."""
    import requests  # import requests
    import json  # import json
      # blank line
    try:  # try:
        webhook_url = current_app.config.get('SLACK_WEBHOOK_URL')  # webhook_url = current_app.config.get('SLACK_WEBHOOK_URL')
          # blank line
        if not webhook_url:  # if not webhook_url:
            current_app.logger.warning("Slack webhook URL not configured")  # current_app.logger.warning("Slack webhook URL not configured")
            return False  # return False
          # blank line
        # Format Slack message with rich formatting  # # Format Slack message with rich formatting
        slack_message = {  # slack_message = {
            "text": f"🚨 System Monitor Alert: {rule.name}",  # "text": f"🚨 System Monitor Alert: {rule.name}",
            "blocks": [  # "blocks": [
                {  # {
                    "type": "header",  # "type": "header",
                    "text": {  # "text": {
                        "type": "plain_text",  # "type": "plain_text",
                        "text": f"🚨 {rule.name}"  # "text": f"🚨 {rule.name}"
                    }  # }
                },  # },
                {  # {
                    "type": "section",  # "type": "section",
                    "fields": [  # "fields": [
                        {  # {
                            "type": "mrkdwn",  # "type": "mrkdwn",
                            "text": f"*Server:*\n{server.name}"  # "text": f"*Server:*\n{server.name}"
                        },  # },
                        {  # {
                            "type": "mrkdwn",  # "type": "mrkdwn",
                            "text": f"*Metric:*\n{rule.metric_type}"  # "text": f"*Metric:*\n{rule.metric_type}"
                        },  # },
                        {  # {
                            "type": "mrkdwn",  # "type": "mrkdwn",
                            "text": f"*Current Value:*\n{metric_value:.2f}"  # "text": f"*Current Value:*\n{metric_value:.2f}"
                        },  # },
                        {  # {
                            "type": "mrkdwn",  # "type": "mrkdwn",
                            "text": f"*Threshold:*\n{rule.comparison} {rule.threshold}"  # "text": f"*Threshold:*\n{rule.comparison} {rule.threshold}"
                        }  # }
                    ]  # ]
                },  # },
                {  # {
                    "type": "section",  # "type": "section",
                    "text": {  # "text": {
                        "type": "mrkdwn",  # "type": "mrkdwn",
                        "text": f"*Message:* {message}"  # "text": f"*Message:* {message}"
                    }  # }
                },  # },
                {  # {
                    "type": "context",  # "type": "context",
                    "elements": [  # "elements": [
                        {  # {
                            "type": "mrkdwn",  # "type": "mrkdwn",
                            "text": f"Triggered at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"  # "text": f"Triggered at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                        }  # }
                    ]  # ]
                }  # }
            ]  # ]
        }  # }
          # blank line
        response = requests.post(  # response = requests.post(
            webhook_url,  # webhook_url,
            data=json.dumps(slack_message),  # data=json.dumps(slack_message),
            headers={'Content-Type': 'application/json'},  # headers={'Content-Type': 'application/json'},
            timeout=5  # timeout=5
        )  # )
          # blank line
        if response.status_code == 200:  # if response.status_code == 200:
            return True  # return True
        else:  # else:
            current_app.logger.error(f"Slack webhook failed with status {response.status_code}")  # current_app.logger.error(f"Slack webhook failed with status {response.status_code}")
            return False  # return False
              # blank line
    except Exception as e:  # except Exception as e:
        current_app.logger.error(f"Error sending Slack alert: {e}")  # current_app.logger.error(f"Error sending Slack alert: {e}")
        return False  # return False
