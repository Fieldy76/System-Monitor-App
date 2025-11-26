"""Data export service for CSV and JSON exports."""  # """Data export service for CSV and JSON exports."""
import pandas as pd  # import pandas as pd
from flask import Response  # from flask import Response
from io import StringIO, BytesIO  # from io import StringIO, BytesIO
import json  # import json
from datetime import datetime, timedelta, timezone  # from datetime import datetime, timedelta, timezone
from app.models import SystemMetric, NetworkMetric, Server  # from app.models import SystemMetric, NetworkMetric, Server
  # blank line
  # blank line
def export_metrics_to_csv(server_id=None, start_date=None, end_date=None, metric_types=None):  # def export_metrics_to_csv(server_id=None, start_date=None, end_date=None, metric_types=None):
    """  # """
    Export system metrics to CSV format.  # Export system metrics to CSV format.
      # blank line
    Args:  # Args:
        server_id: Server ID to filter by (None = all servers)  # server_id: Server ID to filter by (None = all servers)
        start_date: Start date for filtering (datetime object)  # start_date: Start date for filtering (datetime object)
        end_date: End date for filtering (datetime object)  # end_date: End date for filtering (datetime object)
        metric_types: List of metric types to include ['system', 'network']  # metric_types: List of metric types to include ['system', 'network']
      # blank line
    Returns:  # Returns:
        CSV string  # CSV string
    """  # """
    if metric_types is None:  # if metric_types is None:
        metric_types = ['system', 'network']  # metric_types = ['system', 'network']
      # blank line
    # Set default date range if not provided  # # Set default date range if not provided
    if not end_date:  # if not end_date:
        end_date = datetime.now(timezone.utc)  # end_date = datetime.now(timezone.utc)
    if not start_date:  # if not start_date:
        start_date = end_date - timedelta(days=7)  # Last 7 days by default  # start_date = end_date - timedelta(days=7)  # Last 7 days by default
      # blank line
    dataframes = []  # dataframes = []
      # blank line
    # Export system metrics  # # Export system metrics
    if 'system' in metric_types:  # if 'system' in metric_types:
        query = SystemMetric.query.filter(  # query = SystemMetric.query.filter(
            SystemMetric.timestamp >= start_date,  # SystemMetric.timestamp >= start_date,
            SystemMetric.timestamp <= end_date  # SystemMetric.timestamp <= end_date
        )  # )
          # blank line
        if server_id:  # if server_id:
            query = query.filter_by(server_id=server_id)  # query = query.filter_by(server_id=server_id)
          # blank line
        metrics = query.order_by(SystemMetric.timestamp).all()  # metrics = query.order_by(SystemMetric.timestamp).all()
          # blank line
        if metrics:  # if metrics:
            data = []  # data = []
            for m in metrics:  # for m in metrics:
                server = Server.query.get(m.server_id)  # server = Server.query.get(m.server_id)
                data.append({  # data.append({
                    'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),  # 'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'server': server.name if server else 'Unknown',  # 'server': server.name if server else 'Unknown',
                    'cpu_percent': m.cpu_percent,  # 'cpu_percent': m.cpu_percent,
                    'cpu_freq_mhz': m.cpu_freq,  # 'cpu_freq_mhz': m.cpu_freq,
                    'cpu_temp_c': m.cpu_temp_c,  # 'cpu_temp_c': m.cpu_temp_c,
                    'memory_total_gb': m.memory_total / (1024**3) if m.memory_total else None,  # 'memory_total_gb': m.memory_total / (1024**3) if m.memory_total else None,
                    'memory_used_gb': m.memory_used / (1024**3) if m.memory_used else None,  # 'memory_used_gb': m.memory_used / (1024**3) if m.memory_used else None,
                    'memory_percent': m.memory_percent,  # 'memory_percent': m.memory_percent,
                    'disk_total_gb': m.disk_total / (1024**3) if m.disk_total else None,  # 'disk_total_gb': m.disk_total / (1024**3) if m.disk_total else None,
                    'disk_used_gb': m.disk_used / (1024**3) if m.disk_used else None,  # 'disk_used_gb': m.disk_used / (1024**3) if m.disk_used else None,
                    'disk_percent': m.disk_percent,  # 'disk_percent': m.disk_percent,
                    'io_read_gb': m.io_read_bytes / (1024**3) if m.io_read_bytes else None,  # 'io_read_gb': m.io_read_bytes / (1024**3) if m.io_read_bytes else None,
                    'io_write_gb': m.io_write_bytes / (1024**3) if m.io_write_bytes else None,  # 'io_write_gb': m.io_write_bytes / (1024**3) if m.io_write_bytes else None,
                })  # })
              # blank line
            df = pd.DataFrame(data)  # df = pd.DataFrame(data)
            dataframes.append(('system_metrics', df))  # dataframes.append(('system_metrics', df))
      # blank line
    # Export network metrics  # # Export network metrics
    if 'network' in metric_types:  # if 'network' in metric_types:
        query = NetworkMetric.query.filter(  # query = NetworkMetric.query.filter(
            NetworkMetric.timestamp >= start_date,  # NetworkMetric.timestamp >= start_date,
            NetworkMetric.timestamp <= end_date  # NetworkMetric.timestamp <= end_date
        )  # )
          # blank line
        if server_id:  # if server_id:
            query = query.filter_by(server_id=server_id)  # query = query.filter_by(server_id=server_id)
          # blank line
        metrics = query.order_by(NetworkMetric.timestamp).all()  # metrics = query.order_by(NetworkMetric.timestamp).all()
          # blank line
        if metrics:  # if metrics:
            data = []  # data = []
            for m in metrics:  # for m in metrics:
                server = Server.query.get(m.server_id)  # server = Server.query.get(m.server_id)
                data.append({  # data.append({
                    'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),  # 'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'server': server.name if server else 'Unknown',  # 'server': server.name if server else 'Unknown',
                    'bytes_sent_gb': m.bytes_sent / (1024**3),  # 'bytes_sent_gb': m.bytes_sent / (1024**3),
                    'bytes_recv_gb': m.bytes_recv / (1024**3),  # 'bytes_recv_gb': m.bytes_recv / (1024**3),
                    'packets_sent': m.packets_sent,  # 'packets_sent': m.packets_sent,
                    'packets_recv': m.packets_recv,  # 'packets_recv': m.packets_recv,
                    'connections_established': m.connections_established,  # 'connections_established': m.connections_established,
                    'connections_listen': m.connections_listen,  # 'connections_listen': m.connections_listen,
                    'connections_time_wait': m.connections_time_wait,  # 'connections_time_wait': m.connections_time_wait,
                })  # })
              # blank line
            df = pd.DataFrame(data)  # df = pd.DataFrame(data)
            dataframes.append(('network_metrics', df))  # dataframes.append(('network_metrics', df))
      # blank line
    # Combine all dataframes into CSV  # # Combine all dataframes into CSV
    output = StringIO()  # output = StringIO()
      # blank line
    for i, (name, df) in enumerate(dataframes):  # for i, (name, df) in enumerate(dataframes):
        if i > 0:  # if i > 0:
            output.write('\n\n')  # output.write('\n\n')
        output.write(f'# {name.upper()}\n')  # output.write(f'# {name.upper()}\n')
        df.to_csv(output, index=False)  # df.to_csv(output, index=False)
      # blank line
    return output.getvalue()  # return output.getvalue()
  # blank line
  # blank line
def export_metrics_to_json(server_id=None, start_date=None, end_date=None, metric_types=None):  # def export_metrics_to_json(server_id=None, start_date=None, end_date=None, metric_types=None):
    """  # """
    Export system metrics to JSON format.  # Export system metrics to JSON format.
      # blank line
    Args:  # Args:
        server_id: Server ID to filter by (None = all servers)  # server_id: Server ID to filter by (None = all servers)
        start_date: Start date for filtering (datetime object)  # start_date: Start date for filtering (datetime object)
        end_date: End date for filtering (datetime object)  # end_date: End date for filtering (datetime object)
        metric_types: List of metric types to include ['system', 'network']  # metric_types: List of metric types to include ['system', 'network']
      # blank line
    Returns:  # Returns:
        JSON string  # JSON string
    """  # """
    if metric_types is None:  # if metric_types is None:
        metric_types = ['system', 'network']  # metric_types = ['system', 'network']
      # blank line
    # Set default date range if not provided  # # Set default date range if not provided
    if not end_date:  # if not end_date:
        end_date = datetime.now(timezone.utc)  # end_date = datetime.now(timezone.utc)
    if not start_date:  # if not start_date:
        start_date = end_date - timedelta(days=7)  # Last 7 days by default  # start_date = end_date - timedelta(days=7)  # Last 7 days by default
      # blank line
    result = {  # result = {
        'export_date': datetime.now(timezone.utc).isoformat(),  # 'export_date': datetime.now(timezone.utc).isoformat(),
        'start_date': start_date.isoformat(),  # 'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),  # 'end_date': end_date.isoformat(),
        'metrics': {}  # 'metrics': {}
    }  # }
      # blank line
    # Export system metrics  # # Export system metrics
    if 'system' in metric_types:  # if 'system' in metric_types:
        query = SystemMetric.query.filter(  # query = SystemMetric.query.filter(
            SystemMetric.timestamp >= start_date,  # SystemMetric.timestamp >= start_date,
            SystemMetric.timestamp <= end_date  # SystemMetric.timestamp <= end_date
        )  # )
          # blank line
        if server_id:  # if server_id:
            query = query.filter_by(server_id=server_id)  # query = query.filter_by(server_id=server_id)
          # blank line
        metrics = query.order_by(SystemMetric.timestamp).all()  # metrics = query.order_by(SystemMetric.timestamp).all()
          # blank line
        system_data = []  # system_data = []
        for m in metrics:  # for m in metrics:
            server = Server.query.get(m.server_id)  # server = Server.query.get(m.server_id)
            system_data.append({  # system_data.append({
                'timestamp': m.timestamp.isoformat(),  # 'timestamp': m.timestamp.isoformat(),
                'server': server.name if server else 'Unknown',  # 'server': server.name if server else 'Unknown',
                'server_id': m.server_id,  # 'server_id': m.server_id,
                'cpu': {  # 'cpu': {
                    'percent': m.cpu_percent,  # 'percent': m.cpu_percent,
                    'freq_mhz': m.cpu_freq,  # 'freq_mhz': m.cpu_freq,
                    'temp_c': m.cpu_temp_c  # 'temp_c': m.cpu_temp_c
                },  # },
                'memory': {  # 'memory': {
                    'total_bytes': m.memory_total,  # 'total_bytes': m.memory_total,
                    'used_bytes': m.memory_used,  # 'used_bytes': m.memory_used,
                    'percent': m.memory_percent  # 'percent': m.memory_percent
                },  # },
                'disk': {  # 'disk': {
                    'total_bytes': m.disk_total,  # 'total_bytes': m.disk_total,
                    'used_bytes': m.disk_used,  # 'used_bytes': m.disk_used,
                    'percent': m.disk_percent  # 'percent': m.disk_percent
                },  # },
                'io': {  # 'io': {
                    'read_bytes': m.io_read_bytes,  # 'read_bytes': m.io_read_bytes,
                    'write_bytes': m.io_write_bytes,  # 'write_bytes': m.io_write_bytes,
                    'read_count': m.io_read_count,  # 'read_count': m.io_read_count,
                    'write_count': m.io_write_count  # 'write_count': m.io_write_count
                }  # }
            })  # })
          # blank line
        result['metrics']['system'] = system_data  # result['metrics']['system'] = system_data
      # blank line
    # Export network metrics  # # Export network metrics
    if 'network' in metric_types:  # if 'network' in metric_types:
        query = NetworkMetric.query.filter(  # query = NetworkMetric.query.filter(
            NetworkMetric.timestamp >= start_date,  # NetworkMetric.timestamp >= start_date,
            NetworkMetric.timestamp <= end_date  # NetworkMetric.timestamp <= end_date
        )  # )
          # blank line
        if server_id:  # if server_id:
            query = query.filter_by(server_id=server_id)  # query = query.filter_by(server_id=server_id)
          # blank line
        metrics = query.order_by(NetworkMetric.timestamp).all()  # metrics = query.order_by(NetworkMetric.timestamp).all()
          # blank line
        network_data = []  # network_data = []
        for m in metrics:  # for m in metrics:
            server = Server.query.get(m.server_id)  # server = Server.query.get(m.server_id)
            network_data.append({  # network_data.append({
                'timestamp': m.timestamp.isoformat(),  # 'timestamp': m.timestamp.isoformat(),
                'server': server.name if server else 'Unknown',  # 'server': server.name if server else 'Unknown',
                'server_id': m.server_id,  # 'server_id': m.server_id,
                'bytes_sent': m.bytes_sent,  # 'bytes_sent': m.bytes_sent,
                'bytes_recv': m.bytes_recv,  # 'bytes_recv': m.bytes_recv,
                'packets_sent': m.packets_sent,  # 'packets_sent': m.packets_sent,
                'packets_recv': m.packets_recv,  # 'packets_recv': m.packets_recv,
                'connections': {  # 'connections': {
                    'established': m.connections_established,  # 'established': m.connections_established,
                    'listen': m.connections_listen,  # 'listen': m.connections_listen,
                    'time_wait': m.connections_time_wait  # 'time_wait': m.connections_time_wait
                }  # }
            })  # })
          # blank line
        result['metrics']['network'] = network_data  # result['metrics']['network'] = network_data
      # blank line
    return json.dumps(result, indent=2)  # return json.dumps(result, indent=2)
  # blank line
  # blank line
def create_export_response(data, format_type, filename_prefix='system_monitor_export'):  # def create_export_response(data, format_type, filename_prefix='system_monitor_export'):
    """  # """
    Create a Flask Response object for file download.  # Create a Flask Response object for file download.
      # blank line
    Args:  # Args:
        data: Export data (string)  # data: Export data (string)
        format_type: 'csv' or 'json'  # format_type: 'csv' or 'json'
        filename_prefix: Prefix for the filename  # filename_prefix: Prefix for the filename
      # blank line
    Returns:  # Returns:
        Flask Response object  # Flask Response object
    """  # """
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')  # timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    filename = f"{filename_prefix}_{timestamp}.{format_type}"  # filename = f"{filename_prefix}_{timestamp}.{format_type}"
      # blank line
    if format_type == 'csv':  # if format_type == 'csv':
        mimetype = 'text/csv'  # mimetype = 'text/csv'
    elif format_type == 'json':  # elif format_type == 'json':
        mimetype = 'application/json'  # mimetype = 'application/json'
    else:  # else:
        mimetype = 'text/plain'  # mimetype = 'text/plain'
      # blank line
    return Response(  # return Response(
        data,  # data,
        mimetype=mimetype,  # mimetype=mimetype,
        headers={  # headers={
            'Content-Disposition': f'attachment; filename={filename}'  # 'Content-Disposition': f'attachment; filename={filename}'
        }  # }
    )  # )
