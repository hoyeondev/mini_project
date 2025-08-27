from flask import Flask, render_template_string
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime, timedelta
import re

app = Flask(__name__)

# 한글 폰트 설정 (시스템에 맞게 조정)
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'AppleGothic', 'Malgun Gothic']
plt.rcParams['axes.unicode_minus'] = False

def parse_defect_data(file_path):
    """defect_log.txt 파일을 파싱하여 DataFrame으로 반환"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        data = []
        for line in lines:
            line = line.strip()
            if line:
                # 날짜, 결함 타입(확률) 형식 파싱
                match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\s*([^(]+)\(([^)]+)\)', line)
                if match:
                    timestamp = match.group(1)
                    defect_type = match.group(2).strip()
                    confidence = float(match.group(3))
                    data.append({
                        'timestamp': pd.to_datetime(timestamp),
                        'defect_type': defect_type,
                        'confidence': confidence
                    })
        
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error parsing file: {e}")
        return pd.DataFrame()

def create_daily_chart(df):
    """일별 결함 발생 차트 생성"""
    plt.figure(figsize=(12, 6))
    
    # 일별 결함 타입별 집계
    daily_defects = df.groupby([df['timestamp'].dt.date, 'defect_type']).size().unstack(fill_value=0)
    
    # 스택 바 차트
    ax = daily_defects.plot(kind='bar', stacked=True, figsize=(12, 6), colormap='Set3')
    plt.title('Daily Defects by Type (Last 7 Days)', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Number of Defects', fontsize=12)
    plt.legend(title='Defect Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 이미지를 base64로 인코딩
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

def create_defect_type_pie_chart(df):
    """결함 타입별 파이 차트 생성"""
    plt.figure(figsize=(8, 8))
    
    defect_counts = df['defect_type'].value_counts()
    colors = plt.cm.Set3(range(len(defect_counts)))
    
    plt.pie(defect_counts.values, labels=defect_counts.index, autopct='%1.1f%%', 
            colors=colors, startangle=90)
    plt.title('Defect Distribution by Type (Last 7 Days)', fontsize=16, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

@app.route("/")
@app.route("/log")
# @app.route("/dashboard")
def dashboard():
    try:
        # 데이터 로드 및 파싱
        df = parse_defect_data("defect_log.txt")
        
        if df.empty:
            return render_error("No data found or error parsing defect_log.txt")
        
        # 최근 7일 데이터 필터링
        today = datetime.now()
        seven_days_ago = today - timedelta(days=7)
        df_recent = df[df['timestamp'] >= seven_days_ago].copy()
        
        if df_recent.empty:
            return render_error("No data found for the last 7 days")
        
        # 통계 계산
        total_defects = len(df_recent)
        today_defects = len(df_recent[df_recent['timestamp'].dt.date == today.date()])
        defect_types = df_recent['defect_type'].nunique()
        avg_confidence = df_recent['confidence'].mean()
        
        # 차트 생성
        daily_chart = create_daily_chart(df_recent)
        pie_chart = create_defect_type_pie_chart(df_recent)
        
        # 최근 결함 목록 (최대 10개)
        recent_defects = df_recent.sort_values('timestamp', ascending=False).head(10)
        
        # 결함 타입별 통계
        defect_stats = df_recent.groupby('defect_type').agg({
            'confidence': ['count', 'mean']
        }).round(3)
        defect_stats.columns = ['Count', 'Avg Confidence']
        defect_stats = defect_stats.reset_index()
        
        html_template = """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Defect Detection Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                .dashboard-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 2rem 0;
                    margin-bottom: 2rem;
                }
                .stat-card {
                    transition: transform 0.2s;
                }
                .stat-card:hover {
                    transform: translateY(-5px);
                }
                .chart-container {
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                }
                .table-container {
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    padding: 1.5rem;
                }
                body {
                    background-color: #f8f9fa;
                }
            </style>
        </head>
        <body>
            <!-- Header -->
            <div class="dashboard-header">
                <div class="container">
                    <div class="row align-items-center">
                        <div class="col-md-6">
                            <h1><i class="fas fa-chart-line me-3"></i>Defect Detection Dashboard</h1>
                            <p class="mb-0">Real-time quality monitoring system</p>
                        </div>
                        <div class="col-md-6 text-md-end">
                            <h4><i class="fas fa-calendar-alt me-2"></i>{{ today_date }}</h4>
                            <small>Last 7 days analysis</small>
                        </div>
                    </div>
                </div>
            </div>

            <div class="container-fluid">
                <!-- Statistics Cards -->
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="card stat-card border-0 shadow-sm">
                            <div class="card-body text-center">
                                <div class="text-primary mb-2">
                                    <i class="fas fa-exclamation-triangle fa-3x"></i>
                                </div>
                                <h3 class="text-primary">{{ total_defects }}</h3>
                                <p class="text-muted mb-0">Total Defects (7 days)</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card border-0 shadow-sm">
                            <div class="card-body text-center">
                                <div class="text-warning mb-2">
                                    <i class="fas fa-clock fa-3x"></i>
                                </div>
                                <h3 class="text-warning">{{ today_defects }}</h3>
                                <p class="text-muted mb-0">Today's Defects</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card border-0 shadow-sm">
                            <div class="card-body text-center">
                                <div class="text-info mb-2">
                                    <i class="fas fa-tags fa-3x"></i>
                                </div>
                                <h3 class="text-info">{{ defect_types }}</h3>
                                <p class="text-muted mb-0">Defect Types</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card border-0 shadow-sm">
                            <div class="card-body text-center">
                                <div class="text-success mb-2">
                                    <i class="fas fa-percentage fa-3x"></i>
                                </div>
                                <h3 class="text-success">{{ avg_confidence }}%</h3>
                                <p class="text-muted mb-0">Avg Confidence</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Charts Row -->
                <div class="row">
                    <div class="col-lg-8">
                        <div class="chart-container">
                            <h4 class="mb-3"><i class="fas fa-chart-bar me-2"></i>Daily Defects Trend</h4>
                            <img src="data:image/png;base64,{{ daily_chart }}" class="img-fluid" alt="Daily Defects Chart">
                        </div>
                    </div>
                    <div class="col-lg-4">
                        <div class="chart-container">
                            <h4 class="mb-3"><i class="fas fa-chart-pie me-2"></i>Defect Distribution</h4>
                            <img src="data:image/png;base64,{{ pie_chart }}" class="img-fluid" alt="Defect Distribution">
                        </div>
                    </div>
                </div>

                <!-- Tables Row -->
                <div class="row">
                    <div class="col-lg-6">
                        <div class="table-container">
                            <h4 class="mb-3"><i class="fas fa-list me-2"></i>Recent Defects</h4>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>Time</th>
                                            <th>Type</th>
                                            <th>Confidence</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for _, row in recent_defects.iterrows() %}
                                        <tr>
                                            <td>{{ row.timestamp.strftime('%m-%d %H:%M') }}</td>
                                            <td><span class="badge bg-warning">{{ row.defect_type }}</span></td>
                                            <td>{{ "%.2f"|format(row.confidence) }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-6">
                        <div class="table-container">
                            <h4 class="mb-3"><i class="fas fa-chart-bar me-2"></i>Defect Statistics</h4>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>Defect Type</th>
                                            <th>Count</th>
                                            <th>Avg Confidence</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for _, row in defect_stats.iterrows() %}
                                        <tr>
                                            <td><span class="badge bg-primary">{{ row.defect_type }}</span></td>
                                            <td>{{ row.Count }}</td>
                                            <td>{{ "%.3f"|format(row['Avg Confidence']) }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <footer class="text-center py-4 mt-5">
                <div class="container">
                    <small class="text-muted">
                        <i class="fas fa-sync-alt me-1"></i>
                        Last updated: {{ today_date }} | 
                        <i class="fas fa-database me-1"></i>
                        Data source: defect_log.txt
                    </small>
                </div>
            </footer>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """
        
        return render_template_string(html_template,
                                    today_date=today.strftime('%Y-%m-%d %H:%M'),
                                    total_defects=total_defects,
                                    today_defects=today_defects,
                                    defect_types=defect_types,
                                    avg_confidence=round(avg_confidence * 100, 1),
                                    daily_chart=daily_chart,
                                    pie_chart=pie_chart,
                                    recent_defects=recent_defects,
                                    defect_stats=defect_stats)
        
    except Exception as e:
        return render_error(f"Dashboard error: {str(e)}")

def render_error(message):
    """에러 페이지 렌더링"""
    error_template = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Error</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="alert alert-danger text-center">
                        <h4>Dashboard Error</h4>
                        <p>{{ error_message }}</p>
                        <hr>
                        <small>Please check your defect_log.txt file and try again.</small>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(error_template, error_message=message)

if __name__ == "__main__":
    app.run(port=5000, debug=True)