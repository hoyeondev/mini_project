from flask import Flask, render_template_string
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime, timedelta
import re

app = Flask(__name__)

# 폰트 설정
plt.rcParams['font.family'] = ['sans-serif', 'Malgun Gothic']
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
    plt.title('일자별 불량 차트(최근 7일)', fontsize=16, fontweight='bold')
    plt.xlabel('일자', fontsize=12)
    plt.ylabel('불량 수', fontsize=12)
    plt.legend(title='불량 유형', bbox_to_anchor=(1.05, 1), loc='upper left')
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
    plt.title('불량 유형별 통계 (최근 7일)', fontsize=16, fontweight='bold')
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
            return render_error("최근 7일간의 데이터가 없습니다.")
        
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
        
        # HTML 템플릿 파일 읽기
        def load_template():
            try:
                with open('dashboard_template.html', 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                return """
                <div class="alert alert-danger">
                    <h4>Template Error</h4>
                    <p>dashboard_template.html 파일을 찾을 수 없습니다.</p>
                </div>
                """
        
        html_template = load_template()
        
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