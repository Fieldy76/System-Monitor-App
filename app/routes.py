"""Routes and view logic using Flask Blueprints."""
import psutil
import requests
from flask import Blueprint, jsonify, render_template, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from app.models import (db, Server, SystemMetric, NetworkMetric, ProcessSnapshot,
                         AlertRule, AlertHistory, UserPreference)
from app.export import export_metrics_to_csv, export_metrics_to_json, create_export_response
from app.alerts import test_alert_notification
from sqlalchemy import func

main = Blueprint('main', __name__)


def get_size(bytes, suffix="B"):
    """Scale bytes to its proper format (e.g., 1253656 => '1.20MB')."""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


# ============================================================================
# DASHBOARD ROUTES
# ============================================================================

@main.route('/')
@login_required
def index():
    """Render the main dashboard page."""
    servers = Server.query.filter_by(is_active=True).all()
    preferences = current_user.preferences or UserPreference(user_id=current_user.id)
    return render_template('index.html', servers=servers, preferences=preferences)


@main.route('/processes')
@login_required
def processes():
    """Render the process monitoring page."""
    return render_template('processes.html')


@main.route('/alerts')
@login_required
def alerts_page():
    """Render the alerts configuration page."""
    servers = Server.query.filter_by(is_active=True).all()
    return render_template('alerts.html', servers=servers)


@main.route('/servers')
@login_required
def servers_page():
    """Render the server management page."""
    return render_template('servers.html')


@main.route('/settings')
@login_required
def settings():
    """Render the user settings page."""
    preferences = current_user.preferences or UserPreference(user_id=current_user.id)
    servers = Server.query.filter_by(is_active=True).all()
    return render_template('settings.html', preferences=preferences, servers=servers)


# ============================================================================
# REAL-TIME METRICS API
# ============================================================================

@main.route('/api/metrics')
@login_required
def metrics():
    """API endpoint to get real-time system metrics."""
    server_id = request.args.get('server_id', type=int)
    
    # Get server (default to local if not specified)
    if server_id:
        server = Server.query.get(server_id)
    else:
        server = Server.query.filter_by(is_local=True).first()
    
    if not server:
        return jsonify({'error': 'Server not found'}), 404
    
    # If remote server, fetch from agent
    if not server.is_local:
        return fetch_remote_metrics(server)
    
    # Collect local metrics
    cpu_percent = psutil.cpu_percent(interval=None)
    cpu_freq = psutil.cpu_freq()
    cpu_freq_current = cpu_freq.current if cpu_freq else 0
    
    # CPU temperature
    cpu_temp_c = None
    cpu_temp_f = None
    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:
            cpu_temp_c = temps['coretemp'][0].current
        elif 'cpu_thermal' in temps:
            cpu_temp_c = temps['cpu_thermal'][0].current
        elif 'k10temp' in temps:
            cpu_temp_c = temps['k10temp'][0].current
        
        if cpu_temp_c is not None:
            cpu_temp_f = (cpu_temp_c * 9/5) + 32
    except Exception:
        pass

    # Memory usage
    svmem = psutil.virtual_memory()
    memory_usage = {
        'total': get_size(svmem.total),
        'available': get_size(svmem.available),
        'used': get_size(svmem.used),
        'percent': svmem.percent
    }

    # Disk usage
    partitions = psutil.disk_partitions()
    disk_usage_info = []
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            disk_usage_info.append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'total': get_size(partition_usage.total),
                'used': get_size(partition_usage.used),
                'free': get_size(partition_usage.free),
                'percent': partition_usage.percent
            })
        except PermissionError:
            continue

    # Disk I/O
    disk_io = psutil.disk_io_counters()
    disk_io_info = {
        'read_bytes': get_size(disk_io.read_bytes),
        'write_bytes': get_size(disk_io.write_bytes),
        'read_count': disk_io.read_count,
        'write_count': disk_io.write_count
    }
    
    # Network I/O
    net_io = psutil.net_io_counters()
    network_info = {
        'bytes_sent': get_size(net_io.bytes_sent),
        'bytes_recv': get_size(net_io.bytes_recv),
        'bytes_sent_raw': net_io.bytes_sent,
        'bytes_recv_raw': net_io.bytes_recv,
        'packets_sent': net_io.packets_sent,
        'packets_recv': net_io.packets_recv
    }
    
    # Network connections
    try:
        connections = psutil.net_connections(kind='inet')
        conn_stats = {
            'established': sum(1 for c in connections if c.status == 'ESTABLISHED'),
            'listen': sum(1 for c in connections if c.status == 'LISTEN'),
            'time_wait': sum(1 for c in connections if c.status == 'TIME_WAIT'),
            'total': len(connections)
        }
    except Exception:
        conn_stats = {'established': 0, 'listen': 0, 'time_wait': 0, 'total': 0}

    return jsonify({
        'cpu': {
            'percent': cpu_percent,
            'freq': f"{cpu_freq_current:.2f}Mhz",
            'temp_c': cpu_temp_c,
            'temp_f': cpu_temp_f
        },
        'memory': memory_usage,
        'disk': disk_usage_info,
        'io': disk_io_info,
        'network': network_info,
        'connections': conn_stats
    })


def fetch_remote_metrics(server):
    """Fetch metrics from a remote server agent."""
    try:
        response = requests.get(
            f"http://{server.hostname}/api/metrics",
            headers={'X-API-Key': server.api_key},
            timeout=5
        )
        response.raise_for_status()
        
        # Update last_seen
        server.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify(response.json())
    except Exception as e:
        current_app.logger.error(f"Error fetching metrics from {server.name}: {e}")
        return jsonify({'error': 'Failed to fetch metrics from remote server'}), 500


@main.route('/api/network/connections')
@login_required
def network_connections():
    """API endpoint to get detailed network connection information."""
    status_filter = request.args.get('status')
    
    try:
        connections = psutil.net_connections(kind='inet')
        
        # Filter by status if specified
        if status_filter:
            connections = [c for c in connections if c.status == status_filter.upper()]
        
        connection_list = []
        for conn in connections:
            # Get process information if available
            process_name = None
            try:
                if conn.pid:
                    proc = psutil.Process(conn.pid)
                    process_name = proc.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
            # Format connection data
            conn_data = {
                'protocol': 'TCP' if conn.type == 1 else 'UDP',
                'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else 'N/A',
                'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else 'N/A',
                'status': conn.status,
                'pid': conn.pid if conn.pid else 'N/A',
                'process': process_name if process_name else 'N/A'
            }
            connection_list.append(conn_data)
        
        return jsonify({
            'connections': connection_list,
            'count': len(connection_list)
        })
    except PermissionError:
        return jsonify({
            'error': 'Permission denied. Root/admin privileges may be required.',
            'connections': [],
            'count': 0
        }), 403
    except Exception as e:
        current_app.logger.error(f"Error fetching network connections: {e}")
        return jsonify({
            'error': str(e),
            'connections': [],
            'count': 0
        }), 500


# ============================================================================
# HISTORICAL DATA API
# ============================================================================

@main.route('/api/metrics/history')
@login_required
def metrics_history():
    """Get historical metrics data."""
    server_id = request.args.get('server_id', type=int)
    hours = request.args.get('hours', default=24, type=int)
    metric_type = request.args.get('type', default='system')
    
    if not server_id:
        server = Server.query.filter_by(is_local=True).first()
        server_id = server.id if server else None
    
    if not server_id:
        return jsonify({'error': 'Server not found'}), 404
    
    start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    if metric_type == 'system':
        metrics = SystemMetric.query.filter(
            SystemMetric.server_id == server_id,
            SystemMetric.timestamp >= start_time
        ).order_by(SystemMetric.timestamp).all()
        
        data = [{
            'timestamp': m.timestamp.isoformat(),
            'cpu_percent': m.cpu_percent,
            'memory_percent': m.memory_percent,
            'disk_percent': m.disk_percent,
            'cpu_temp_c': m.cpu_temp_c
        } for m in metrics]
        
    elif metric_type == 'network':
        metrics = NetworkMetric.query.filter(
            NetworkMetric.server_id == server_id,
            NetworkMetric.timestamp >= start_time
        ).order_by(NetworkMetric.timestamp).all()
        
        data = [{
            'timestamp': m.timestamp.isoformat(),
            'bytes_sent': m.bytes_sent,
            'bytes_recv': m.bytes_recv,
            'connections_established': m.connections_established
        } for m in metrics]
    else:
        return jsonify({'error': 'Invalid metric type'}), 400
    
    return jsonify({'data': data})


# ============================================================================
# PROCESS MONITORING API
# ============================================================================

@main.route('/api/processes')
@login_required
def get_processes():
    """Get list of running processes."""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'username': pinfo['username'],
                    'cpu_percent': pinfo['cpu_percent'] or 0,
                    'memory_percent': pinfo['memory_percent'] or 0,
                    'status': pinfo['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage (descending)
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        return jsonify({'processes': processes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/processes/<int:pid>')
@login_required
def get_process_details(pid):
    """Get detailed information about a specific process."""
    try:
        proc = psutil.Process(pid)
        info = proc.as_dict(attrs=['pid', 'name', 'username', 'status', 'create_time',
                                     'cpu_percent', 'memory_percent', 'memory_info',
                                     'num_threads', 'cmdline'])
        
        info['create_time'] = datetime.fromtimestamp(info['create_time']).isoformat()
        info['memory_rss'] = get_size(info['memory_info'].rss) if info.get('memory_info') else 'N/A'
        
        return jsonify(info)
    except psutil.NoSuchProcess:
        return jsonify({'error': 'Process not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/processes/<int:pid>/kill', methods=['POST'])
@login_required
def kill_process(pid):
    """Terminate a process."""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        return jsonify({'success': True, 'message': f'Process {pid} terminated'})
    except psutil.NoSuchProcess:
        return jsonify({'error': 'Process not found'}), 404
    except psutil.AccessDenied:
        return jsonify({'error': 'Access denied'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ALERT MANAGEMENT API
# ============================================================================

@main.route('/api/alerts/rules', methods=['GET', 'POST'])
@login_required
def alert_rules():
    """Get all alert rules or create a new one."""
    if request.method == 'GET':
        rules = AlertRule.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            'rules': [{
                'id': r.id,
                'name': r.name,
                'metric_type': r.metric_type,
                'threshold': r.threshold,
                'comparison': r.comparison,
                'server_id': r.server_id,
                'notify_email': r.notify_email,
                'notify_sms': r.notify_sms,
                'is_active': r.is_active
            } for r in rules]
        })
    
    elif request.method == 'POST':
        data = request.json
        
        rule = AlertRule(
            user_id=current_user.id,
            name=data['name'],
            metric_type=data['metric_type'],
            threshold=float(data['threshold']),
            comparison=data['comparison'],
            server_id=data.get('server_id'),
            duration=int(data.get('duration', 60)),
            notify_email=data.get('notify_email', True),
            notify_sms=data.get('notify_sms', False),
            email_address=data.get('email_address'),
            phone_number=data.get('phone_number'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return jsonify({'success': True, 'id': rule.id}), 201


@main.route('/api/alerts/rules/<int:rule_id>', methods=['PUT', 'DELETE'])
@login_required
def alert_rule_detail(rule_id):
    """Update or delete an alert rule."""
    rule = AlertRule.query.get(rule_id)
    
    if not rule or rule.user_id != current_user.id:
        return jsonify({'error': 'Alert rule not found'}), 404
    
    if request.method == 'PUT':
        data = request.json
        rule.name = data.get('name', rule.name)
        rule.threshold = float(data.get('threshold', rule.threshold))
        rule.is_active = data.get('is_active', rule.is_active)
        rule.notify_email = data.get('notify_email', rule.notify_email)
        rule.notify_sms = data.get('notify_sms', rule.notify_sms)
        
        db.session.commit()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        db.session.delete(rule)
        db.session.commit()
        return jsonify({'success': True})


@main.route('/api/alerts/history')
@login_required
def alert_history():
    """Get alert history."""
    limit = request.args.get('limit', default=50, type=int)
    
    history = AlertHistory.query.join(AlertRule).filter(
        AlertRule.user_id == current_user.id
    ).order_by(AlertHistory.triggered_at.desc()).limit(limit).all()
    
    return jsonify({
        'history': [{
            'id': h.id,
            'rule_name': h.rule.name,
            'server_name': Server.query.get(h.server_id).name,
            'metric_value': h.metric_value,
            'message': h.message,
            'triggered_at': h.triggered_at.isoformat(),
            'email_sent': h.email_sent,
            'sms_sent': h.sms_sent,
            'acknowledged': h.acknowledged
        } for h in history]
    })


@main.route('/api/alerts/test/<int:rule_id>', methods=['POST'])
@login_required
def test_alert(rule_id):
    """Test an alert notification."""
    notification_type = request.json.get('type', 'email')
    success, message = test_alert_notification(rule_id, notification_type)
    
    return jsonify({'success': success, 'message': message})


# ============================================================================
# SERVER MANAGEMENT API
# ============================================================================

@main.route('/api/servers', methods=['GET', 'POST'])
@login_required
def servers_api():
    """Get all servers or add a new one."""
    if request.method == 'GET':
        servers = Server.query.all()
        return jsonify({
            'servers': [{
                'id': s.id,
                'name': s.name,
                'hostname': s.hostname,
                'is_active': s.is_active,
                'is_local': s.is_local,
                'last_seen': s.last_seen.isoformat() if s.last_seen else None
            } for s in servers]
        })
    
    elif request.method == 'POST':
        if not current_user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        
        data = request.json
        
        server = Server(
            name=data['name'],
            hostname=data['hostname'],
            api_key=data['api_key'],
            is_active=True,
            is_local=False
        )
        
        db.session.add(server)
        db.session.commit()
        
        return jsonify({'success': True, 'id': server.id}), 201


@main.route('/api/servers/<int:server_id>', methods=['PUT', 'DELETE'])
@login_required
def server_detail(server_id):
    """Update or delete a server."""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    server = Server.query.get(server_id)
    
    if not server or server.is_local:
        return jsonify({'error': 'Server not found or cannot modify local server'}), 404
    
    if request.method == 'PUT':
        data = request.json
        server.name = data.get('name', server.name)
        server.hostname = data.get('hostname', server.hostname)
        server.is_active = data.get('is_active', server.is_active)
        
        db.session.commit()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        db.session.delete(server)
        db.session.commit()
        return jsonify({'success': True})


# ============================================================================
# USER SETTINGS API
# ============================================================================

@main.route('/api/settings', methods=['GET', 'PUT'])
@login_required
def user_settings():
    """Get or update user preferences."""
    preferences = current_user.preferences
    
    if not preferences:
        preferences = UserPreference(user_id=current_user.id)
        db.session.add(preferences)
        db.session.commit()
    
    if request.method == 'GET':
        return jsonify({
            'refresh_interval': preferences.refresh_interval,
            'chart_data_points': preferences.chart_data_points,
            'theme': preferences.theme,
            'default_server_id': preferences.default_server_id,
            'email_notifications': preferences.email_notifications,
            'sms_notifications': preferences.sms_notifications
        })
    
    elif request.method == 'PUT':
        data = request.json
        
        preferences.refresh_interval = data.get('refresh_interval', preferences.refresh_interval)
        preferences.chart_data_points = data.get('chart_data_points', preferences.chart_data_points)
        preferences.theme = data.get('theme', preferences.theme)
        preferences.default_server_id = data.get('default_server_id', preferences.default_server_id)
        preferences.email_notifications = data.get('email_notifications', preferences.email_notifications)
        preferences.sms_notifications = data.get('sms_notifications', preferences.sms_notifications)
        
        db.session.commit()
        return jsonify({'success': True})


# ============================================================================
# DATA EXPORT API
# ============================================================================

@main.route('/api/export/csv')
@login_required
def export_csv():
    """Export metrics to CSV."""
    server_id = request.args.get('server_id', type=int)
    days = request.args.get('days', default=7, type=int)
    metric_types = request.args.getlist('metrics') or ['system', 'network']
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    csv_data = export_metrics_to_csv(server_id, start_date, end_date, metric_types)
    return create_export_response(csv_data, 'csv')


@main.route('/api/export/json')
@login_required
def export_json():
    """Export metrics to JSON."""
    server_id = request.args.get('server_id', type=int)
    days = request.args.get('days', default=7, type=int)
    metric_types = request.args.getlist('metrics') or ['system', 'network']
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    json_data = export_metrics_to_json(server_id, start_date, end_date, metric_types)
    return create_export_response(json_data, 'json')


# ============================================================================
# SERVICE HEALTH CHECK ROUTES
# ============================================================================

@main.route('/health')
@login_required
def health_dashboard():
    """Health check dashboard page."""
    return render_template('health.html')


@main.route('/api/health/services', methods=['GET'])
@login_required
def get_health_services():
    """Get all registered services with their health status."""
    from app.models import ServiceHealth
    
    services = ServiceHealth.query.all()
    return jsonify({
        'services': [service.to_dict() for service in services]
    })


@main.route('/api/health/services', methods=['POST'])
@login_required
def create_health_service():
    """Add a new service to monitor."""
    from app.models import ServiceHealth
    
    if not current_user.is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name') or not data.get('url'):
        return jsonify({'error': 'Name and URL are required'}), 400
    
    service = ServiceHealth(
        name=data['name'],
        url=data['url'],
        description=data.get('description'),
        check_interval=data.get('check_interval', 60),
        timeout=data.get('timeout', 5),
        is_active=data.get('is_active', True),
        created_by=current_user.id
    )
    
    db.session.add(service)
    db.session.commit()
    
    return jsonify({
        'message': 'Service added successfully',
        'service': service.to_dict()
    }), 201


@main.route('/api/health/services/<int:service_id>', methods=['PUT'])
@login_required
def update_health_service(service_id):
    """Update service configuration."""
    from app.models import ServiceHealth
    
    if not current_user.is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    service = ServiceHealth.query.get_or_404(service_id)
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        service.name = data['name']
    if 'url' in data:
        service.url = data['url']
    if 'description' in data:
        service.description = data['description']
    if 'check_interval' in data:
        service.check_interval = data['check_interval']
    if 'timeout' in data:
        service.timeout = data['timeout']
    if 'is_active' in data:
        service.is_active = data['is_active']
    
    service.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify({
        'message': 'Service updated successfully',
        'service': service.to_dict()
    })


@main.route('/api/health/services/<int:service_id>', methods=['DELETE'])
@login_required
def delete_health_service(service_id):
    """Remove a service from monitoring."""
    from app.models import ServiceHealth
    
    if not current_user.is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    service = ServiceHealth.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    
    return jsonify({'message': 'Service deleted successfully'})


# ============================================================================
# DASHBOARD LAYOUT ROUTES
# ============================================================================

@main.route('/api/dashboard/layout', methods=['GET'])
@login_required
def get_dashboard_layout():
    """Get user's active dashboard layout."""
    from app.models import DashboardLayout
    
    layout = DashboardLayout.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).first()
    
    if layout:
        return jsonify(layout.to_dict())
    else:
        # Return default layout
        return jsonify({
            'layout_config': None,
            'message': 'No custom layout found, using default'
        })


@main.route('/api/dashboard/layout', methods=['POST'])
@login_required
def save_dashboard_layout():
    """Save or update user's dashboard layout."""
    from app.models import DashboardLayout
    
    data = request.get_json()
    
    if not data.get('layout_config'):
        return jsonify({'error': 'Layout configuration is required'}), 400
    
    # Deactivate existing layouts
    DashboardLayout.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).update({'is_active': False})
    
    # Create new layout
    layout = DashboardLayout(
        user_id=current_user.id,
        name=data.get('name', 'Custom Layout'),
        layout_config=data['layout_config'],
        is_active=True
    )
    
    db.session.add(layout)
    db.session.commit()
    
    return jsonify({
        'message': 'Layout saved successfully',
        'layout': layout.to_dict()
    }), 201


@main.route('/api/dashboard/layout/<int:layout_id>', methods=['DELETE'])
@login_required
def delete_dashboard_layout(layout_id):
    """Delete a dashboard layout."""
    from app.models import DashboardLayout
    
    layout = DashboardLayout.query.get_or_404(layout_id)
    
    # Ensure user owns this layout
    if layout.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(layout)
    db.session.commit()
    
    return jsonify({'message': 'Layout deleted successfully'})
