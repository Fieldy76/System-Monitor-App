"""Background tasks for metric collection and alert checking."""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import psutil
from app.models import db, Server, SystemMetric, NetworkMetric, ProcessSnapshot, AlertRule, AlertHistory
from flask import current_app


# Global scheduler instance
scheduler = BackgroundScheduler()


def init_scheduler(app):
    """Initialize the background scheduler with the Flask app context."""
    if not scheduler.running:
        # Store app context for tasks
        scheduler.app = app
        
        # Schedule metric collection every 60 seconds
        scheduler.add_job(
            func=collect_metrics_job,
            trigger='interval',
            seconds=app.config.get('METRIC_COLLECTION_INTERVAL', 60),
            id='collect_metrics',
            replace_existing=True
        )
        
        # Schedule alert checking every 60 seconds
        scheduler.add_job(
            func=check_alerts_job,
            trigger='interval',
            seconds=app.config.get('ALERT_CHECK_INTERVAL', 60),
            id='check_alerts',
            replace_existing=True
        )
        
        # Schedule cleanup every day at 2 AM
        scheduler.add_job(
            func=cleanup_old_data_job,
            trigger='cron',
            hour=2,
            minute=0,
            id='cleanup_old_data',
            replace_existing=True
        )
        
        # Schedule health checks every 60 seconds
        scheduler.add_job(
            func=run_health_checks_job,
            trigger='interval',
            seconds=60,
            id='health_checks',
            replace_existing=True
        )
        
        scheduler.start()


def collect_metrics_job():
    """Job wrapper for metric collection with app context."""
    with scheduler.app.app_context():
        collect_system_metrics()
        collect_network_metrics()


def collect_system_metrics():
    """Collect and store system metrics for the local server."""
    try:
        # Get local server
        local_server = Server.query.filter_by(is_local=True).first()
        if not local_server:
            return
        
        # Collect CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        cpu_freq_current = cpu_freq.current if cpu_freq else None
        
        # Collect CPU temperature
        cpu_temp_c = None
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                cpu_temp_c = temps['coretemp'][0].current
            elif 'cpu_thermal' in temps:
                cpu_temp_c = temps['cpu_thermal'][0].current
            elif 'k10temp' in temps:
                cpu_temp_c = temps['k10temp'][0].current
        except Exception:
            pass
        
        # Collect memory metrics
        svmem = psutil.virtual_memory()
        
        # Collect disk metrics (primary partition)
        disk_usage = psutil.disk_usage('/')
        
        # Collect I/O metrics
        disk_io = psutil.disk_io_counters()
        
        # Create metric record
        metric = SystemMetric(
            server_id=local_server.id,
            cpu_percent=cpu_percent,
            cpu_freq=cpu_freq_current,
            cpu_temp_c=cpu_temp_c,
            memory_total=svmem.total,
            memory_used=svmem.used,
            memory_percent=svmem.percent,
            disk_total=disk_usage.total,
            disk_used=disk_usage.used,
            disk_percent=disk_usage.percent,
            io_read_bytes=disk_io.read_bytes,
            io_write_bytes=disk_io.write_bytes,
            io_read_count=disk_io.read_count,
            io_write_count=disk_io.write_count
        )
        
        db.session.add(metric)
        db.session.commit()
        
        # Update server last_seen
        local_server.last_seen = datetime.utcnow()
        db.session.commit()
        
    except Exception as e:
        current_app.logger.error(f"Error collecting system metrics: {e}")
        db.session.rollback()


def collect_network_metrics():
    """Collect and store network metrics for the local server."""
    try:
        # Get local server
        local_server = Server.query.filter_by(is_local=True).first()
        if not local_server:
            return
        
        # Collect network I/O
        net_io = psutil.net_io_counters()
        
        # Collect connection statistics
        connections = psutil.net_connections(kind='inet')
        conn_established = sum(1 for c in connections if c.status == 'ESTABLISHED')
        conn_listen = sum(1 for c in connections if c.status == 'LISTEN')
        conn_time_wait = sum(1 for c in connections if c.status == 'TIME_WAIT')
        
        # Create metric record
        metric = NetworkMetric(
            server_id=local_server.id,
            bytes_sent=net_io.bytes_sent,
            bytes_recv=net_io.bytes_recv,
            packets_sent=net_io.packets_sent,
            packets_recv=net_io.packets_recv,
            connections_established=conn_established,
            connections_listen=conn_listen,
            connections_time_wait=conn_time_wait
        )
        
        db.session.add(metric)
        db.session.commit()
        
    except Exception as e:
        current_app.logger.error(f"Error collecting network metrics: {e}")
        db.session.rollback()


def check_alerts_job():
    """Job wrapper for alert checking with app context."""
    with scheduler.app.app_context():
        check_alert_thresholds()


def check_alert_thresholds():
    """Check all active alert rules and trigger notifications if needed."""
    try:
        from app.alerts import check_and_notify_alerts
        check_and_notify_alerts()
    except Exception as e:
        current_app.logger.error(f"Error checking alerts: {e}")


def cleanup_old_data_job():
    """Job wrapper for data cleanup with app context."""
    with scheduler.app.app_context():
        cleanup_old_metrics()


def cleanup_old_metrics():
    """Delete old metrics based on data retention policy."""
    try:
        retention_days = current_app.config.get('DATA_RETENTION_DAYS', 30)
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Delete old system metrics
        SystemMetric.query.filter(SystemMetric.timestamp < cutoff_date).delete()
        
        # Delete old network metrics
        NetworkMetric.query.filter(NetworkMetric.timestamp < cutoff_date).delete()
        
        # Delete old process snapshots
        ProcessSnapshot.query.filter(ProcessSnapshot.timestamp < cutoff_date).delete()
        
        # Delete old alert history (keep for 90 days)
        alert_cutoff = datetime.utcnow() - timedelta(days=90)
        AlertHistory.query.filter(AlertHistory.triggered_at < alert_cutoff).delete()
        
        db.session.commit()
        current_app.logger.info(f"Cleaned up metrics older than {retention_days} days")
        
    except Exception as e:
        current_app.logger.error(f"Error cleaning up old data: {e}")
        db.session.rollback()


def run_health_checks_job():
    """Job wrapper for health checks with app context."""
    with scheduler.app.app_context():
        run_health_checks()


def run_health_checks():
    """Periodically check all registered services."""
    from app.models import ServiceHealth
    from app.utils.healthchecks import check_http_service
    
    try:
        # Get all active services
        services = ServiceHealth.query.filter_by(is_active=True).all()
        
        for service in services:
            # Perform health check
            is_up, status_code, response_time, error_message = check_http_service(
                service.url,
                service.name,
                service.timeout
            )
            
            # Update service status
            service.last_check_time = datetime.utcnow()
            service.is_up = is_up
            service.status_code = status_code
            service.response_time = response_time
            service.error_message = error_message
            service.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            current_app.logger.info(
                f"Health check for {service.name}: "
                f"{'UP' if is_up else 'DOWN'} "
                f"(status: {status_code}, response: {response_time}ms)"
            )
            
    except Exception as e:
        current_app.logger.error(f"Error running health checks: {e}")
        db.session.rollback()
