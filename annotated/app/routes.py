"""Routes and view logic using Flask Blueprints."""
import psutil  # Import psutil for system monitoring
import requests  # Import requests for making HTTP requests
from flask import Blueprint, jsonify, render_template, request, current_app  # Import Flask components
from flask_login import login_required, current_user  # Import Flask-Login for authentication
from datetime import datetime, timedelta, timezone  # Import datetime for time handling
from app.models import (db, Server, SystemMetric, NetworkMetric, ProcessSnapshot,
                         AlertRule, AlertHistory, UserPreference)  # Import database models
from app.export import export_metrics_to_csv, export_metrics_to_json, create_export_response  # Import export functions
from app.alerts import test_alert_notification  # Import alert testing function
from sqlalchemy import func  # Import SQLAlchemy functions

main = Blueprint('main', __name__)  # Create a Blueprint named 'main'


def get_size(bytes, suffix="B"):
    """Scale bytes to its proper format (e.g., 1253656 => '1.20MB')."""
    factor = 1024  # Define the factor for conversion (1024 bytes = 1 KB)
    for unit in ["", "K", "M", "G", "T", "P"]:  # Iterate through units
        if bytes < factor:  # If bytes is less than the current factor
            return f"{bytes:.2f}{unit}{suffix}"  # Return formatted string
        bytes /= factor  # Divide bytes by factor for next unit


# ============================================================================
# DASHBOARD ROUTES
# ============================================================================

@main.route('/')
@login_required  # Require login for this route
def index():
    """Render the main dashboard page."""
    servers = Server.query.filter_by(is_active=True).all()  # Get all active servers
    preferences = current_user.preferences or UserPreference(user_id=current_user.id)  # Get user preferences or create default
    return render_template('index.html', servers=servers, preferences=preferences)  # Render index.html template


@main.route('/processes')
@login_required  # Require login for this route
def processes():
    """Render the process monitoring page."""
    return render_template('processes.html')  # Render processes.html template


@main.route('/alerts')
@login_required  # Require login for this route
def alerts_page():
    """Render the alerts configuration page."""
    servers = Server.query.filter_by(is_active=True).all()  # Get all active servers
    return render_template('alerts.html', servers=servers)  # Render alerts.html template


@main.route('/servers')
@login_required  # Require login for this route
def servers_page():
    """Render the server management page."""
    return render_template('servers.html')  # Render servers.html template


@main.route('/settings')
@login_required  # Require login for this route
def settings():
    """Render the user settings page."""
    preferences = current_user.preferences or UserPreference(user_id=current_user.id)  # Get user preferences
    servers = Server.query.filter_by(is_active=True).all()  # Get all active servers
    return render_template('settings.html', preferences=preferences, servers=servers)  # Render settings.html template


# ============================================================================
# REAL-TIME METRICS API
# ============================================================================

@main.route('/api/metrics')
@login_required  # Require login for this route
def metrics():
    """API endpoint to get real-time system metrics."""
    server_id = request.args.get('server_id', type=int)  # Get server_id from query parameters
    
    # Get server (default to local if not specified)
    if server_id:
        server = Server.query.get(server_id)  # Get server by ID
    else:
        server = Server.query.filter_by(is_local=True).first()  # Get local server
    
    if not server:
        return jsonify({'error': 'Server not found'}), 404  # Return error if server not found
    
    # If remote server, fetch from agent
    if not server.is_local:
        return fetch_remote_metrics(server)  # Fetch metrics from remote server
    
    # Collect local metrics
    cpu_percent = psutil.cpu_percent(interval=None)  # Get CPU usage percentage
    cpu_freq = psutil.cpu_freq()  # Get CPU frequency
    cpu_freq_current = cpu_freq.current if cpu_freq else 0  # Get current CPU frequency
    
    # CPU temperature
    cpu_temp_c = None
    cpu_temp_f = None
    try:
        temps = psutil.sensors_temperatures()  # Get system temperatures
        if 'coretemp' in temps:
            cpu_temp_c = temps['coretemp'][0].current  # Get core temperature
        elif 'cpu_thermal' in temps:
            cpu_temp_c = temps['cpu_thermal'][0].current  # Get CPU thermal temperature
        elif 'k10temp' in temps:
            cpu_temp_c = temps['k10temp'][0].current  # Get AMD CPU temperature
        
        if cpu_temp_c is not None:
            cpu_temp_f = (cpu_temp_c * 9/5) + 32  # Convert Celsius to Fahrenheit
    except Exception:
        pass  # Ignore errors if temperature sensors are not available

    # Memory usage
    svmem = psutil.virtual_memory()  # Get virtual memory usage
    memory_usage = {
        'total': get_size(svmem.total),  # Total memory
        'available': get_size(svmem.available),  # Available memory
        'used': get_size(svmem.used),  # Used memory
        'percent': svmem.percent  # Memory usage percentage
    }

    # Disk usage
    partitions = psutil.disk_partitions()  # Get disk partitions
    disk_usage_info = []
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)  # Get usage for partition
            disk_usage_info.append({
                'device': partition.device,  # Device name
                'mountpoint': partition.mountpoint,  # Mount point
                'total': get_size(partition_usage.total),  # Total space
                'used': get_size(partition_usage.used),  # Used space
                'free': get_size(partition_usage.free),  # Free space
                'percent': partition_usage.percent  # Usage percentage
            })
        except PermissionError:
            continue  # Skip if permission denied

    # Disk I/O
    disk_io = psutil.disk_io_counters()  # Get disk I/O statistics
    disk_io_info = {
        'read_bytes': get_size(disk_io.read_bytes),  # Total read bytes formatted
        'write_bytes': get_size(disk_io.write_bytes),  # Total write bytes formatted
        'read_bytes_raw': disk_io.read_bytes,  # Total read bytes raw (for charts)
        'write_bytes_raw': disk_io.write_bytes,  # Total write bytes raw (for charts)
        'read_count': disk_io.read_count,  # Total read operations
        'write_count': disk_io.write_count  # Total write operations
    }
    
    # Network I/O
    net_io = psutil.net_io_counters()  # Get network I/O statistics
    network_info = {
        'bytes_sent': get_size(net_io.bytes_sent),  # Total bytes sent formatted
        'bytes_recv': get_size(net_io.bytes_recv),  # Total bytes received formatted
        'bytes_sent_raw': net_io.bytes_sent,  # Total bytes sent raw
        'bytes_recv_raw': net_io.bytes_recv,  # Total bytes received raw
        'packets_sent': net_io.packets_sent,  # Total packets sent
        'packets_recv': net_io.packets_recv  # Total packets received
    }
    
    # Network connections
    try:
        connections = psutil.net_connections(kind='inet')  # Get network connections
        conn_stats = {
            'established': sum(1 for c in connections if c.status == 'ESTABLISHED'),  # Count established connections
            'listen': sum(1 for c in connections if c.status == 'LISTEN'),  # Count listening connections
            'time_wait': sum(1 for c in connections if c.status == 'TIME_WAIT'),  # Count time_wait connections
            'total': len(connections)  # Total connections
        }
    except Exception:
        conn_stats = {'established': 0, 'listen': 0, 'time_wait': 0, 'total': 0}  # Default if error

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
        )  # Make request to remote server
        response.raise_for_status()  # Raise error for bad status codes
        
        # Update last_seen
        server.last_seen = datetime.now(timezone.utc)  # Update last seen time
        db.session.commit()  # Commit changes to database
        
        return jsonify(response.json())  # Return remote metrics
    except Exception as e:
        current_app.logger.error(f"Error fetching metrics from {server.name}: {e}")  # Log error
        return jsonify({'error': 'Failed to fetch metrics from remote server'}), 500  # Return error response


@main.route('/api/network/connections')
@login_required  # Require login for this route
def network_connections():
    """API endpoint to get detailed network connection information."""
    status_filter = request.args.get('status')  # Get status filter from query params
    
    try:
        connections = psutil.net_connections(kind='inet')  # Get network connections
        
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


@main.route('/api/disk/io-processes')
@login_required  # Require login for this route
def disk_io_processes():
    """API endpoint to get processes sorted by I/O activity."""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):  # Iterate through processes
            try:
                # Get I/O counters for each process
                io_counters = proc.io_counters()
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'read_bytes': io_counters.read_bytes,
                    'write_bytes': io_counters.write_bytes,
                    'read_count': io_counters.read_count,
                    'write_count': io_counters.write_count,
                    'total_bytes': io_counters.read_bytes + io_counters.write_bytes
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                continue
        
        # Sort processes
        sort_by = request.args.get('sort', 'total')  # Get sort criteria
        
        if sort_by == 'read':
            processes.sort(key=lambda x: x['read_bytes'], reverse=True)
        elif sort_by == 'write':
            processes.sort(key=lambda x: x['write_bytes'], reverse=True)
        else:
            processes.sort(key=lambda x: x['total_bytes'], reverse=True)
        
        # Take top 50 processes
        top_processes = processes[:50]
        
        # Format bytes for display
        for proc in top_processes:
            proc['read_bytes_formatted'] = get_size(proc['read_bytes'])
            proc['write_bytes_formatted'] = get_size(proc['write_bytes'])
        
        return jsonify({
            'processes': top_processes,
            'count': len(top_processes)
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching I/O processes: {e}")
        return jsonify({
            'error': str(e),
            'processes': [],
            'count': 0
        }), 500


@main.route('/api/disk/analyze')
@login_required  # Require login for this route
def disk_analyze():
    """API endpoint to analyze disk space usage for a mountpoint."""
    mountpoint = request.args.get('mountpoint', '/')  # Get mountpoint
    
    try:
        import os
        from pathlib import Path
        
        # Safety check - only allow actual mountpoints
        partitions = psutil.disk_partitions()
        valid_mountpoints = [p.mountpoint for p in partitions]
        
        if mountpoint not in valid_mountpoints:
            return jsonify({'error': 'Invalid mountpoint'}), 400
        
        # Directories to skip for safety and performance
        skip_dirs = {'proc', 'sys', 'dev', 'run', 'tmp', 'snap', '.snapshots'}
        
        directory_sizes = {}
        
        # Scan directories (limited depth)
        base_path = Path(mountpoint)
        for item in base_path.iterdir():
            if item.name in skip_dirs or item.name.startswith('.'):
                continue
            
            if item.is_dir():
                try:
                    # Calculate directory size (with depth limit)
                    total_size = 0
                    file_count = 0
                    
                    for dirpath, dirnames, filenames in os.walk(item, topdown=True):
                        # Limit depth to 3 levels
                        depth = dirpath[len(str(item)):].count(os.sep)
                        if depth > 2:
                            dirnames[:] = []  # Don't recurse deeper
                            continue
                        
                        # Skip hidden and system directories
                        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in skip_dirs]
                        
                        for filename in filenames:
                            try:
                                filepath = os.path.join(dirpath, filename)
                                if not os.path.islink(filepath):
                                    total_size += os.path.getsize(filepath)
                                    file_count += 1
                            except (OSError, PermissionError):
                                continue
                        
                        # Limit processing to prevent timeout
                        if file_count > 100000:
                            break
                    
                    if total_size > 0:
                        directory_sizes[str(item)] = {
                            'size': total_size,
                            'size_formatted': get_size(total_size),
                            'file_count': file_count
                        }
                except (PermissionError, OSError):
                    continue
        
        # Sort by size and get top 10
        sorted_dirs = sorted(directory_sizes.items(), key=lambda x: x[1]['size'], reverse=True)[:10]
        
        result = [{
            'path': path,
            'size': info['size'],
            'size_formatted': info['size_formatted'],
            'file_count': info['file_count']
        } for path, info in sorted_dirs]
        
        return jsonify({
            'directories': result,
            'mountpoint': mountpoint,
            'count': len(result)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing disk {mountpoint}: {e}")
        return jsonify({
            'error': str(e),
            'directories': [],
            'count': 0
        }), 500


# ============================================================================
# HISTORICAL DATA API
# ============================================================================

@main.route('/api/metrics/history')
@login_required  # Require login for this route
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
@login_required  # Require login for this route
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
        
        # Sort processes
        sort_by = request.args.get('sort', 'cpu')
        
        if sort_by == 'memory':
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        else:
            # Default to CPU
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        return jsonify({'processes': processes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/processes/<int:pid>')
@login_required  # Require login for this route
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
@login_required  # Require login for this route
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
@login_required  # Require login for this route
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
@login_required  # Require login for this route
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
@login_required  # Require login for this route
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
@login_required  # Require login for this route
def test_alert(rule_id):
    """Test an alert notification."""
    notification_type = request.json.get('type', 'email')
    success, message = test_alert_notification(rule_id, notification_type)
    
    return jsonify({'success': success, 'message': message})


# ============================================================================
# SERVER MANAGEMENT API
# ============================================================================

@main.route('/api/servers', methods=['GET', 'POST'])
@login_required  # Require login for this route
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
@login_required  # Require login for this route
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
@login_required  # Require login for this route
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
@login_required  # Require login for this route
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
@login_required  # Require login for this route
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
@login_required  # Require login for this route
def health_dashboard():
    """Health check dashboard page."""
    return render_template('health.html')


@main.route('/api/health/services', methods=['GET'])
@login_required  # Require login for this route
def get_health_services():
    """Get all registered services with their health status."""
    from app.models import ServiceHealth
    
    services = ServiceHealth.query.all()
    return jsonify({
        'services': [{
            'id': s.id,
            'name': s.name,
            'url': s.url,
            'type': s.type,
            'status': s.status,
            'last_check': s.last_check.isoformat() if s.last_check else None,
            'response_time': s.response_time
        } for s in services]
    })
