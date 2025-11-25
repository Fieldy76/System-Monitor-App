"""Background tasks for metric collection and alert checking."""  # """Background tasks for metric collection and alert checking."""
from apscheduler.schedulers.background import BackgroundScheduler  # from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta  # from datetime import datetime, timedelta
import psutil  # import psutil
from app.models import db, Server, SystemMetric, NetworkMetric, ProcessSnapshot, AlertRule, AlertHistory  # from app.models import db, Server, SystemMetric, NetworkMetric, ProcessSnapshot, AlertRule, AlertHistory
from flask import current_app  # from flask import current_app
  # blank line
  # blank line
# Global scheduler instance  # # Global scheduler instance
scheduler = BackgroundScheduler()  # scheduler = BackgroundScheduler()
  # blank line
  # blank line
def init_scheduler(app):  # def init_scheduler(app):
    """Initialize the background scheduler with the Flask app context."""  # """Initialize the background scheduler with the Flask app context."""
    if not scheduler.running:  # if not scheduler.running:
        # Store app context for tasks  # # Store app context for tasks
        scheduler.app = app  # scheduler.app = app
          # blank line
        # Schedule metric collection every 60 seconds  # # Schedule metric collection every 60 seconds
        scheduler.add_job(  # scheduler.add_job(
            func=collect_metrics_job,  # func=collect_metrics_job,
            trigger='interval',  # trigger='interval',
            seconds=app.config.get('METRIC_COLLECTION_INTERVAL', 60),  # seconds=app.config.get('METRIC_COLLECTION_INTERVAL', 60),
            id='collect_metrics',  # id='collect_metrics',
            replace_existing=True  # replace_existing=True
        )  # )
          # blank line
        # Schedule alert checking every 60 seconds  # # Schedule alert checking every 60 seconds
        scheduler.add_job(  # scheduler.add_job(
            func=check_alerts_job,  # func=check_alerts_job,
            trigger='interval',  # trigger='interval',
            seconds=app.config.get('ALERT_CHECK_INTERVAL', 60),  # seconds=app.config.get('ALERT_CHECK_INTERVAL', 60),
            id='check_alerts',  # id='check_alerts',
            replace_existing=True  # replace_existing=True
        )  # )
          # blank line
        # Schedule cleanup every day at 2 AM  # # Schedule cleanup every day at 2 AM
        scheduler.add_job(  # scheduler.add_job(
            func=cleanup_old_data_job,  # func=cleanup_old_data_job,
            trigger='cron',  # trigger='cron',
            hour=2,  # hour=2,
            minute=0,  # minute=0,
            id='cleanup_old_data',  # id='cleanup_old_data',
            replace_existing=True  # replace_existing=True
        )  # )
          # blank line
        # Schedule health checks every 60 seconds  # # Schedule health checks every 60 seconds
        scheduler.add_job(  # scheduler.add_job(
            func=run_health_checks_job,  # func=run_health_checks_job,
            trigger='interval',  # trigger='interval',
            seconds=60,  # seconds=60,
            id='health_checks',  # id='health_checks',
            replace_existing=True  # replace_existing=True
        )  # )
          # blank line
        scheduler.start()  # scheduler.start()
  # blank line
  # blank line
def collect_metrics_job():  # def collect_metrics_job():
    """Job wrapper for metric collection with app context."""  # """Job wrapper for metric collection with app context."""
    with scheduler.app.app_context():  # with scheduler.app.app_context():
        collect_system_metrics()  # collect_system_metrics()
        collect_network_metrics()  # collect_network_metrics()
  # blank line
  # blank line
def collect_system_metrics():  # def collect_system_metrics():
    """Collect and store system metrics for the local server."""  # """Collect and store system metrics for the local server."""
    try:  # try:
        # Get local server  # # Get local server
        local_server = Server.query.filter_by(is_local=True).first()  # local_server = Server.query.filter_by(is_local=True).first()
        if not local_server:  # if not local_server:
            return  # return
          # blank line
        # Collect CPU metrics  # # Collect CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)  # cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()  # cpu_freq = psutil.cpu_freq()
        cpu_freq_current = cpu_freq.current if cpu_freq else None  # cpu_freq_current = cpu_freq.current if cpu_freq else None
          # blank line
        # Collect CPU temperature  # # Collect CPU temperature
        cpu_temp_c = None  # cpu_temp_c = None
        try:  # try:
            temps = psutil.sensors_temperatures()  # temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:  # if 'coretemp' in temps:
                cpu_temp_c = temps['coretemp'][0].current  # cpu_temp_c = temps['coretemp'][0].current
            elif 'cpu_thermal' in temps:  # elif 'cpu_thermal' in temps:
                cpu_temp_c = temps['cpu_thermal'][0].current  # cpu_temp_c = temps['cpu_thermal'][0].current
            elif 'k10temp' in temps:  # elif 'k10temp' in temps:
                cpu_temp_c = temps['k10temp'][0].current  # cpu_temp_c = temps['k10temp'][0].current
        except Exception:  # except Exception:
            pass  # pass
          # blank line
        # Collect memory metrics  # # Collect memory metrics
        svmem = psutil.virtual_memory()  # svmem = psutil.virtual_memory()
          # blank line
        # Collect disk metrics (primary partition)  # # Collect disk metrics (primary partition)
        disk_usage = psutil.disk_usage('/')  # disk_usage = psutil.disk_usage('/')
          # blank line
        # Collect I/O metrics  # # Collect I/O metrics
        disk_io = psutil.disk_io_counters()  # disk_io = psutil.disk_io_counters()
          # blank line
        # Create metric record  # # Create metric record
        metric = SystemMetric(  # metric = SystemMetric(
            server_id=local_server.id,  # server_id=local_server.id,
            cpu_percent=cpu_percent,  # cpu_percent=cpu_percent,
            cpu_freq=cpu_freq_current,  # cpu_freq=cpu_freq_current,
            cpu_temp_c=cpu_temp_c,  # cpu_temp_c=cpu_temp_c,
            memory_total=svmem.total,  # memory_total=svmem.total,
            memory_used=svmem.used,  # memory_used=svmem.used,
            memory_percent=svmem.percent,  # memory_percent=svmem.percent,
            disk_total=disk_usage.total,  # disk_total=disk_usage.total,
            disk_used=disk_usage.used,  # disk_used=disk_usage.used,
            disk_percent=disk_usage.percent,  # disk_percent=disk_usage.percent,
            io_read_bytes=disk_io.read_bytes,  # io_read_bytes=disk_io.read_bytes,
            io_write_bytes=disk_io.write_bytes,  # io_write_bytes=disk_io.write_bytes,
            io_read_count=disk_io.read_count,  # io_read_count=disk_io.read_count,
            io_write_count=disk_io.write_count  # io_write_count=disk_io.write_count
        )  # )
          # blank line
        db.session.add(metric)  # db.session.add(metric)
        db.session.commit()  # db.session.commit()
          # blank line
        # Update server last_seen  # # Update server last_seen
        local_server.last_seen = datetime.utcnow()  # local_server.last_seen = datetime.utcnow()
        db.session.commit()  # db.session.commit()
          # blank line
    except Exception as e:  # except Exception as e:
        current_app.logger.error(f"Error collecting system metrics: {e}")  # current_app.logger.error(f"Error collecting system metrics: {e}")
        db.session.rollback()  # db.session.rollback()
  # blank line
  # blank line
def collect_network_metrics():  # def collect_network_metrics():
    """Collect and store network metrics for the local server."""  # """Collect and store network metrics for the local server."""
    try:  # try:
        # Get local server  # # Get local server
        local_server = Server.query.filter_by(is_local=True).first()  # local_server = Server.query.filter_by(is_local=True).first()
        if not local_server:  # if not local_server:
            return  # return
          # blank line
        # Collect network I/O  # # Collect network I/O
        net_io = psutil.net_io_counters()  # net_io = psutil.net_io_counters()
          # blank line
        # Collect connection statistics  # # Collect connection statistics
        connections = psutil.net_connections(kind='inet')  # connections = psutil.net_connections(kind='inet')
        conn_established = sum(1 for c in connections if c.status == 'ESTABLISHED')  # conn_established = sum(1 for c in connections if c.status == 'ESTABLISHED')
        conn_listen = sum(1 for c in connections if c.status == 'LISTEN')  # conn_listen = sum(1 for c in connections if c.status == 'LISTEN')
        conn_time_wait = sum(1 for c in connections if c.status == 'TIME_WAIT')  # conn_time_wait = sum(1 for c in connections if c.status == 'TIME_WAIT')
          # blank line
        # Create metric record  # # Create metric record
        metric = NetworkMetric(  # metric = NetworkMetric(
            server_id=local_server.id,  # server_id=local_server.id,
            bytes_sent=net_io.bytes_sent,  # bytes_sent=net_io.bytes_sent,
            bytes_recv=net_io.bytes_recv,  # bytes_recv=net_io.bytes_recv,
            packets_sent=net_io.packets_sent,  # packets_sent=net_io.packets_sent,
            packets_recv=net_io.packets_recv,  # packets_recv=net_io.packets_recv,
            connections_established=conn_established,  # connections_established=conn_established,
            connections_listen=conn_listen,  # connections_listen=conn_listen,
            connections_time_wait=conn_time_wait  # connections_time_wait=conn_time_wait
        )  # )
          # blank line
        db.session.add(metric)  # db.session.add(metric)
        db.session.commit()  # db.session.commit()
          # blank line
    except Exception as e:  # except Exception as e:
        current_app.logger.error(f"Error collecting network metrics: {e}")  # current_app.logger.error(f"Error collecting network metrics: {e}")
        db.session.rollback()  # db.session.rollback()
  # blank line
  # blank line
def check_alerts_job():  # def check_alerts_job():
    """Job wrapper for alert checking with app context."""  # """Job wrapper for alert checking with app context."""
    with scheduler.app.app_context():  # with scheduler.app.app_context():
        check_alert_thresholds()  # check_alert_thresholds()
  # blank line
  # blank line
def check_alert_thresholds():  # def check_alert_thresholds():
    """Check all active alert rules and trigger notifications if needed."""  # """Check all active alert rules and trigger notifications if needed."""
    try:  # try:
        from app.alerts import check_and_notify_alerts  # from app.alerts import check_and_notify_alerts
        check_and_notify_alerts()  # check_and_notify_alerts()
    except Exception as e:  # except Exception as e:
        current_app.logger.error(f"Error checking alerts: {e}")  # current_app.logger.error(f"Error checking alerts: {e}")
  # blank line
  # blank line
def cleanup_old_data_job():  # def cleanup_old_data_job():
    """Job wrapper for data cleanup with app context."""  # """Job wrapper for data cleanup with app context."""
    with scheduler.app.app_context():  # with scheduler.app.app_context():
        cleanup_old_metrics()  # cleanup_old_metrics()
  # blank line
  # blank line
def cleanup_old_metrics():  # def cleanup_old_metrics():
    """Delete old metrics based on data retention policy."""  # """Delete old metrics based on data retention policy."""
    try:  # try:
        retention_days = current_app.config.get('DATA_RETENTION_DAYS', 30)  # retention_days = current_app.config.get('DATA_RETENTION_DAYS', 30)
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)  # cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
          # blank line
        # Delete old system metrics  # # Delete old system metrics
        SystemMetric.query.filter(SystemMetric.timestamp < cutoff_date).delete()  # SystemMetric.query.filter(SystemMetric.timestamp < cutoff_date).delete()
          # blank line
        # Delete old network metrics  # # Delete old network metrics
        NetworkMetric.query.filter(NetworkMetric.timestamp < cutoff_date).delete()  # NetworkMetric.query.filter(NetworkMetric.timestamp < cutoff_date).delete()
          # blank line
        # Delete old process snapshots  # # Delete old process snapshots
        ProcessSnapshot.query.filter(ProcessSnapshot.timestamp < cutoff_date).delete()  # ProcessSnapshot.query.filter(ProcessSnapshot.timestamp < cutoff_date).delete()
          # blank line
        # Delete old alert history (keep for 90 days)  # # Delete old alert history (keep for 90 days)
        alert_cutoff = datetime.utcnow() - timedelta(days=90)  # alert_cutoff = datetime.utcnow() - timedelta(days=90)
        AlertHistory.query.filter(AlertHistory.triggered_at < alert_cutoff).delete()  # AlertHistory.query.filter(AlertHistory.triggered_at < alert_cutoff).delete()
          # blank line
        db.session.commit()  # db.session.commit()
        current_app.logger.info(f"Cleaned up metrics older than {retention_days} days")  # current_app.logger.info(f"Cleaned up metrics older than {retention_days} days")
          # blank line
    except Exception as e:  # except Exception as e:
        current_app.logger.error(f"Error cleaning up old data: {e}")  # current_app.logger.error(f"Error cleaning up old data: {e}")
        db.session.rollback()  # db.session.rollback()
  # blank line
  # blank line
def run_health_checks_job():  # def run_health_checks_job():
    """Job wrapper for health checks with app context."""  # """Job wrapper for health checks with app context."""
    with scheduler.app.app_context():  # with scheduler.app.app_context():
        run_health_checks()  # run_health_checks()
  # blank line
  # blank line
def run_health_checks():  # def run_health_checks():
    """Periodically check all registered services."""  # """Periodically check all registered services."""
    from app.models import ServiceHealth  # from app.models import ServiceHealth
    from app.utils.healthchecks import check_http_service  # from app.utils.healthchecks import check_http_service
      # blank line
    try:  # try:
        # Get all active services  # # Get all active services
        services = ServiceHealth.query.filter_by(is_active=True).all()  # services = ServiceHealth.query.filter_by(is_active=True).all()
          # blank line
        for service in services:  # for service in services:
            # Perform health check  # # Perform health check
            is_up, status_code, response_time, error_message = check_http_service(  # is_up, status_code, response_time, error_message = check_http_service(
                service.url,  # service.url,
                service.name,  # service.name,
                service.timeout  # service.timeout
            )  # )
              # blank line
            # Update service status  # # Update service status
            service.last_check_time = datetime.utcnow()  # service.last_check_time = datetime.utcnow()
            service.is_up = is_up  # service.is_up = is_up
            service.status_code = status_code  # service.status_code = status_code
            service.response_time = response_time  # service.response_time = response_time
            service.error_message = error_message  # service.error_message = error_message
            service.updated_at = datetime.utcnow()  # service.updated_at = datetime.utcnow()
              # blank line
            db.session.commit()  # db.session.commit()
              # blank line
            current_app.logger.info(  # current_app.logger.info(
                f"Health check for {service.name}: "  # f"Health check for {service.name}: "
                f"{'UP' if is_up else 'DOWN'} "  # f"{'UP' if is_up else 'DOWN'} "
                f"(status: {status_code}, response: {response_time}ms)"  # f"(status: {status_code}, response: {response_time}ms)"
            )  # )
              # blank line
    except Exception as e:  # except Exception as e:
        current_app.logger.error(f"Error running health checks: {e}")  # current_app.logger.error(f"Error running health checks: {e}")
        db.session.rollback()  # db.session.rollback()
