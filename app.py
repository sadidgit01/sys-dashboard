from flask import Flask, render_template, Response
import psutil
import time
import json
from datetime import datetime

app = Flask(__name__)

# Store last 50 data points
metrics_history = {
    'timestamps': [],
    'cpu': [],
    'memory': [],
    'disk': []
}

def get_system_metrics():
    """Collect system metrics"""
    # CPU usage (percent)
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Memory usage (percent)
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    # Disk usage (percent) - using root partition
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    
    return {
        'cpu': cpu_percent,
        'memory': memory_percent,
        'disk': disk_percent,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }

def generate_metrics():
    """Generate metrics and maintain history"""
    while True:
        metrics = get_system_metrics()
        
        # Update history (keep last 50 points)
        for key in ['cpu', 'memory', 'disk']:
            metrics_history[key].append(metrics[key])
            if len(metrics_history[key]) > 50:
                metrics_history[key].pop(0)
        
        metrics_history['timestamps'].append(metrics['timestamp'])
        if len(metrics_history['timestamps']) > 50:
            metrics_history['timestamps'].pop(0)
        
        # Format data for SSE
        data = {
            'timestamps': metrics_history['timestamps'],
            'cpu': metrics_history['cpu'],
            'memory': metrics_history['memory'],
            'disk': metrics_history['disk']
        }
        
        yield f"data: {json.dumps(data)}\n\n"
        time.sleep(1)  # Update interval

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/metrics')
def metrics():
    return Response(generate_metrics(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)