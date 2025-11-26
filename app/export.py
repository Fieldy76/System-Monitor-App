"""Data export service for CSV and JSON exports."""
import pandas as pd
from flask import Response
from io import StringIO, BytesIO
import json
from datetime import datetime, timedelta, timezone
from app.models import SystemMetric, NetworkMetric, Server


def export_metrics_to_csv(server_id=None, start_date=None, end_date=None, metric_types=None):
    """
    Export system metrics to CSV format.
    
    Args:
        server_id: Server ID to filter by (None = all servers)
        start_date: Start date for filtering (datetime object)
        end_date: End date for filtering (datetime object)
        metric_types: List of metric types to include ['system', 'network']
    
    Returns:
        CSV string
    """
    if metric_types is None:
        metric_types = ['system', 'network']
    
    # Set default date range if not provided
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date - timedelta(days=7)  # Last 7 days by default
    
    dataframes = []
    
    # Export system metrics
    if 'system' in metric_types:
        query = SystemMetric.query.filter(
            SystemMetric.timestamp >= start_date,
            SystemMetric.timestamp <= end_date
        )
        
        if server_id:
            query = query.filter_by(server_id=server_id)
        
        metrics = query.order_by(SystemMetric.timestamp).all()
        
        if metrics:
            data = []
            for m in metrics:
                server = Server.query.get(m.server_id)
                data.append({
                    'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'server': server.name if server else 'Unknown',
                    'cpu_percent': m.cpu_percent,
                    'cpu_freq_mhz': m.cpu_freq,
                    'cpu_temp_c': m.cpu_temp_c,
                    'memory_total_gb': m.memory_total / (1024**3) if m.memory_total else None,
                    'memory_used_gb': m.memory_used / (1024**3) if m.memory_used else None,
                    'memory_percent': m.memory_percent,
                    'disk_total_gb': m.disk_total / (1024**3) if m.disk_total else None,
                    'disk_used_gb': m.disk_used / (1024**3) if m.disk_used else None,
                    'disk_percent': m.disk_percent,
                    'io_read_gb': m.io_read_bytes / (1024**3) if m.io_read_bytes else None,
                    'io_write_gb': m.io_write_bytes / (1024**3) if m.io_write_bytes else None,
                })
            
            df = pd.DataFrame(data)
            dataframes.append(('system_metrics', df))
    
    # Export network metrics
    if 'network' in metric_types:
        query = NetworkMetric.query.filter(
            NetworkMetric.timestamp >= start_date,
            NetworkMetric.timestamp <= end_date
        )
        
        if server_id:
            query = query.filter_by(server_id=server_id)
        
        metrics = query.order_by(NetworkMetric.timestamp).all()
        
        if metrics:
            data = []
            for m in metrics:
                server = Server.query.get(m.server_id)
                data.append({
                    'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'server': server.name if server else 'Unknown',
                    'bytes_sent_gb': m.bytes_sent / (1024**3),
                    'bytes_recv_gb': m.bytes_recv / (1024**3),
                    'packets_sent': m.packets_sent,
                    'packets_recv': m.packets_recv,
                    'connections_established': m.connections_established,
                    'connections_listen': m.connections_listen,
                    'connections_time_wait': m.connections_time_wait,
                })
            
            df = pd.DataFrame(data)
            dataframes.append(('network_metrics', df))
    
    # Combine all dataframes into CSV
    output = StringIO()
    
    for i, (name, df) in enumerate(dataframes):
        if i > 0:
            output.write('\n\n')
        output.write(f'# {name.upper()}\n')
        df.to_csv(output, index=False)
    
    return output.getvalue()


def export_metrics_to_json(server_id=None, start_date=None, end_date=None, metric_types=None):
    """
    Export system metrics to JSON format.
    
    Args:
        server_id: Server ID to filter by (None = all servers)
        start_date: Start date for filtering (datetime object)
        end_date: End date for filtering (datetime object)
        metric_types: List of metric types to include ['system', 'network']
    
    Returns:
        JSON string
    """
    if metric_types is None:
        metric_types = ['system', 'network']
    
    # Set default date range if not provided
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date - timedelta(days=7)  # Last 7 days by default
    
    result = {
        'export_date': datetime.now(timezone.utc).isoformat(),
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'metrics': {}
    }
    
    # Export system metrics
    if 'system' in metric_types:
        query = SystemMetric.query.filter(
            SystemMetric.timestamp >= start_date,
            SystemMetric.timestamp <= end_date
        )
        
        if server_id:
            query = query.filter_by(server_id=server_id)
        
        metrics = query.order_by(SystemMetric.timestamp).all()
        
        system_data = []
        for m in metrics:
            server = Server.query.get(m.server_id)
            system_data.append({
                'timestamp': m.timestamp.isoformat(),
                'server': server.name if server else 'Unknown',
                'server_id': m.server_id,
                'cpu': {
                    'percent': m.cpu_percent,
                    'freq_mhz': m.cpu_freq,
                    'temp_c': m.cpu_temp_c
                },
                'memory': {
                    'total_bytes': m.memory_total,
                    'used_bytes': m.memory_used,
                    'percent': m.memory_percent
                },
                'disk': {
                    'total_bytes': m.disk_total,
                    'used_bytes': m.disk_used,
                    'percent': m.disk_percent
                },
                'io': {
                    'read_bytes': m.io_read_bytes,
                    'write_bytes': m.io_write_bytes,
                    'read_count': m.io_read_count,
                    'write_count': m.io_write_count
                }
            })
        
        result['metrics']['system'] = system_data
    
    # Export network metrics
    if 'network' in metric_types:
        query = NetworkMetric.query.filter(
            NetworkMetric.timestamp >= start_date,
            NetworkMetric.timestamp <= end_date
        )
        
        if server_id:
            query = query.filter_by(server_id=server_id)
        
        metrics = query.order_by(NetworkMetric.timestamp).all()
        
        network_data = []
        for m in metrics:
            server = Server.query.get(m.server_id)
            network_data.append({
                'timestamp': m.timestamp.isoformat(),
                'server': server.name if server else 'Unknown',
                'server_id': m.server_id,
                'bytes_sent': m.bytes_sent,
                'bytes_recv': m.bytes_recv,
                'packets_sent': m.packets_sent,
                'packets_recv': m.packets_recv,
                'connections': {
                    'established': m.connections_established,
                    'listen': m.connections_listen,
                    'time_wait': m.connections_time_wait
                }
            })
        
        result['metrics']['network'] = network_data
    
    return json.dumps(result, indent=2)


def create_export_response(data, format_type, filename_prefix='system_monitor_export'):
    """
    Create a Flask Response object for file download.
    
    Args:
        data: Export data (string)
        format_type: 'csv' or 'json'
        filename_prefix: Prefix for the filename
    
    Returns:
        Flask Response object
    """
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    filename = f"{filename_prefix}_{timestamp}.{format_type}"
    
    if format_type == 'csv':
        mimetype = 'text/csv'
    elif format_type == 'json':
        mimetype = 'application/json'
    else:
        mimetype = 'text/plain'
    
    return Response(
        data,
        mimetype=mimetype,
        headers={
            'Content-Disposition': f'attachment; filename={filename}'
        }
    )
