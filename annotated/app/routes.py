"""Routes and view logic using Flask Blueprints."""  # """Routes and view logic using Flask Blueprints."""
import psutil  # import psutil
import requests  # import requests
from flask import Blueprint, jsonify, render_template, request, current_app  # from flask import Blueprint, jsonify, render_template, request, current_app
from flask_login import login_required, current_user  # from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone  # from datetime import datetime, timedelta, timezone
from app.models import (db, Server, SystemMetric, NetworkMetric, ProcessSnapshot,  # from app.models import (db, Server, SystemMetric, NetworkMetric, ProcessSnapshot,
                         AlertRule, AlertHistory, UserPreference)  # AlertRule, AlertHistory, UserPreference)
from app.export import export_metrics_to_csv, export_metrics_to_json, create_export_response  # from app.export import export_metrics_to_csv, export_metrics_to_json, create_export_response
from app.alerts import test_alert_notification  # from app.alerts import test_alert_notification
from sqlalchemy import func  # from sqlalchemy import func
  # blank line
main = Blueprint('main', __name__)  # main = Blueprint('main', __name__)
  # blank line
  # blank line
def get_size(bytes, suffix="B"):  # def get_size(bytes, suffix="B"):
    """Scale bytes to its proper format (e.g., 1253656 => '1.20MB')."""  # """Scale bytes to its proper format (e.g., 1253656 => '1.20MB')."""
    factor = 1024  # factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:  # for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:  # if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"  # return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor  # bytes /= factor
  # blank line
  # blank line
# ============================================================================  # # ============================================================================
# DASHBOARD ROUTES  # # DASHBOARD ROUTES
# ============================================================================  # # ============================================================================
  # blank line
@main.route('/')  # @main.route('/')
@login_required  # @login_required
def index():  # def index():
    """Render the main dashboard page."""  # """Render the main dashboard page."""
    servers = Server.query.filter_by(is_active=True).all()  # servers = Server.query.filter_by(is_active=True).all()
    preferences = current_user.preferences or UserPreference(user_id=current_user.id)  # preferences = current_user.preferences or UserPreference(user_id=current_user.id)
    return render_template('index.html', servers=servers, preferences=preferences)  # return render_template('index.html', servers=servers, preferences=preferences)
  # blank line
  # blank line
@main.route('/processes')  # @main.route('/processes')
@login_required  # @login_required
def processes():  # def processes():
    """Render the process monitoring page."""  # """Render the process monitoring page."""
    return render_template('processes.html')  # return render_template('processes.html')
  # blank line
  # blank line
@main.route('/alerts')  # @main.route('/alerts')
@login_required  # @login_required
def alerts_page():  # def alerts_page():
    """Render the alerts configuration page."""  # """Render the alerts configuration page."""
    servers = Server.query.filter_by(is_active=True).all()  # servers = Server.query.filter_by(is_active=True).all()
    return render_template('alerts.html', servers=servers)  # return render_template('alerts.html', servers=servers)
  # blank line
  # blank line
@main.route('/servers')  # @main.route('/servers')
@login_required  # @login_required
def servers_page():  # def servers_page():
    """Render the server management page."""  # """Render the server management page."""
    return render_template('servers.html')  # return render_template('servers.html')
  # blank line
  # blank line
@main.route('/settings')  # @main.route('/settings')
@login_required  # @login_required
def settings():  # def settings():
    """Render the user settings page."""  # """Render the user settings page."""
    preferences = current_user.preferences or UserPreference(user_id=current_user.id)  # preferences = current_user.preferences or UserPreference(user_id=current_user.id)
    servers = Server.query.filter_by(is_active=True).all()  # servers = Server.query.filter_by(is_active=True).all()
    return render_template('settings.html', preferences=preferences, servers=servers)  # return render_template('settings.html', preferences=preferences, servers=servers)
  # blank line
  # blank line
# ============================================================================  # # ============================================================================
# REAL-TIME METRICS API  # # REAL-TIME METRICS API
# ============================================================================  # # ============================================================================
  # blank line
@main.route('/api/metrics')  # @main.route('/api/metrics')
@login_required  # @login_required
def metrics():  # def metrics():
    """API endpoint to get real-time system metrics."""  # """API endpoint to get real-time system metrics."""
    server_id = request.args.get('server_id', type=int)  # server_id = request.args.get('server_id', type=int)
      # blank line
    # Get server (default to local if not specified)  # # Get server (default to local if not specified)
    if server_id:  # if server_id:
        server = Server.query.get(server_id)  # server = Server.query.get(server_id)
    else:  # else:
        server = Server.query.filter_by(is_local=True).first()  # server = Server.query.filter_by(is_local=True).first()
      # blank line
    if not server:  # if not server:
        return jsonify({'error': 'Server not found'}), 404  # return jsonify({'error': 'Server not found'}), 404
      # blank line
    # If remote server, fetch from agent  # # If remote server, fetch from agent
    if not server.is_local:  # if not server.is_local:
        return fetch_remote_metrics(server)  # return fetch_remote_metrics(server)
      # blank line
    # Collect local metrics  # # Collect local metrics
    cpu_percent = psutil.cpu_percent(interval=None)  # cpu_percent = psutil.cpu_percent(interval=None)
    cpu_freq = psutil.cpu_freq()  # cpu_freq = psutil.cpu_freq()
    cpu_freq_current = cpu_freq.current if cpu_freq else 0  # cpu_freq_current = cpu_freq.current if cpu_freq else 0
      # blank line
    # CPU temperature  # # CPU temperature
    cpu_temp_c = None  # cpu_temp_c = None
    cpu_temp_f = None  # cpu_temp_f = None
    try:  # try:
        temps = psutil.sensors_temperatures()  # temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:  # if 'coretemp' in temps:
            cpu_temp_c = temps['coretemp'][0].current  # cpu_temp_c = temps['coretemp'][0].current
        elif 'cpu_thermal' in temps:  # elif 'cpu_thermal' in temps:
            cpu_temp_c = temps['cpu_thermal'][0].current  # cpu_temp_c = temps['cpu_thermal'][0].current
        elif 'k10temp' in temps:  # elif 'k10temp' in temps:
            cpu_temp_c = temps['k10temp'][0].current  # cpu_temp_c = temps['k10temp'][0].current
          # blank line
        if cpu_temp_c is not None:  # if cpu_temp_c is not None:
            cpu_temp_f = (cpu_temp_c * 9/5) + 32  # cpu_temp_f = (cpu_temp_c * 9/5) + 32
    except Exception:  # except Exception:
        pass  # pass
  # blank line
    # Memory usage  # # Memory usage
    svmem = psutil.virtual_memory()  # svmem = psutil.virtual_memory()
    memory_usage = {  # memory_usage = {
        'total': get_size(svmem.total),  # 'total': get_size(svmem.total),
        'available': get_size(svmem.available),  # 'available': get_size(svmem.available),
        'used': get_size(svmem.used),  # 'used': get_size(svmem.used),
        'percent': svmem.percent  # 'percent': svmem.percent
    }  # }
  # blank line
    # Disk usage  # # Disk usage
    partitions = psutil.disk_partitions()  # partitions = psutil.disk_partitions()
    disk_usage_info = []  # disk_usage_info = []
    for partition in partitions:  # for partition in partitions:
        try:  # try:
            partition_usage = psutil.disk_usage(partition.mountpoint)  # partition_usage = psutil.disk_usage(partition.mountpoint)
            disk_usage_info.append({  # disk_usage_info.append({
                'device': partition.device,  # 'device': partition.device,
                'mountpoint': partition.mountpoint,  # 'mountpoint': partition.mountpoint,
                'total': get_size(partition_usage.total),  # 'total': get_size(partition_usage.total),
                'used': get_size(partition_usage.used),  # 'used': get_size(partition_usage.used),
                'free': get_size(partition_usage.free),  # 'free': get_size(partition_usage.free),
                'percent': partition_usage.percent  # 'percent': partition_usage.percent
            })  # })
        except PermissionError:  # except PermissionError:
            continue  # continue
  # blank line
    # Disk I/O  # # Disk I/O
    disk_io = psutil.disk_io_counters()  # disk_io = psutil.disk_io_counters()
    disk_io_info = {  # disk_io_info = {
        'read_bytes': get_size(disk_io.read_bytes),  # 'read_bytes': get_size(disk_io.read_bytes),
        'write_bytes': get_size(disk_io.write_bytes),  # 'write_bytes': get_size(disk_io.write_bytes),
        'read_count': disk_io.read_count,  # 'read_count': disk_io.read_count,
        'write_count': disk_io.write_count  # 'write_count': disk_io.write_count
    }  # }
      # blank line
    # Network I/O  # # Network I/O
    net_io = psutil.net_io_counters()  # net_io = psutil.net_io_counters()
    network_info = {  # network_info = {
        'bytes_sent': get_size(net_io.bytes_sent),  # 'bytes_sent': get_size(net_io.bytes_sent),
        'bytes_recv': get_size(net_io.bytes_recv),  # 'bytes_recv': get_size(net_io.bytes_recv),
        'bytes_sent_raw': net_io.bytes_sent,  # 'bytes_sent_raw': net_io.bytes_sent,
        'bytes_recv_raw': net_io.bytes_recv,  # 'bytes_recv_raw': net_io.bytes_recv,
        'packets_sent': net_io.packets_sent,  # 'packets_sent': net_io.packets_sent,
        'packets_recv': net_io.packets_recv  # 'packets_recv': net_io.packets_recv
    }  # }
      # blank line
    # Network connections  # # Network connections
    try:  # try:
        connections = psutil.net_connections(kind='inet')  # connections = psutil.net_connections(kind='inet')
        conn_stats = {  # conn_stats = {
            'established': sum(1 for c in connections if c.status == 'ESTABLISHED'),  # 'established': sum(1 for c in connections if c.status == 'ESTABLISHED'),
            'listen': sum(1 for c in connections if c.status == 'LISTEN'),  # 'listen': sum(1 for c in connections if c.status == 'LISTEN'),
            'time_wait': sum(1 for c in connections if c.status == 'TIME_WAIT'),  # 'time_wait': sum(1 for c in connections if c.status == 'TIME_WAIT'),
            'total': len(connections)  # 'total': len(connections)
        }  # }
    except Exception:  # except Exception:
        conn_stats = {'established': 0, 'listen': 0, 'time_wait': 0, 'total': 0}  # conn_stats = {'established': 0, 'listen': 0, 'time_wait': 0, 'total': 0}
  # blank line
    return jsonify({  # return jsonify({
        'cpu': {  # 'cpu': {
            'percent': cpu_percent,  # 'percent': cpu_percent,
            'freq': f"{cpu_freq_current:.2f}Mhz",  # 'freq': f"{cpu_freq_current:.2f}Mhz",
            'temp_c': cpu_temp_c,  # 'temp_c': cpu_temp_c,
            'temp_f': cpu_temp_f  # 'temp_f': cpu_temp_f
        },  # },
        'memory': memory_usage,  # 'memory': memory_usage,
        'disk': disk_usage_info,  # 'disk': disk_usage_info,
        'io': disk_io_info,  # 'io': disk_io_info,
        'network': network_info,  # 'network': network_info,
        'connections': conn_stats  # 'connections': conn_stats
    })  # })
  # blank line
  # blank line
def fetch_remote_metrics(server):  # def fetch_remote_metrics(server):
    """Fetch metrics from a remote server agent."""  # """Fetch metrics from a remote server agent."""
    try:  # try:
        response = requests.get(  # response = requests.get(
            f"http://{server.hostname}/api/metrics",  # f"http://{server.hostname}/api/metrics",
            headers={'X-API-Key': server.api_key},  # headers={'X-API-Key': server.api_key},
            timeout=5  # timeout=5
        )  # )
        response.raise_for_status()  # response.raise_for_status()
          # blank line
        # Update last_seen  # # Update last_seen
        server.last_seen = datetime.now(timezone.utc)  # server.last_seen = datetime.now(timezone.utc)
        db.session.commit()  # db.session.commit()
          # blank line
        return jsonify(response.json())  # return jsonify(response.json())
    except Exception as e:  # except Exception as e:
        current_app.logger.error(f"Error fetching metrics from {server.name}: {e}")  # current_app.logger.error(f"Error fetching metrics from {server.name}: {e}")
        return jsonify({'error': 'Failed to fetch metrics from remote server'}), 500  # return jsonify({'error': 'Failed to fetch metrics from remote server'}), 500
  # blank line
  # blank line
@main.route('/api/network/connections')  # @main.route('/api/network/connections')
@login_required  # @login_required
def network_connections():  # def network_connections():
    """API endpoint to get detailed network connection information."""  # """API endpoint to get detailed network connection information."""
    status_filter = request.args.get('status')  # status_filter = request.args.get('status')
      # blank line
    try:  # try:
        connections = psutil.net_connections(kind='inet')  # connections = psutil.net_connections(kind='inet')
          # blank line
        # Filter by status if specified  # # Filter by status if specified
        if status_filter:  # if status_filter:
            connections = [c for c in connections if c.status == status_filter.upper()]  # connections = [c for c in connections if c.status == status_filter.upper()]
          # blank line
        connection_list = []  # connection_list = []
        for conn in connections:  # for conn in connections:
            # Get process information if available  # # Get process information if available
            process_name = None  # process_name = None
            try:  # try:
                if conn.pid:  # if conn.pid:
                    proc = psutil.Process(conn.pid)  # proc = psutil.Process(conn.pid)
                    process_name = proc.name()  # process_name = proc.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):  # except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass  # pass
              # blank line
            # Format connection data  # # Format connection data
            conn_data = {  # conn_data = {
                'protocol': 'TCP' if conn.type == 1 else 'UDP',  # 'protocol': 'TCP' if conn.type == 1 else 'UDP',
                'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else 'N/A',  # 'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else 'N/A',
                'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else 'N/A',  # 'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else 'N/A',
                'status': conn.status,  # 'status': conn.status,
                'pid': conn.pid if conn.pid else 'N/A',  # 'pid': conn.pid if conn.pid else 'N/A',
                'process': process_name if process_name else 'N/A'  # 'process': process_name if process_name else 'N/A'
            }  # }
            connection_list.append(conn_data)  # connection_list.append(conn_data)
          # blank line
        return jsonify({  # return jsonify({
            'connections': connection_list,  # 'connections': connection_list,
            'count': len(connection_list)  # 'count': len(connection_list)
        })  # })
    except PermissionError:  # except PermissionError:
        return jsonify({  # return jsonify({
            'error': 'Permission denied. Root/admin privileges may be required.',  # 'error': 'Permission denied. Root/admin privileges may be required.',
            'connections': [],  # 'connections': [],
            'count': 0  # 'count': 0
        }), 403  # }), 403
    except Exception as e:  # except Exception as e:
        current_app.logger.error(f"Error fetching network connections: {e}")  # current_app.logger.error(f"Error fetching network connections: {e}")
        return jsonify({  # return jsonify({
            'error': str(e),  # 'error': str(e),
            'connections': [],  # 'connections': [],
            'count': 0  # 'count': 0
        }), 500  # }), 500
  # blank line
  # blank line
@main.route('/api/disk/io-processes')  # @main.route('/api/disk/io-processes')
@login_required  # @login_required
def disk_io_processes():  # def disk_io_processes():
    """API endpoint to get processes sorted by I/O activity."""  # """API endpoint to get processes sorted by I/O activity."""
    try:  # try:
        processes = []  # processes = []
        for proc in psutil.process_iter(['pid', 'name']):  # for proc in psutil.process_iter(['pid', 'name']):
            try:  # try:
                # Get I/O counters for each process  # # Get I/O counters for each process
                io_counters = proc.io_counters()  # io_counters = proc.io_counters()
                processes.append({  # processes.append({
                    'pid': proc.info['pid'],  # 'pid': proc.info['pid'],
                    'name': proc.info['name'],  # 'name': proc.info['name'],
                    'read_bytes': io_counters.read_bytes,  # 'read_bytes': io_counters.read_bytes,
                    'write_bytes': io_counters.write_bytes,  # 'write_bytes': io_counters.write_bytes,
                    'read_count': io_counters.read_count,  # 'read_count': io_counters.read_count,
                    'write_count': io_counters.write_count,  # 'write_count': io_counters.write_count,
                    'total_bytes': io_counters.read_bytes + io_counters.write_bytes  # 'total_bytes': io_counters.read_bytes + io_counters.write_bytes
                })  # })
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):  # except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                continue  # continue
          # blank line
        # Sort by total I/O (descending)  # # Sort by total I/O (descending)
        processes.sort(key=lambda x: x['total_bytes'], reverse=True)  # processes.sort(key=lambda x: x['total_bytes'], reverse=True)
          # blank line
        # Take top 50 processes  # # Take top 50 processes
        top_processes = processes[:50]  # top_processes = processes[:50]
          # blank line
        # Format bytes for display  # # Format bytes for display
        for proc in top_processes:  # for proc in top_processes:
            proc['read_bytes_formatted'] = get_size(proc['read_bytes'])  # proc['read_bytes_formatted'] = get_size(proc['read_bytes'])
            proc['write_bytes_formatted'] = get_size(proc['write_bytes'])  # proc['write_bytes_formatted'] = get_size(proc['write_bytes'])
          # blank line
        return jsonify({  # return jsonify({
            'processes': top_processes,  # 'processes': top_processes,
            'count': len(top_processes)  # 'count': len(top_processes)
        })  # })
    except Exception as e:  # except Exception as e:
        current_app.logger.error(f"Error fetching I/O processes: {e}")  # current_app.logger.error(f"Error fetching I/O processes: {e}")
        return jsonify({  # return jsonify({
            'error': str(e),  # 'error': str(e),
            'processes': [],  # 'processes': [],
            'count': 0  # 'count': 0
        }), 500  # }), 500
  # blank line
  # blank line
@main.route('/api/disk/analyze')  # @main.route('/api/disk/analyze')
@login_required  # @login_required
def disk_analyze():  # def disk_analyze():
    """API endpoint to analyze disk space usage for a mountpoint."""  # """API endpoint to analyze disk space usage for a mountpoint."""
    mountpoint = request.args.get('mountpoint', '/')  # mountpoint = request.args.get('mountpoint', '/')
      # blank line
    try:  # try:
        import os  # import os
        from pathlib import Path  # from pathlib import Path
          # blank line
        # Safety check - only allow actual mountpoints  # # Safety check - only allow actual mountpoints
        partitions = psutil.disk_partitions()  # partitions = psutil.disk_partitions()
        valid_mountpoints = [p.mountpoint for p in partitions]  # valid_mountpoints = [p.mountpoint for p in partitions]
          # blank line
        if mountpoint not in valid_mountpoints:  # if mountpoint not in valid_mountpoints:
            return jsonify({'error': 'Invalid mountpoint'}), 400  # return jsonify({'error': 'Invalid mountpoint'}), 400
          # blank line
        # Directories to skip for safety and performance  # # Directories to skip for safety and performance
        skip_dirs = {'proc', 'sys', 'dev', 'run', 'tmp', 'snap', '.snapshots'}  # skip_dirs = {'proc', 'sys', 'dev', 'run', 'tmp', 'snap', '.snapshots'}
          # blank line
        directory_sizes = {}  # directory_sizes = {}
          # blank line
        # Scan directories (limited depth)  # # Scan directories (limited depth)
        base_path = Path(mountpoint)  # base_path = Path(mountpoint)
        for item in base_path.iterdir():  # for item in base_path.iterdir():
            if item.name in skip_dirs or item.name.startswith('.'):  # if item.name in skip_dirs or item.name.startswith('.'):
                continue  # continue
              # blank line
            if item.is_dir():  # if item.is_dir():
                try:  # try:
                    # Calculate directory size (with depth limit)  # # Calculate directory size (with depth limit)
                    total_size = 0  # total_size = 0
                    file_count = 0  # file_count = 0
                      # blank line
                    for dirpath, dirnames, filenames in os.walk(item, topdown=True):  # for dirpath, dirnames, filenames in os.walk(item, topdown=True):
                        # Limit depth to 3 levels  # # Limit depth to 3 levels
                        depth = dirpath[len(str(item)):].count(os.sep)  # depth = dirpath[len(str(item)):].count(os.sep)
                        if depth > 2:  # if depth > 2:
                            dirnames[:] = []  # Don't recurse deeper  # dirnames[:] = []  # Don't recurse deeper
                            continue  # continue
                          # blank line
                        # Skip hidden and system directories  # # Skip hidden and system directories
                        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in skip_dirs]  # dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in skip_dirs]
                          # blank line
                        for filename in filenames:  # for filename in filenames:
                            try:  # try:
                                filepath = os.path.join(dirpath, filename)  # filepath = os.path.join(dirpath, filename)
                                if not os.path.islink(filepath):  # if not os.path.islink(filepath):
                                    total_size += os.path.getsize(filepath)  # total_size += os.path.getsize(filepath)
                                    file_count += 1  # file_count += 1
                            except (OSError, PermissionError):  # except (OSError, PermissionError):
                                continue  # continue
                          # blank line
                        # Limit processing to prevent timeout  # # Limit processing to prevent timeout
                        if file_count > 100000:  # if file_count > 100000:
                            break  # break
                      # blank line
                    if total_size > 0:  # if total_size > 0:
                        directory_sizes[str(item)] = {  # directory_sizes[str(item)] = {
                            'size': total_size,  # 'size': total_size,
                            'size_formatted': get_size(total_size),  # 'size_formatted': get_size(total_size),
                            'file_count': file_count  # 'file_count': file_count
                        }  # }
                except (PermissionError, OSError):  # except (PermissionError, OSError):
                    continue  # continue
          # blank line
        # Sort by size and get top 10  # # Sort by size and get top 10
        sorted_dirs = sorted(directory_sizes.items(), key=lambda x: x[1]['size'], reverse=True)[:10]  # sorted_dirs = sorted(directory_sizes.items(), key=lambda x: x[1]['size'], reverse=True)[:10]
          # blank line
        result = [{  # result = [{
            'path': path,  # 'path': path,
            'size': info['size'],  # 'size': info['size'],
            'size_formatted': info['size_formatted'],  # 'size_formatted': info['size_formatted'],
            'file_count': info['file_count']  # 'file_count': info['file_count']
        } for path, info in sorted_dirs]  # } for path, info in sorted_dirs]
          # blank line
        return jsonify({  # return jsonify({
            'directories': result,  # 'directories': result,
            'mountpoint': mountpoint,  # 'mountpoint': mountpoint,
            'count': len(result)  # 'count': len(result)
        })  # })
          # blank line
    except Exception as e:  # except Exception as e:
        current_app.logger.error(f"Error analyzing disk {mountpoint}: {e}")  # current_app.logger.error(f"Error analyzing disk {mountpoint}: {e}")
        return jsonify({  # return jsonify({
            'error': str(e),  # 'error': str(e),
            'directories': [],  # 'directories': [],
            'count': 0  # 'count': 0
        }), 500  # }), 500
  # blank line
  # blank line
# ============================================================================  # # ============================================================================
# HISTORICAL DATA API  # # HISTORICAL DATA API
# ============================================================================  # # ============================================================================
  # blank line
@main.route('/api/metrics/history')  # @main.route('/api/metrics/history')
@login_required  # @login_required
def metrics_history():  # def metrics_history():
    """Get historical metrics data."""  # """Get historical metrics data."""
    server_id = request.args.get('server_id', type=int)  # server_id = request.args.get('server_id', type=int)
    hours = request.args.get('hours', default=24, type=int)  # hours = request.args.get('hours', default=24, type=int)
    metric_type = request.args.get('type', default='system')  # metric_type = request.args.get('type', default='system')
      # blank line
    if not server_id:  # if not server_id:
        server = Server.query.filter_by(is_local=True).first()  # server = Server.query.filter_by(is_local=True).first()
        server_id = server.id if server else None  # server_id = server.id if server else None
      # blank line
    if not server_id:  # if not server_id:
        return jsonify({'error': 'Server not found'}), 404  # return jsonify({'error': 'Server not found'}), 404
      # blank line
    start_time = datetime.now(timezone.utc) - timedelta(hours=hours)  # start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
      # blank line
    if metric_type == 'system':  # if metric_type == 'system':
        metrics = SystemMetric.query.filter(  # metrics = SystemMetric.query.filter(
            SystemMetric.server_id == server_id,  # SystemMetric.server_id == server_id,
            SystemMetric.timestamp >= start_time  # SystemMetric.timestamp >= start_time
        ).order_by(SystemMetric.timestamp).all()  # ).order_by(SystemMetric.timestamp).all()
          # blank line
        data = [{  # data = [{
            'timestamp': m.timestamp.isoformat(),  # 'timestamp': m.timestamp.isoformat(),
            'cpu_percent': m.cpu_percent,  # 'cpu_percent': m.cpu_percent,
            'memory_percent': m.memory_percent,  # 'memory_percent': m.memory_percent,
            'disk_percent': m.disk_percent,  # 'disk_percent': m.disk_percent,
            'cpu_temp_c': m.cpu_temp_c  # 'cpu_temp_c': m.cpu_temp_c
        } for m in metrics]  # } for m in metrics]
          # blank line
    elif metric_type == 'network':  # elif metric_type == 'network':
        metrics = NetworkMetric.query.filter(  # metrics = NetworkMetric.query.filter(
            NetworkMetric.server_id == server_id,  # NetworkMetric.server_id == server_id,
            NetworkMetric.timestamp >= start_time  # NetworkMetric.timestamp >= start_time
        ).order_by(NetworkMetric.timestamp).all()  # ).order_by(NetworkMetric.timestamp).all()
          # blank line
        data = [{  # data = [{
            'timestamp': m.timestamp.isoformat(),  # 'timestamp': m.timestamp.isoformat(),
            'bytes_sent': m.bytes_sent,  # 'bytes_sent': m.bytes_sent,
            'bytes_recv': m.bytes_recv,  # 'bytes_recv': m.bytes_recv,
            'connections_established': m.connections_established  # 'connections_established': m.connections_established
        } for m in metrics]  # } for m in metrics]
    else:  # else:
        return jsonify({'error': 'Invalid metric type'}), 400  # return jsonify({'error': 'Invalid metric type'}), 400
      # blank line
    return jsonify({'data': data})  # return jsonify({'data': data})
  # blank line
  # blank line
# ============================================================================  # # ============================================================================
# PROCESS MONITORING API  # # PROCESS MONITORING API
# ============================================================================  # # ============================================================================
  # blank line
@main.route('/api/processes')  # @main.route('/api/processes')
@login_required  # @login_required
def get_processes():  # def get_processes():
    """Get list of running processes."""  # """Get list of running processes."""
    try:  # try:
        processes = []  # processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):  # for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:  # try:
                pinfo = proc.info  # pinfo = proc.info
                processes.append({  # processes.append({
                    'pid': pinfo['pid'],  # 'pid': pinfo['pid'],
                    'name': pinfo['name'],  # 'name': pinfo['name'],
                    'username': pinfo['username'],  # 'username': pinfo['username'],
                    'cpu_percent': pinfo['cpu_percent'] or 0,  # 'cpu_percent': pinfo['cpu_percent'] or 0,
                    'memory_percent': pinfo['memory_percent'] or 0,  # 'memory_percent': pinfo['memory_percent'] or 0,
                    'status': pinfo['status']  # 'status': pinfo['status']
                })  # })
            except (psutil.NoSuchProcess, psutil.AccessDenied):  # except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue  # continue
          # blank line
        # Sort by CPU usage (descending)  # # Sort by CPU usage (descending)
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)  # processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
          # blank line
        return jsonify({'processes': processes})  # return jsonify({'processes': processes})
    except Exception as e:  # except Exception as e:
        return jsonify({'error': str(e)}), 500  # return jsonify({'error': str(e)}), 500
  # blank line
  # blank line
@main.route('/api/processes/<int:pid>')  # @main.route('/api/processes/<int:pid>')
@login_required  # @login_required
def get_process_details(pid):  # def get_process_details(pid):
    """Get detailed information about a specific process."""  # """Get detailed information about a specific process."""
    try:  # try:
        proc = psutil.Process(pid)  # proc = psutil.Process(pid)
        info = proc.as_dict(attrs=['pid', 'name', 'username', 'status', 'create_time',  # info = proc.as_dict(attrs=['pid', 'name', 'username', 'status', 'create_time',
                                     'cpu_percent', 'memory_percent', 'memory_info',  # 'cpu_percent', 'memory_percent', 'memory_info',
                                     'num_threads', 'cmdline'])  # 'num_threads', 'cmdline'])
          # blank line
        info['create_time'] = datetime.fromtimestamp(info['create_time']).isoformat()  # info['create_time'] = datetime.fromtimestamp(info['create_time']).isoformat()
        info['memory_rss'] = get_size(info['memory_info'].rss) if info.get('memory_info') else 'N/A'  # info['memory_rss'] = get_size(info['memory_info'].rss) if info.get('memory_info') else 'N/A'
          # blank line
        return jsonify(info)  # return jsonify(info)
    except psutil.NoSuchProcess:  # except psutil.NoSuchProcess:
        return jsonify({'error': 'Process not found'}), 404  # return jsonify({'error': 'Process not found'}), 404
    except Exception as e:  # except Exception as e:
        return jsonify({'error': str(e)}), 500  # return jsonify({'error': str(e)}), 500
  # blank line
  # blank line
@main.route('/api/processes/<int:pid>/kill', methods=['POST'])  # @main.route('/api/processes/<int:pid>/kill', methods=['POST'])
@login_required  # @login_required
def kill_process(pid):  # def kill_process(pid):
    """Terminate a process."""  # """Terminate a process."""
    if not current_user.is_admin:  # if not current_user.is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403  # return jsonify({'error': 'Admin privileges required'}), 403
      # blank line
    try:  # try:
        proc = psutil.Process(pid)  # proc = psutil.Process(pid)
        proc.terminate()  # proc.terminate()
        return jsonify({'success': True, 'message': f'Process {pid} terminated'})  # return jsonify({'success': True, 'message': f'Process {pid} terminated'})
    except psutil.NoSuchProcess:  # except psutil.NoSuchProcess:
        return jsonify({'error': 'Process not found'}), 404  # return jsonify({'error': 'Process not found'}), 404
    except psutil.AccessDenied:  # except psutil.AccessDenied:
        return jsonify({'error': 'Access denied'}), 403  # return jsonify({'error': 'Access denied'}), 403
    except Exception as e:  # except Exception as e:
        return jsonify({'error': str(e)}), 500  # return jsonify({'error': str(e)}), 500
  # blank line
  # blank line
# ============================================================================  # # ============================================================================
# ALERT MANAGEMENT API  # # ALERT MANAGEMENT API
# ============================================================================  # # ============================================================================
  # blank line
@main.route('/api/alerts/rules', methods=['GET', 'POST'])  # @main.route('/api/alerts/rules', methods=['GET', 'POST'])
@login_required  # @login_required
def alert_rules():  # def alert_rules():
    """Get all alert rules or create a new one."""  # """Get all alert rules or create a new one."""
    if request.method == 'GET':  # if request.method == 'GET':
        rules = AlertRule.query.filter_by(user_id=current_user.id).all()  # rules = AlertRule.query.filter_by(user_id=current_user.id).all()
        return jsonify({  # return jsonify({
            'rules': [{  # 'rules': [{
                'id': r.id,  # 'id': r.id,
                'name': r.name,  # 'name': r.name,
                'metric_type': r.metric_type,  # 'metric_type': r.metric_type,
                'threshold': r.threshold,  # 'threshold': r.threshold,
                'comparison': r.comparison,  # 'comparison': r.comparison,
                'server_id': r.server_id,  # 'server_id': r.server_id,
                'notify_email': r.notify_email,  # 'notify_email': r.notify_email,
                'notify_sms': r.notify_sms,  # 'notify_sms': r.notify_sms,
                'is_active': r.is_active  # 'is_active': r.is_active
            } for r in rules]  # } for r in rules]
        })  # })
      # blank line
    elif request.method == 'POST':  # elif request.method == 'POST':
        data = request.json  # data = request.json
          # blank line
        rule = AlertRule(  # rule = AlertRule(
            user_id=current_user.id,  # user_id=current_user.id,
            name=data['name'],  # name=data['name'],
            metric_type=data['metric_type'],  # metric_type=data['metric_type'],
            threshold=float(data['threshold']),  # threshold=float(data['threshold']),
            comparison=data['comparison'],  # comparison=data['comparison'],
            server_id=data.get('server_id'),  # server_id=data.get('server_id'),
            duration=int(data.get('duration', 60)),  # duration=int(data.get('duration', 60)),
            notify_email=data.get('notify_email', True),  # notify_email=data.get('notify_email', True),
            notify_sms=data.get('notify_sms', False),  # notify_sms=data.get('notify_sms', False),
            email_address=data.get('email_address'),  # email_address=data.get('email_address'),
            phone_number=data.get('phone_number'),  # phone_number=data.get('phone_number'),
            is_active=data.get('is_active', True)  # is_active=data.get('is_active', True)
        )  # )
          # blank line
        db.session.add(rule)  # db.session.add(rule)
        db.session.commit()  # db.session.commit()
          # blank line
        return jsonify({'success': True, 'id': rule.id}), 201  # return jsonify({'success': True, 'id': rule.id}), 201
  # blank line
  # blank line
@main.route('/api/alerts/rules/<int:rule_id>', methods=['PUT', 'DELETE'])  # @main.route('/api/alerts/rules/<int:rule_id>', methods=['PUT', 'DELETE'])
@login_required  # @login_required
def alert_rule_detail(rule_id):  # def alert_rule_detail(rule_id):
    """Update or delete an alert rule."""  # """Update or delete an alert rule."""
    rule = AlertRule.query.get(rule_id)  # rule = AlertRule.query.get(rule_id)
      # blank line
    if not rule or rule.user_id != current_user.id:  # if not rule or rule.user_id != current_user.id:
        return jsonify({'error': 'Alert rule not found'}), 404  # return jsonify({'error': 'Alert rule not found'}), 404
      # blank line
    if request.method == 'PUT':  # if request.method == 'PUT':
        data = request.json  # data = request.json
        rule.name = data.get('name', rule.name)  # rule.name = data.get('name', rule.name)
        rule.threshold = float(data.get('threshold', rule.threshold))  # rule.threshold = float(data.get('threshold', rule.threshold))
        rule.is_active = data.get('is_active', rule.is_active)  # rule.is_active = data.get('is_active', rule.is_active)
        rule.notify_email = data.get('notify_email', rule.notify_email)  # rule.notify_email = data.get('notify_email', rule.notify_email)
        rule.notify_sms = data.get('notify_sms', rule.notify_sms)  # rule.notify_sms = data.get('notify_sms', rule.notify_sms)
          # blank line
        db.session.commit()  # db.session.commit()
        return jsonify({'success': True})  # return jsonify({'success': True})
      # blank line
    elif request.method == 'DELETE':  # elif request.method == 'DELETE':
        db.session.delete(rule)  # db.session.delete(rule)
        db.session.commit()  # db.session.commit()
        return jsonify({'success': True})  # return jsonify({'success': True})
  # blank line
  # blank line
@main.route('/api/alerts/history')  # @main.route('/api/alerts/history')
@login_required  # @login_required
def alert_history():  # def alert_history():
    """Get alert history."""  # """Get alert history."""
    limit = request.args.get('limit', default=50, type=int)  # limit = request.args.get('limit', default=50, type=int)
      # blank line
    history = AlertHistory.query.join(AlertRule).filter(  # history = AlertHistory.query.join(AlertRule).filter(
        AlertRule.user_id == current_user.id  # AlertRule.user_id == current_user.id
    ).order_by(AlertHistory.triggered_at.desc()).limit(limit).all()  # ).order_by(AlertHistory.triggered_at.desc()).limit(limit).all()
      # blank line
    return jsonify({  # return jsonify({
        'history': [{  # 'history': [{
            'id': h.id,  # 'id': h.id,
            'rule_name': h.rule.name,  # 'rule_name': h.rule.name,
            'server_name': Server.query.get(h.server_id).name,  # 'server_name': Server.query.get(h.server_id).name,
            'metric_value': h.metric_value,  # 'metric_value': h.metric_value,
            'message': h.message,  # 'message': h.message,
            'triggered_at': h.triggered_at.isoformat(),  # 'triggered_at': h.triggered_at.isoformat(),
            'email_sent': h.email_sent,  # 'email_sent': h.email_sent,
            'sms_sent': h.sms_sent,  # 'sms_sent': h.sms_sent,
            'acknowledged': h.acknowledged  # 'acknowledged': h.acknowledged
        } for h in history]  # } for h in history]
    })  # })
  # blank line
  # blank line
@main.route('/api/alerts/test/<int:rule_id>', methods=['POST'])  # @main.route('/api/alerts/test/<int:rule_id>', methods=['POST'])
@login_required  # @login_required
def test_alert(rule_id):  # def test_alert(rule_id):
    """Test an alert notification."""  # """Test an alert notification."""
    notification_type = request.json.get('type', 'email')  # notification_type = request.json.get('type', 'email')
    success, message = test_alert_notification(rule_id, notification_type)  # success, message = test_alert_notification(rule_id, notification_type)
      # blank line
    return jsonify({'success': success, 'message': message})  # return jsonify({'success': success, 'message': message})
  # blank line
  # blank line
# ============================================================================  # # ============================================================================
# SERVER MANAGEMENT API  # # SERVER MANAGEMENT API
# ============================================================================  # # ============================================================================
  # blank line
@main.route('/api/servers', methods=['GET', 'POST'])  # @main.route('/api/servers', methods=['GET', 'POST'])
@login_required  # @login_required
def servers_api():  # def servers_api():
    """Get all servers or add a new one."""  # """Get all servers or add a new one."""
    if request.method == 'GET':  # if request.method == 'GET':
        servers = Server.query.all()  # servers = Server.query.all()
        return jsonify({  # return jsonify({
            'servers': [{  # 'servers': [{
                'id': s.id,  # 'id': s.id,
                'name': s.name,  # 'name': s.name,
                'hostname': s.hostname,  # 'hostname': s.hostname,
                'is_active': s.is_active,  # 'is_active': s.is_active,
                'is_local': s.is_local,  # 'is_local': s.is_local,
                'last_seen': s.last_seen.isoformat() if s.last_seen else None  # 'last_seen': s.last_seen.isoformat() if s.last_seen else None
            } for s in servers]  # } for s in servers]
        })  # })
      # blank line
    elif request.method == 'POST':  # elif request.method == 'POST':
        if not current_user.is_admin:  # if not current_user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403  # return jsonify({'error': 'Admin privileges required'}), 403
          # blank line
        data = request.json  # data = request.json
          # blank line
        server = Server(  # server = Server(
            name=data['name'],  # name=data['name'],
            hostname=data['hostname'],  # hostname=data['hostname'],
            api_key=data['api_key'],  # api_key=data['api_key'],
            is_active=True,  # is_active=True,
            is_local=False  # is_local=False
        )  # )
          # blank line
        db.session.add(server)  # db.session.add(server)
        db.session.commit()  # db.session.commit()
          # blank line
        return jsonify({'success': True, 'id': server.id}), 201  # return jsonify({'success': True, 'id': server.id}), 201
  # blank line
  # blank line
@main.route('/api/servers/<int:server_id>', methods=['PUT', 'DELETE'])  # @main.route('/api/servers/<int:server_id>', methods=['PUT', 'DELETE'])
@login_required  # @login_required
def server_detail(server_id):  # def server_detail(server_id):
    """Update or delete a server."""  # """Update or delete a server."""
    if not current_user.is_admin:  # if not current_user.is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403  # return jsonify({'error': 'Admin privileges required'}), 403
      # blank line
    server = Server.query.get(server_id)  # server = Server.query.get(server_id)
      # blank line
    if not server or server.is_local:  # if not server or server.is_local:
        return jsonify({'error': 'Server not found or cannot modify local server'}), 404  # return jsonify({'error': 'Server not found or cannot modify local server'}), 404
      # blank line
    if request.method == 'PUT':  # if request.method == 'PUT':
        data = request.json  # data = request.json
        server.name = data.get('name', server.name)  # server.name = data.get('name', server.name)
        server.hostname = data.get('hostname', server.hostname)  # server.hostname = data.get('hostname', server.hostname)
        server.is_active = data.get('is_active', server.is_active)  # server.is_active = data.get('is_active', server.is_active)
          # blank line
        db.session.commit()  # db.session.commit()
        return jsonify({'success': True})  # return jsonify({'success': True})
      # blank line
    elif request.method == 'DELETE':  # elif request.method == 'DELETE':
        db.session.delete(server)  # db.session.delete(server)
        db.session.commit()  # db.session.commit()
        return jsonify({'success': True})  # return jsonify({'success': True})
  # blank line
  # blank line
# ============================================================================  # # ============================================================================
# USER SETTINGS API  # # USER SETTINGS API
# ============================================================================  # # ============================================================================
  # blank line
@main.route('/api/settings', methods=['GET', 'PUT'])  # @main.route('/api/settings', methods=['GET', 'PUT'])
@login_required  # @login_required
def user_settings():  # def user_settings():
    """Get or update user preferences."""  # """Get or update user preferences."""
    preferences = current_user.preferences  # preferences = current_user.preferences
      # blank line
    if not preferences:  # if not preferences:
        preferences = UserPreference(user_id=current_user.id)  # preferences = UserPreference(user_id=current_user.id)
        db.session.add(preferences)  # db.session.add(preferences)
        db.session.commit()  # db.session.commit()
      # blank line
    if request.method == 'GET':  # if request.method == 'GET':
        return jsonify({  # return jsonify({
            'refresh_interval': preferences.refresh_interval,  # 'refresh_interval': preferences.refresh_interval,
            'chart_data_points': preferences.chart_data_points,  # 'chart_data_points': preferences.chart_data_points,
            'theme': preferences.theme,  # 'theme': preferences.theme,
            'default_server_id': preferences.default_server_id,  # 'default_server_id': preferences.default_server_id,
            'email_notifications': preferences.email_notifications,  # 'email_notifications': preferences.email_notifications,
            'sms_notifications': preferences.sms_notifications  # 'sms_notifications': preferences.sms_notifications
        })  # })
      # blank line
    elif request.method == 'PUT':  # elif request.method == 'PUT':
        data = request.json  # data = request.json
          # blank line
        preferences.refresh_interval = data.get('refresh_interval', preferences.refresh_interval)  # preferences.refresh_interval = data.get('refresh_interval', preferences.refresh_interval)
        preferences.chart_data_points = data.get('chart_data_points', preferences.chart_data_points)  # preferences.chart_data_points = data.get('chart_data_points', preferences.chart_data_points)
        preferences.theme = data.get('theme', preferences.theme)  # preferences.theme = data.get('theme', preferences.theme)
        preferences.default_server_id = data.get('default_server_id', preferences.default_server_id)  # preferences.default_server_id = data.get('default_server_id', preferences.default_server_id)
        preferences.email_notifications = data.get('email_notifications', preferences.email_notifications)  # preferences.email_notifications = data.get('email_notifications', preferences.email_notifications)
        preferences.sms_notifications = data.get('sms_notifications', preferences.sms_notifications)  # preferences.sms_notifications = data.get('sms_notifications', preferences.sms_notifications)
          # blank line
        db.session.commit()  # db.session.commit()
        return jsonify({'success': True})  # return jsonify({'success': True})
  # blank line
  # blank line
# ============================================================================  # # ============================================================================
# DATA EXPORT API  # # DATA EXPORT API
# ============================================================================  # # ============================================================================
  # blank line
@main.route('/api/export/csv')  # @main.route('/api/export/csv')
@login_required  # @login_required
def export_csv():  # def export_csv():
    """Export metrics to CSV."""  # """Export metrics to CSV."""
    server_id = request.args.get('server_id', type=int)  # server_id = request.args.get('server_id', type=int)
    days = request.args.get('days', default=7, type=int)  # days = request.args.get('days', default=7, type=int)
    metric_types = request.args.getlist('metrics') or ['system', 'network']  # metric_types = request.args.getlist('metrics') or ['system', 'network']
      # blank line
    end_date = datetime.now(timezone.utc)  # end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)  # start_date = end_date - timedelta(days=days)
      # blank line
    csv_data = export_metrics_to_csv(server_id, start_date, end_date, metric_types)  # csv_data = export_metrics_to_csv(server_id, start_date, end_date, metric_types)
    return create_export_response(csv_data, 'csv')  # return create_export_response(csv_data, 'csv')
  # blank line
  # blank line
@main.route('/api/export/json')  # @main.route('/api/export/json')
@login_required  # @login_required
def export_json():  # def export_json():
    """Export metrics to JSON."""  # """Export metrics to JSON."""
    server_id = request.args.get('server_id', type=int)  # server_id = request.args.get('server_id', type=int)
    days = request.args.get('days', default=7, type=int)  # days = request.args.get('days', default=7, type=int)
    metric_types = request.args.getlist('metrics') or ['system', 'network']  # metric_types = request.args.getlist('metrics') or ['system', 'network']
      # blank line
    end_date = datetime.now(timezone.utc)  # end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)  # start_date = end_date - timedelta(days=days)
      # blank line
    json_data = export_metrics_to_json(server_id, start_date, end_date, metric_types)  # json_data = export_metrics_to_json(server_id, start_date, end_date, metric_types)
    return create_export_response(json_data, 'json')  # return create_export_response(json_data, 'json')
  # blank line
  # blank line
# ============================================================================  # # ============================================================================
# SERVICE HEALTH CHECK ROUTES  # # SERVICE HEALTH CHECK ROUTES
# ============================================================================  # # ============================================================================
  # blank line
@main.route('/health')  # @main.route('/health')
@login_required  # @login_required
def health_dashboard():  # def health_dashboard():
    """Health check dashboard page."""  # """Health check dashboard page."""
    return render_template('health.html')  # return render_template('health.html')
  # blank line
  # blank line
@main.route('/api/health/services', methods=['GET'])  # @main.route('/api/health/services', methods=['GET'])
@login_required  # @login_required
def get_health_services():  # def get_health_services():
    """Get all registered services with their health status."""  # """Get all registered services with their health status."""
    from app.models import ServiceHealth  # from app.models import ServiceHealth
      # blank line
    services = ServiceHealth.query.all()  # services = ServiceHealth.query.all()
    return jsonify({  # return jsonify({
        'services': [service.to_dict() for service in services]  # 'services': [service.to_dict() for service in services]
    })  # })
  # blank line
  # blank line
@main.route('/api/health/services', methods=['POST'])  # @main.route('/api/health/services', methods=['POST'])
@login_required  # @login_required
def create_health_service():  # def create_health_service():
    """Add a new service to monitor."""  # """Add a new service to monitor."""
    from app.models import ServiceHealth  # from app.models import ServiceHealth
      # blank line
    if not current_user.is_admin:  # if not current_user.is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403  # return jsonify({'error': 'Admin privileges required'}), 403
      # blank line
    data = request.get_json()  # data = request.get_json()
      # blank line
    # Validate required fields  # # Validate required fields
    if not data.get('name') or not data.get('url'):  # if not data.get('name') or not data.get('url'):
        return jsonify({'error': 'Name and URL are required'}), 400  # return jsonify({'error': 'Name and URL are required'}), 400
      # blank line
    service = ServiceHealth(  # service = ServiceHealth(
        name=data['name'],  # name=data['name'],
        url=data['url'],  # url=data['url'],
        description=data.get('description'),  # description=data.get('description'),
        check_interval=data.get('check_interval', 60),  # check_interval=data.get('check_interval', 60),
        timeout=data.get('timeout', 5),  # timeout=data.get('timeout', 5),
        is_active=data.get('is_active', True),  # is_active=data.get('is_active', True),
        created_by=current_user.id  # created_by=current_user.id
    )  # )
      # blank line
    db.session.add(service)  # db.session.add(service)
    db.session.commit()  # db.session.commit()
      # blank line
    return jsonify({  # return jsonify({
        'message': 'Service added successfully',  # 'message': 'Service added successfully',
        'service': service.to_dict()  # 'service': service.to_dict()
    }), 201  # }), 201
  # blank line
  # blank line
@main.route('/api/health/services/<int:service_id>', methods=['PUT'])  # @main.route('/api/health/services/<int:service_id>', methods=['PUT'])
@login_required  # @login_required
def update_health_service(service_id):  # def update_health_service(service_id):
    """Update service configuration."""  # """Update service configuration."""
    from app.models import ServiceHealth  # from app.models import ServiceHealth
      # blank line
    if not current_user.is_admin:  # if not current_user.is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403  # return jsonify({'error': 'Admin privileges required'}), 403
      # blank line
    service = ServiceHealth.query.get_or_404(service_id)  # service = ServiceHealth.query.get_or_404(service_id)
    data = request.get_json()  # data = request.get_json()
      # blank line
    # Update fields  # # Update fields
    if 'name' in data:  # if 'name' in data:
        service.name = data['name']  # service.name = data['name']
    if 'url' in data:  # if 'url' in data:
        service.url = data['url']  # service.url = data['url']
    if 'description' in data:  # if 'description' in data:
        service.description = data['description']  # service.description = data['description']
    if 'check_interval' in data:  # if 'check_interval' in data:
        service.check_interval = data['check_interval']  # service.check_interval = data['check_interval']
    if 'timeout' in data:  # if 'timeout' in data:
        service.timeout = data['timeout']  # service.timeout = data['timeout']
    if 'is_active' in data:  # if 'is_active' in data:
        service.is_active = data['is_active']  # service.is_active = data['is_active']
      # blank line
    service.updated_at = datetime.now(timezone.utc)  # service.updated_at = datetime.now(timezone.utc)
    db.session.commit()  # db.session.commit()
      # blank line
    return jsonify({  # return jsonify({
        'message': 'Service updated successfully',  # 'message': 'Service updated successfully',
        'service': service.to_dict()  # 'service': service.to_dict()
    })  # })
  # blank line
  # blank line
@main.route('/api/health/services/<int:service_id>', methods=['DELETE'])  # @main.route('/api/health/services/<int:service_id>', methods=['DELETE'])
@login_required  # @login_required
def delete_health_service(service_id):  # def delete_health_service(service_id):
    """Remove a service from monitoring."""  # """Remove a service from monitoring."""
    from app.models import ServiceHealth  # from app.models import ServiceHealth
      # blank line
    if not current_user.is_admin:  # if not current_user.is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403  # return jsonify({'error': 'Admin privileges required'}), 403
      # blank line
    service = ServiceHealth.query.get_or_404(service_id)  # service = ServiceHealth.query.get_or_404(service_id)
    db.session.delete(service)  # db.session.delete(service)
    db.session.commit()  # db.session.commit()
      # blank line
    return jsonify({'message': 'Service deleted successfully'})  # return jsonify({'message': 'Service deleted successfully'})
  # blank line
  # blank line
# ============================================================================  # # ============================================================================
# DASHBOARD LAYOUT ROUTES  # # DASHBOARD LAYOUT ROUTES
# ============================================================================  # # ============================================================================
  # blank line
@main.route('/api/dashboard/layout', methods=['GET'])  # @main.route('/api/dashboard/layout', methods=['GET'])
@login_required  # @login_required
def get_dashboard_layout():  # def get_dashboard_layout():
    """Get user's active dashboard layout."""  # """Get user's active dashboard layout."""
    from app.models import DashboardLayout  # from app.models import DashboardLayout
      # blank line
    layout = DashboardLayout.query.filter_by(  # layout = DashboardLayout.query.filter_by(
        user_id=current_user.id,  # user_id=current_user.id,
        is_active=True  # is_active=True
    ).first()  # ).first()
      # blank line
    if layout:  # if layout:
        return jsonify(layout.to_dict())  # return jsonify(layout.to_dict())
    else:  # else:
        # Return default layout  # # Return default layout
        return jsonify({  # return jsonify({
            'layout_config': None,  # 'layout_config': None,
            'message': 'No custom layout found, using default'  # 'message': 'No custom layout found, using default'
        })  # })
  # blank line
  # blank line
@main.route('/api/dashboard/layout', methods=['POST'])  # @main.route('/api/dashboard/layout', methods=['POST'])
@login_required  # @login_required
def save_dashboard_layout():  # def save_dashboard_layout():
    """Save or update user's dashboard layout."""  # """Save or update user's dashboard layout."""
    from app.models import DashboardLayout  # from app.models import DashboardLayout
      # blank line
    data = request.get_json()  # data = request.get_json()
      # blank line
    if not data.get('layout_config'):  # if not data.get('layout_config'):
        return jsonify({'error': 'Layout configuration is required'}), 400  # return jsonify({'error': 'Layout configuration is required'}), 400
      # blank line
    # Deactivate existing layouts  # # Deactivate existing layouts
    DashboardLayout.query.filter_by(  # DashboardLayout.query.filter_by(
        user_id=current_user.id,  # user_id=current_user.id,
        is_active=True  # is_active=True
    ).update({'is_active': False})  # ).update({'is_active': False})
      # blank line
    # Create new layout  # # Create new layout
    layout = DashboardLayout(  # layout = DashboardLayout(
        user_id=current_user.id,  # user_id=current_user.id,
        name=data.get('name', 'Custom Layout'),  # name=data.get('name', 'Custom Layout'),
        layout_config=data['layout_config'],  # layout_config=data['layout_config'],
        is_active=True  # is_active=True
    )  # )
      # blank line
    db.session.add(layout)  # db.session.add(layout)
    db.session.commit()  # db.session.commit()
      # blank line
    return jsonify({  # return jsonify({
        'message': 'Layout saved successfully',  # 'message': 'Layout saved successfully',
        'layout': layout.to_dict()  # 'layout': layout.to_dict()
    }), 201  # }), 201
  # blank line
  # blank line
@main.route('/api/dashboard/layout/<int:layout_id>', methods=['DELETE'])  # @main.route('/api/dashboard/layout/<int:layout_id>', methods=['DELETE'])
@login_required  # @login_required
def delete_dashboard_layout(layout_id):  # def delete_dashboard_layout(layout_id):
    """Delete a dashboard layout."""  # """Delete a dashboard layout."""
    from app.models import DashboardLayout  # from app.models import DashboardLayout
      # blank line
    layout = DashboardLayout.query.get_or_404(layout_id)  # layout = DashboardLayout.query.get_or_404(layout_id)
      # blank line
    # Ensure user owns this layout  # # Ensure user owns this layout
    if layout.user_id != current_user.id:  # if layout.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403  # return jsonify({'error': 'Unauthorized'}), 403
      # blank line
    db.session.delete(layout)  # db.session.delete(layout)
    db.session.commit()  # db.session.commit()
      # blank line
    return jsonify({'message': 'Layout deleted successfully'})  # return jsonify({'message': 'Layout deleted successfully'})
